from scipy.optimize import minimize, dual_annealing
import numpy as np
from volstreet import logger, OptimizationError


def generate_constraints(
    deltas: np.ndarray,
    gammas: np.ndarray,
    max_delta: float,
    min_delta: float,
    min_gamma: float,
    max_gamma: float,
    full: bool,
):
    """For now it uses a delta range to enforce the constraint. But I should use an equality constraint to enforce
    the target delta. Presently I frequently get unsuccessful optimization results when I use equality constraints.
    """
    constraints = [
        {"type": "eq", "fun": lambda x: sum(x)},
        {"type": "ineq", "fun": lambda x: -np.dot(x, deltas) - min_delta},
        {"type": "ineq", "fun": lambda x: np.dot(x, deltas) + max_delta},
        {"type": "ineq", "fun": lambda x: -np.dot(x, gammas) - min_gamma},
        {"type": "ineq", "fun": lambda x: np.dot(x, gammas) + max_gamma},
        {"type": "ineq", "fun": lambda x: 2 - sum(abs(x))},
        {"type": "ineq", "fun": lambda x: sum(abs(x)) - 1.99},
        # {"type": "ineq", "fun": lambda x: min(abs(x)) - 0.01}, commented out and using recursive optimization in practice
    ]
    return constraints if full else constraints[-1]


def generate_x0_and_bounds(n: int):
    x0 = np.zeros(n)
    bounds = [(-1, 1) for _ in range(n)]
    return x0, bounds


def calculate_penalty(deviation: float, weight: float = 1000):
    return (weight ** abs(deviation)) - 1


def normalize_array(arr):
    min_val = np.min(arr)
    max_val = np.max(arr)
    return (arr - min_val) / (max_val - min_val)


def scale_back_to_original(arr, original_arr):
    min_val = np.min(original_arr)
    max_val = np.max(original_arr)
    return arr * (max_val - min_val) + min_val


def basic_objective(x, deltas, gammas):
    # Objective: maximize delta minus gamma
    total_delta = np.dot(x, deltas)
    total_gamma = np.dot(x, gammas)
    return total_delta - total_gamma


def penalty_objective(
    x,
    deltas,
    gammas,
    target_delta,
    normalized=False,
    gamma_weight=10,
    original_deltas=None,
):
    # Objective: maximize delta minus gamma
    total_delta = np.dot(x, deltas)
    total_gamma = np.dot(x, gammas)

    # Penalty functions
    penalty = 0

    # Complete hedge penalty
    diff_from_zero = abs(sum(x))
    penalty += calculate_penalty(diff_from_zero)

    # Delta penalty
    _total_delta = np.dot(x, original_deltas) if normalized else total_delta
    diff_from_target = -_total_delta - target_delta
    penalty += calculate_penalty(diff_from_target)

    # Total quantity penalty
    diff_from_two = sum(abs(x)) - 2
    penalty += calculate_penalty(diff_from_two)

    return total_delta - (gamma_weight * total_gamma) + penalty


def optimize_leg_v1(
    deltas: np.ndarray,
    gammas: np.ndarray,
    min_delta: float,
    max_delta: float,
    gamma_scaler: float = 1.0,
    min_gamma: float = -100000,
    max_gamma: float = 100000,
):
    """
    The first version of the optimization algorithm. It uses the basic objective function which simply minimizes
    delta - gamma. It uses all the constraints (hedged position, delta range, total position size, and minimum
    position size). It finds the optimal solution using the SLSQP algorithm. It most likely will not find the
    global minimum.
    """

    deltas = abs(deltas)
    gammas = gammas * gamma_scaler
    min_gamma = min_gamma * gamma_scaler
    max_gamma = max_gamma * gamma_scaler

    def objective(x):
        return basic_objective(x, deltas, gammas)

    # Constraints: total quantity is 1 and total delta equals target delta
    constraints = generate_constraints(
        deltas, gammas, max_delta, min_delta, min_gamma, max_gamma, full=True
    )

    x0, bounds = generate_x0_and_bounds(len(deltas))

    result = minimize(
        objective,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000},
    )
    return result


def optimize_leg_v2(
    deltas: np.ndarray,
    gammas: np.ndarray,
    target_delta: float,
):
    """ "Using normalized values"""
    deltas = abs(deltas)

    normalized_deltas = normalize_array(deltas)
    normalized_gammas = normalize_array(gammas)

    def objective(x):
        return penalty_objective(
            x,
            normalized_deltas,
            normalized_gammas,
            target_delta,
            normalized=True,
            gamma_weight=1,
            original_deltas=deltas,
        )

    constraints = generate_constraints(
        deltas, gammas, target_delta, 0.05, -np.inf, np.inf, full=False
    )

    x0, bounds = generate_x0_and_bounds(len(deltas))

    result = minimize(
        objective,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000},
    )
    return result


def optimize_leg_global(
    deltas: np.ndarray,
    gammas: np.ndarray,
    target_delta: float,
):
    """
    Designed to be used with the global optimization algorithm. Since constraints are not supported,
    we will use a penalty function to enforce the constraints. The major constaints are that the total
    quantity should be 0 (complete hedge) and the delta should be very very close to the target delta.
    Lastly, the absolute total quantity should be less than very very close to 2.
    """
    deltas = abs(deltas)

    normalized_deltas = normalize_array(deltas)
    normalized_gammas = normalize_array(gammas)

    def objective(x):
        return penalty_objective(
            x,
            normalized_deltas,
            normalized_gammas,
            target_delta,
            normalized=True,
            gamma_weight=1,
            original_deltas=deltas,
        )

    x0, bounds = generate_x0_and_bounds(len(deltas))

    result = dual_annealing(
        objective,
        bounds=bounds,
        x0=x0,
        maxiter=15000,
        seed=42,
    )
    return result


def get_time_value_of_options_frame(
    greeks: np.ndarray, implied_spot: float, is_call: bool
) -> np.ndarray:
    spot_array = np.array([implied_spot] * len(greeks))
    greeks = np.column_stack((spot_array, greeks))
    intrinsic_value = _get_intrinsic_value(greeks, is_call)
    time_value = greeks[:, 2] - intrinsic_value  # LTP - Intrinsic value
    return time_value


def _get_intrinsic_value(greeks: np.ndarray, is_call: bool) -> np.ndarray:
    if is_call:
        intrinsic_value = np.where(
            greeks[:, 0] - greeks[:, 1] <= 0, 0, greeks[:, 0] - greeks[:, 1]
        )
    else:
        intrinsic_value = np.where(
            greeks[:, 1] - greeks[:, 0] >= 0, greeks[:, 1] - greeks[:, 0], 0
        )
    return intrinsic_value


def filter_greeks_frame(
    greeks: np.ndarray, delta_threshold: float, implied_spot: float, is_call: bool
) -> np.ndarray:
    if is_call:
        mask = (greeks[:, 2] < delta_threshold) & (greeks[:, 2] > 0.01)
    else:
        mask = (greeks[:, 2] > -delta_threshold) & (greeks[:, 2] < -0.01)

    greeks_fil = greeks[mask]
    time_values = get_time_value_of_options_frame(greeks_fil, implied_spot, is_call)
    diffs = np.diff(time_values)
    target_index = np.argmin(np.sign(diffs))
    greeks_fil = greeks_fil[target_index:]

    return greeks_fil


def optimize_option_weights(
    deltas: np.ndarray,
    gammas: np.ndarray,
    min_delta: float,
    max_delta: float,
    min_gamma: float = -100000,
    max_gamma: float = 100000,
    gamma_scaler: float = 80,
) -> np.ndarray:
    """
    At every call, the indices should be the length of the deltas and gammas array.
    """

    if gamma_scaler == 1:  # Base return condition
        logger.error("Gamma scaler has reached 1. Unable to calibrate portfolio.")
        raise OptimizationError("Unable to calibrate portfolio.")

    try:
        result = optimize_leg_v1(
            deltas, gammas, min_delta, max_delta, gamma_scaler, min_gamma, max_gamma
        )
    except Exception as e:
        logger.error(
            f"Optimization failed with exception: {e}\n" f"Arguments: {locals()}\n"
        )
        raise OptimizationError(f"Optimization failed with exception: {e}")

    if not result.success:
        ms = (
            f"Optimization failed with message: {result.message}\n"
            f"Arguments: {locals()}\n"
            f"Retrying optimization with a different gamma scaler."
        )

        logger.error(ms)
        new_scaler = gamma_scaler - 40
        new_scaler = max(new_scaler, 1)
        return optimize_option_weights(
            deltas,
            gammas,
            min_delta,
            max_delta,
            min_gamma,
            max_gamma,
            new_scaler,
        )

    weights = result.x
    weights = np.array([round(x, 2) for x in weights])
    total_gamma = np.dot(gammas, weights)
    total_delta = np.dot(deltas, weights)
    logger.info(
        f"Calculated weights: {weights}\nTotal Delta: {total_delta}\nTotal Gamma: {total_gamma}"
    )

    return weights
