import numpy as np
from attrs import define, field, validators
from datetime import datetime, timedelta, time
from time import sleep
from itertools import product
import inspect
import traceback
from typing import Callable
from volstreet import config
from volstreet.exceptions import OptimizationError
from volstreet.config import logger
from volstreet.blackscholes import Greeks
from volstreet.utils.core import (
    time_to_expiry,
    current_time,
    dynamic_ceil,
    dynamic_floor,
    round_shares_to_lot_size,
    filter_orderbook_by_time,
)
from volstreet.utils.communication import notifier
from volstreet.utils.data_io import load_json_data, load_combine_save_json_data
from volstreet.angel_interface.interface import (
    ActiveSession,
    LiveFeeds,
    fetch_quotes,
    fetch_book,
    lookup_and_return,
)
from volstreet.trade_interface import (
    Index,
    Strangle,
    Straddle,
    Action,
    Option,
    OptionType,
    execute_instructions,
    place_option_order_and_notify,
    cancel_pending_orders,
)
from volstreet.strategies.optimization import (
    filter_greeks_frame,
    optimize_option_weights,
)
from volstreet.strategies.error_handling import log_error


@define(slots=False, repr=False, eq=False)
class ActiveOption(Option):
    """An extension of Option for more flexibility.
    Counterpart attribute is only implemented to conduct the hygiene check. It has no other use.
    """

    # class attributes
    _disable_singleton = True

    # Required arguments
    strike = field(validator=validators.instance_of((int, float)))
    option_type = field(
        validator=validators.instance_of(OptionType), repr=lambda x: x.value
    )
    underlying = field(validator=validators.instance_of(str))
    expiry = field(validator=validators.instance_of(str))
    underlying_instance = field(repr=False, validator=validators.instance_of(Index))

    # Optional arguments
    caching = field(default=False, validator=validators.instance_of(bool))

    # Other attributes with default values
    recommended_qty = field(
        validator=validators.instance_of(int), default=0, init=False
    )  # Used for delta hedging for now
    _active_qty = field(validator=validators.instance_of(int), init=False, default=0)
    _premium_received = field(
        validator=validators.instance_of((int, float)), init=False, default=0
    )
    _ltp = field(default=np.nan, init=False)
    _last_ltp_fetch_time = field(default=datetime(1997, 12, 30), init=False)
    _greeks = field(default=None, init=False)
    _last_greeks_fetch_time = field(default=datetime(1997, 12, 30), init=False)
    counterpart = field(
        validator=validators.instance_of(Option),
        init=False,
    )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(strike={self.strike}, option_type={self.option_type.value}, "
            f"underlying={self.underlying}, expiry={self.expiry}, active_qty={self.active_qty}, "
            f"premium_received={self.premium_received}, "
            f"recommended_qty={self.recommended_qty})"
        )

    def __hash__(self):
        return hash((self.strike, self.option_type.value, self.underlying, self.expiry))

    def __eq__(self, other):
        if not isinstance(other, (Option, ActiveOption)):
            return False
        return (
            self.strike == other.strike
            and self.option_type == other.option_type
            and self.underlying == other.underlying
            and self.expiry == other.expiry
        )

    @counterpart.default
    def _counterpart_default(self):
        return Option(
            strike=self.strike,
            option_type=(
                OptionType.PUT
                if self.option_type == OptionType.CALL
                else OptionType.CALL
            ),
            underlying=self.underlying,
            expiry=self.expiry,
        )

    @property
    def active_qty(self):
        return self._active_qty

    @active_qty.setter
    def active_qty(self, value):
        current_stack = inspect.stack()
        caller_function_name = current_stack[2].function
        if caller_function_name != "update_active_qty_and_premium":
            raise Exception(
                "active_qty can only be set from 'update_active_qty_and_premium' function. "
                "Please use that function to update the active qty."
            )
        self._active_qty = value

    @property
    def premium_received(self):
        return self._premium_received

    @premium_received.setter
    def premium_received(self, value):
        current_stack = inspect.stack()
        caller_function_name = current_stack[2].function
        if caller_function_name != "update_active_qty_and_premium":
            raise Exception(
                "premium_received can only be set from 'update_active_qty_and_premium' function. "
                "Please use that function to update the active qty."
            )
        self._premium_received = value

    @property
    def premium_outstanding(self):
        return self.active_qty * self.current_ltp

    @property
    def position_greeks(self) -> Greeks:
        return self.current_greeks * self.active_qty

    @property
    def current_ltp(self) -> float:
        """The difference between this function and the parent function is that
        this function will set cached ltp."""
        if (
            self.caching
            and not np.isnan(self._ltp)
            and current_time() - self._last_ltp_fetch_time
            < timedelta(seconds=config.CACHE_INTERVAL)
        ):
            return self._ltp
        else:  # Fetch from source
            ltp = super().fetch_ltp()
            self._ltp = ltp
            self._last_ltp_fetch_time = current_time()
            return ltp

    @property
    def current_greeks(self) -> Greeks:
        """The difference between this function and the parent function is that
        this function will conduct a hygiene check and set cached greeks."""

        # Use cached greeks if eligible
        if (
            self.caching
            and self._greeks is not None
            and current_time() - self._last_greeks_fetch_time
            < timedelta(seconds=config.CACHE_INTERVAL)
        ):
            return self._greeks

        else:  # Fetch from source
            spot = self.underlying_instance.fetch_ltp()
            r = self.underlying_instance.get_basis_for_expiry(
                self.expiry, underlying_price=spot
            )
            price = self.current_ltp
            tte = time_to_expiry(self.expiry)

            greeks = super().fetch_greeks(spot, price, tte, r)
            if np.isnan(greeks.delta) or np.isnan(greeks.gamma):
                counter_greeks = self.counterpart.fetch_greeks(
                    spot=spot,
                    t=tte,
                    r=r,
                )
                greeks = greek_hygiene_check(
                    target_greeks=greeks,
                    counter_greeks=counter_greeks,
                    option_type=self.option_type,
                )
            self._greeks = greeks
            self._last_greeks_fetch_time = current_time()
            return greeks

    def execute_order(
        self,
        quantity_in_shares: int,
        price: float,
        order_tag: str = "",
        notifier_url: str | None = None,
    ) -> None:
        """This function should place an order and return the average price."""
        if quantity_in_shares == 0:
            return  # Safeguard against placing orders with 0 qty

        price = "LIMIT" if LiveFeeds.price_feed_connected() or price is None else price
        transaction_type = Action.BUY if quantity_in_shares > 0 else Action.SELL
        qty_in_lots = int(abs(quantity_in_shares) / self.lot_size)
        avg_price = place_option_order_and_notify(
            self,
            action=transaction_type,
            qty_in_lots=qty_in_lots,
            prices=price,
            order_tag=order_tag,
            webhook_url=notifier_url,
        )
        self.update_active_qty_and_premium(quantity_in_shares, avg_price)

    def update_active_qty_and_premium(self, adjustment_qty: int, avg_price: float):
        self.active_qty = self.active_qty + adjustment_qty
        self.premium_received = self.premium_received - (adjustment_qty * avg_price)


class PositionMonitor:
    def __init__(self, underlying: Index, **kwargs):
        self.underlying = underlying
        self.instrument = None
        self.position_active = False
        self.exit_triggers = {}
        self.counter = 0

        for key, value in kwargs.items():
            setattr(self, key, value)

    def exit_triggered(self):
        return any(self.exit_triggers.values())


@define(slots=False)
class DeltaPosition:
    # Required attributes
    underlying: Index = field(validator=validators.instance_of(Index))
    base_exposure_qty = field()

    # Other attributes with default values
    order_tag = field(default="", validator=validators.instance_of(str))
    cached_strikes = field(default=[], repr=False)
    expiry = field(validator=validators.instance_of(str))
    _prospective_calls = field(factory=list, repr=False)
    _prospective_puts = field(factory=list, repr=False)
    hedge_call_option = field(default=None, repr=False)
    hedge_put_option = field(default=None, repr=False)
    exit_triggers: dict[str, bool] = field(
        factory=lambda: {"end_time": False, "qty_breach_exit": False}
    )
    notifier_url: str = field(default=None)

    @property
    def all_options(self):
        return self._prospective_calls + self._prospective_puts

    def _filter_prospective_options(self, options, option_type):
        """
        Filter out illiquid options from a given list of options based on the option type.

        :param options: List of options to filter.
        :param option_type: Type of the options (CALL or PUT).
        :return: Filtered list of options.
        """
        try:
            otm_strikes = self.underlying.get_otm_strikes(
                [opt.strike for opt in options], option_type
            )
            filtered_options = filter_out_illiquid_options(
                [opt for opt in options if opt.strike in otm_strikes],
                timedelta_minutes=3,
            )
        except Exception as e:
            logger.error(
                f"Error while filtering out illiquid options for {self.underlying.name} "
                f"with error {e} and traceback {traceback.format_exc()}"
            )
            filtered_options = options
        return filtered_options

    @property
    def prospective_calls(self):
        return self._filter_prospective_options(
            self._prospective_calls, OptionType.CALL
        )

    @prospective_calls.setter
    def prospective_calls(self, value):
        raise Exception("prospective_calls attribute is read only")

    @property
    def prospective_puts(self):
        return self._filter_prospective_options(self._prospective_puts, OptionType.PUT)

    @prospective_puts.setter
    def prospective_puts(self, value):
        raise Exception("prospective_puts attribute is read only")

    @property
    def prospective_options(self):
        return self.prospective_calls + self.prospective_puts

    @prospective_options.setter
    def prospective_options(self, value):
        raise Exception(f"prospective_options attribute is read only")

    @property
    def recommended_calls(self):
        if self._prospective_calls:
            recommended_calls = [
                call for call in self._prospective_calls if call.recommended_qty != 0
            ]
            return recommended_calls
        return []

    @recommended_calls.setter
    def recommended_calls(self, value):
        raise Exception("recommended_calls attribute is read only")

    @property
    def recommended_puts(self):
        if self._prospective_puts:
            recommended_puts = [
                put for put in self._prospective_puts if put.recommended_qty != 0
            ]
            return recommended_puts
        return []

    @recommended_puts.setter
    def recommended_puts(self, value):
        raise Exception("recommended_puts attribute is read only")

    @property
    def recommended_options(self):
        if self.all_options:
            return [opt for opt in self.all_options if opt.recommended_qty != 0]
        return []

    @recommended_options.setter
    def recommended_options(self, value):
        raise Exception("recommended_options attribute is read only")

    @property
    def active_call_options(self):
        if self._prospective_calls:
            return [opt for opt in self._prospective_calls if opt.active_qty != 0]
        return []

    @active_call_options.setter
    def active_call_options(self, value):
        raise Exception("active_call_options attribute is read only")

    @property
    def active_put_options(self):
        if self._prospective_puts:
            return [opt for opt in self._prospective_puts if opt.active_qty != 0]
        return []

    @active_put_options.setter
    def active_put_options(self, value):
        raise Exception("active_put_options attribute is read only")

    @property
    def active_options(self):
        if self.all_options:
            return [opt for opt in self.all_options if opt.active_qty != 0]
        return []

    @active_options.setter
    def active_options(self, value):
        raise Exception("active_options attribute is read only")

    @expiry.default
    def _expiry_default(self):
        return self.underlying.current_expiry

    @property
    def aggregate_call_active_qty(self):
        return sum(
            opt.active_qty
            for opt in self._prospective_calls
            if opt.option_type == OptionType.CALL
        )

    @property
    def aggregate_put_active_qty(self):
        return sum(
            opt.active_qty
            for opt in self._prospective_puts
            if opt.option_type == OptionType.PUT
        )

    @staticmethod
    def get_option_greeks(options, informative: bool = False) -> np.ndarray:
        """Returns a 2d array of greeks for each option in the collection"""
        greeks = np.array([option.current_greeks.as_array() for option in options])
        if informative:
            strikes = np.array([option.strike for option in options])
            ltp = np.array([option._ltp for option in options])
            return np.column_stack((strikes, ltp, greeks))
        else:
            return greeks

    @staticmethod
    def get_option_ivs(options: list[Option], filter_func: Callable = None):
        ivs = [option.current_greeks.iv for option in options]
        if filter_func:
            return np.array([*filter(filter_func, ivs)])
        else:
            return np.array(ivs)

    @staticmethod
    def get_option_deltas(options: list[Option], filter_func: Callable = None):
        deltas = [option.current_greeks.delta for option in options]
        if filter_func:
            return np.array([*filter(filter_func, deltas)])
        else:
            return np.array(deltas)

    @staticmethod
    def get_option_gammas(options: list[Option], filter_func: Callable = None):
        gammas = [option.current_greeks.gamma for option in options]
        if filter_func:
            return np.array([*filter(filter_func, gammas)])
        else:
            return np.array(gammas)

    def potential_greeks(self) -> Greeks:
        greeks = np.sum(
            [(opt.recommended_qty * opt.current_greeks) for opt in self.all_options]
        )
        return greeks

    def aggregate_greeks(self) -> Greeks:
        return np.sum([opt.position_greeks for opt in self.active_options])

    def reset_options(self):
        for option in self.all_options:
            option.recommended_qty = 0

    def identify_prospective_options(
        self,
        range_of_strikes: int,
        options_with_cache: bool,
    ) -> tuple[list[ActiveOption], list[ActiveOption]]:
        if (
            LiveFeeds.price_feed_connected()
            and self.underlying
            in LiveFeeds.price_feed.underlying_options_subscribed.keys()
        ):
            logger.info(
                f"{self.underlying.name} fetched prospective strikes from live feed"
            )
            strikes = LiveFeeds.price_feed.underlying_options_subscribed[
                self.underlying
            ]
        else:
            strikes = self.underlying.get_active_strikes(range_of_strikes)

        self.cached_strikes = strikes

        return (
            [
                ActiveOption(
                    strike=strike,
                    option_type=OptionType.CALL,
                    underlying=self.underlying.name,
                    expiry=self.expiry,
                    underlying_instance=self.underlying,
                    caching=options_with_cache,
                )
                for strike in strikes
            ],
            [
                ActiveOption(
                    strike=strike,
                    option_type=OptionType.PUT,
                    underlying=self.underlying.name,
                    expiry=self.expiry,
                    underlying_instance=self.underlying,
                    caching=options_with_cache,
                )
                for strike in strikes
            ],
        )

    def update_prospective_options(
        self, range_of_strikes: int, options_with_cache: bool
    ) -> None:
        prospective_calls, prospective_puts = self.identify_prospective_options(
            range_of_strikes=range_of_strikes, options_with_cache=options_with_cache
        )

        # Convert prospective options and current options to sets for efficient processing
        prospective_calls_set = set(prospective_calls)
        prospective_puts_set = set(prospective_puts)
        current_calls_set = set(self._prospective_calls)
        current_puts_set = set(self._prospective_puts)

        # Use set operations to find the difference
        new_calls = prospective_calls_set - current_calls_set
        new_puts = prospective_puts_set - current_puts_set
        calls_to_remove = current_calls_set - prospective_calls_set
        puts_to_remove = current_puts_set - prospective_puts_set

        # Update the current prospective calls and puts
        current_calls_set.update(new_calls)
        current_puts_set.update(new_puts)
        current_calls_set -= calls_to_remove
        current_puts_set -= puts_to_remove

        # If the original attributes must be lists, convert them back
        self._prospective_calls = [*sorted(current_calls_set, key=lambda x: x.strike)]
        self._prospective_puts = [
            *sorted(current_puts_set, key=lambda x: -1 * x.strike)
        ]  # Descending order

    def set_hedge_options(self):
        self.hedge_call_option = min(
            self.prospective_calls, key=lambda x: abs(x.current_greeks.delta - 0.5)
        )
        self.hedge_put_option = min(
            self.prospective_puts, key=lambda x: abs(x.current_greeks.delta + 0.5)
        )

    def update_underlying(self) -> None:
        """Updates the underlying price and the implied future interest rate."""
        self.underlying.fetch_ltp()
        self.underlying.get_basis_for_expiry(self.expiry)

    def _handle_option_type(self, options, target_delta):
        higher_options = [
            *filter(lambda x: abs(x.current_greeks.delta) >= target_delta, options)
        ]
        lower_options = [
            *filter(lambda x: abs(x.current_greeks.delta) < target_delta, options)
        ]

        if not higher_options and not lower_options:
            notifier(
                f"{self.underlying.name} no options found for target delta {target_delta} "
                f"increasing target delta by 0.1.",
                self.notifier_url,
                "ERROR",
            )
            return False

        if higher_options and not lower_options:  # Only higher options are available
            option_to_sell = min(
                higher_options, key=lambda x: abs(x.current_greeks.delta)
            )
            option_to_sell.recommended_qty = -round_shares_to_lot_size(
                self.base_exposure_qty, option_to_sell.lot_size
            )
            return True

        upper_option = min(higher_options, key=lambda x: abs(x.current_greeks.delta))
        lower_option = max(lower_options, key=lambda x: abs(x.current_greeks.delta))

        ratio_upper = (target_delta - abs(lower_option.current_greeks.delta)) / (
            abs(upper_option.current_greeks.delta)
            - abs(lower_option.current_greeks.delta)
        )
        ratio_lower = (abs(upper_option.current_greeks.delta) - target_delta) / (
            abs(upper_option.current_greeks.delta)
            - abs(lower_option.current_greeks.delta)
        )

        if ratio_upper > 1 or ratio_lower > 1:
            notifier(
                f"Weird quantity ratios for {self.underlying.name}. "
                f"Ratios: {ratio_upper} and {ratio_lower}. "
                f"Upper option: {upper_option}. "
                f"Lower option: {lower_option}. Retrying...",
                self.notifier_url,
                "ERROR",
            )
            return "retry"

        upper_option_qty = round_shares_to_lot_size(
            self.base_exposure_qty * ratio_upper, upper_option.lot_size
        )
        lower_option_qty = round_shares_to_lot_size(
            self.base_exposure_qty * ratio_lower, lower_option.lot_size
        )

        upper_option.recommended_qty = -upper_option_qty
        lower_option.recommended_qty = -lower_option_qty
        return True

    def prepare_greek_frame_with_options(
        self, options: list[Option], is_call: bool
    ) -> np.ndarray:
        greeks = self.get_option_greeks(options, informative=True)
        array = np.array([option for option in options])
        greeks = np.column_stack((greeks, array))
        logger.debug(f"Greeks: {greeks}. Dispatching to filter_greeks_frame")
        greeks = filter_greeks_frame(
            greeks,
            0.65,
            self.underlying.get_synthetic_future_price(self.expiry),
            is_call,
        )
        return greeks

    def set_recommendation_for_first_side(
        self,
        options: list[Option],
        is_call: bool,
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        greeks = self.prepare_greek_frame_with_options(options, is_call)

        # Finding the gamma of the option whose delta is closest to 0.1
        idx = np.abs(greeks[:, 2] - 0.1).argmin()
        target_gamma = greeks[idx, 3]
        gamma_floor = dynamic_floor(target_gamma)
        gamma_ceil = dynamic_ceil(target_gamma)

        for attempt in range(3):
            try:
                weights = optimize_option_weights(
                    greeks[:, 2],
                    greeks[:, 3],
                    0.09,
                    0.6,
                    gamma_floor,
                    gamma_ceil,
                )
                break
            except OptimizationError as e:
                if attempt == 2:
                    raise e
                gamma_floor *= 0.95
                gamma_ceil *= 1.05
            except Exception as e:
                logger.error(
                    f"Error in optimization: {e}, Traceback: {traceback.format_exc()}"
                )
                raise e

        # noinspection PyUnboundLocalVariable
        for option, weight in zip(greeks[:, -1], weights):
            option.recommended_qty = round_shares_to_lot_size(
                weight * self.base_exposure_qty, option.lot_size
            )

        # Return the weighted delta which will be used to configure the other side
        calibrated_delta = np.dot(weights, greeks[:, 2])
        target_deltas = (abs(calibrated_delta) - 0.01, abs(calibrated_delta) + 0.01)
        target_gammas = (gamma_floor, gamma_ceil)
        return target_deltas, target_gammas

    def set_recommendation_for_second_side(
        self,
        options: list[Option],
        is_call: bool,
        target_deltas: tuple[float, float],
        target_gammas: tuple[float, float],
    ) -> None:
        greeks = self.prepare_greek_frame_with_options(options, is_call)

        for attempt in range(3):
            try:
                # This will try with multiple gamma scalers within itself,
                # if all fails, it will raise an OptimizationError
                weights = optimize_option_weights(
                    greeks[:, 2], greeks[:, 3], *target_deltas, *target_gammas
                )
                break
            except OptimizationError:
                if attempt == 2:
                    raise OptimizationError("Second side optimization failed")
                elif attempt == 1:
                    target_gammas = (-10000, 10000)  # Use the entire range
                else:
                    target_gammas = (target_gammas[0] * 0.75, target_gammas[1] * 1.25)
            except Exception as e:
                logger.error(
                    f"Error in optimization: {e}, Traceback: {traceback.format_exc()}"
                )
                raise OptimizationError("Second side optimization failed")

        # noinspection PyUnboundLocalVariable
        for option, weight in zip(greeks[:, -1], weights):
            option.recommended_qty = round_shares_to_lot_size(
                weight * self.base_exposure_qty, option.lot_size
            )

    def set_optimized_recommended_qty(self) -> None:
        self.reset_options()
        try:
            target_deltas, target_gammas = self.set_recommendation_for_first_side(
                self.prospective_calls, is_call=True
            )
            self.set_recommendation_for_second_side(
                self.prospective_puts,
                is_call=False,
                target_deltas=target_deltas,
                target_gammas=target_gammas,
            )
        except Exception as e:
            if "Second side optimization failed" in str(e):
                notifier(
                    f"Second side optimization failed for {self.underlying.name}. "
                    f"Trying to calibrate again in reverse order.",
                    self.notifier_url,
                    "ERROR",
                )
                self.reset_options()  # CRUCIAL TO RESET THE OPTIONS

                # Reverse the order of calibration
                target_deltas, target_gammas = self.set_recommendation_for_first_side(
                    self.prospective_puts, is_call=False
                )
                self.set_recommendation_for_second_side(
                    self.prospective_calls,
                    is_call=True,
                    target_deltas=target_deltas,
                    target_gammas=target_gammas,
                )
            else:
                notifier(
                    f"Optimization failed for {self.underlying.name}.",
                    self.notifier_url,
                    "ERROR",
                )
                raise e

    def set_recommended_qty_backup(
        self, target_delta: float = None, attempt_no: int = 0
    ):
        self.reset_options()

        if target_delta > 0.7 or attempt_no > 5:
            raise ValueError(
                f"Unable to calibrate positions for {self.underlying.name} "
                f"after {attempt_no} attempts."
            )

        if attempt_no > 0:
            self.update_underlying()

        success_calls = self._handle_option_type(
            self.prospective_calls,
            target_delta,
        )
        success_puts = self._handle_option_type(
            self.prospective_puts,
            target_delta,
        )

        if success_calls == "retry" or success_puts == "retry":
            self.set_recommended_qty_backup(
                target_delta=target_delta, attempt_no=attempt_no + 1
            )

        if not success_calls or not success_puts:
            self.set_recommended_qty_backup(
                target_delta=target_delta + 0.1, attempt_no=attempt_no + 1
            )

    def set_recommended_qty(self, target_delta: float, optimized: bool) -> None:
        if optimized:
            try:
                self.set_optimized_recommended_qty()
            except Exception as e:
                notifier(
                    f"{self.underlying.name} Error while setting optimized recommended qty: {e}\n"
                    f"Using backup implementation\n"
                    f"Traceback: {e.__traceback__}",
                    self.notifier_url,
                    "ERROR",
                )
                self.set_recommended_qty_backup(target_delta)
        else:
            self.set_recommended_qty_backup(target_delta)

    def adjust_recommended_qty(self):
        """Adjusts the recommended qty to account for active qty in order to avoid unnecessary
        orders."""
        for option in self.all_options:
            if option.recommended_qty == 0 and option.active_qty == 0:
                continue
            option.recommended_qty = option.recommended_qty - option.active_qty

    def enter_positions(self) -> None:
        instructions = {
            option: {
                "action": Action.BUY if option.recommended_qty >= 0 else Action.SELL,
                "price": option.current_ltp,
                "quantity_in_lots": abs(option.recommended_qty) / option.lot_size,
                "order_tag": self.order_tag,
            }
            for option in self.recommended_options
        }
        execution_details = execute_instructions(instructions)
        for option, avg_price in execution_details.items():
            option.update_active_qty_and_premium(option.recommended_qty, avg_price)
            option.recommended_qty = 0

    def reset_trigger_flags(self):
        self.exit_triggers = {"end_time": False, "qty_breach_exit": False}

    def recommend_delta_action(
        self,
        delta_threshold: float,
        aggregate_delta: float,
    ) -> tuple[ActiveOption, int] | tuple[None, np.nan]:
        """Returns a negative qty because the qty is to be sold."""
        hedge_call_delta = self.hedge_call_option.current_greeks.delta
        hedge_put_delta = self.hedge_put_option.current_greeks.delta
        if (
            aggregate_delta >= delta_threshold
        ):  # Net delta is positive, sell the required qty of calls
            qty_to_sell = int((abs(aggregate_delta) - 0) / abs(hedge_call_delta))
            option_to_sell = self.hedge_call_option
        elif (
            aggregate_delta <= -delta_threshold
        ):  # Net delta is negative, sell the required qty of puts
            qty_to_sell = int((abs(aggregate_delta) - 0) / abs(hedge_put_delta))
            option_to_sell = self.hedge_put_option
        else:
            return None, 0

        qty_to_sell = round_shares_to_lot_size(qty_to_sell, option_to_sell.lot_size)
        if qty_to_sell == 0:
            return None, 0
        else:
            return (None, 0) if qty_to_sell == 0 else (option_to_sell, -qty_to_sell)

    def check_for_breach(
        self,
        adjustment_leg: OptionType,
        adjustment_qty: int,
        max_qty_shares: int,
    ) -> bool:
        if adjustment_leg == OptionType.CALL:  # Market is moving down
            breach = (
                abs(self.aggregate_call_active_qty) + adjustment_qty
            ) > max_qty_shares
        elif adjustment_leg == OptionType.PUT:  # Market is moving up
            breach = (
                abs(self.aggregate_put_active_qty) + adjustment_qty
            ) > max_qty_shares
        else:
            raise ValueError("Invalid option type")
        return breach

    def exit_positions(self):
        """Handles squaring up of the position"""
        instructions = {
            option: {
                "action": Action.BUY if option.active_qty <= 0 else Action.SELL,
                "price": option.current_ltp,
                "quantity_in_lots": abs(option.active_qty) / option.lot_size,
                "order_tag": self.order_tag,
            }
            for option in self.active_options
        }
        execution_details = execute_instructions(instructions)
        for option, avg_price in execution_details.items():
            option.update_active_qty_and_premium(-option.active_qty, avg_price)

    def record_position_status(self) -> None:
        """Designed to periodically save the position status to a file."""
        """
        Saves the current position status to a JSON file periodically.
        """

        date = current_time().strftime("%Y-%m-%d")
        file_path = f"{ActiveSession.obj.userId}\\{self.underlying.name}_delta_data\\{date}.json"

        position_status = {
            "timestamp": current_time(),
            "underlying": self.underlying.name,
            "expiry": self.expiry,
            "base_exposure_qty": self.base_exposure_qty,
            "active_call_options": [
                {
                    "strike": option.strike,
                    "option_type": option.option_type.value,
                    "active_qty": option.active_qty,
                    "premium_received": option.premium_received,
                    "current_ltp": option.current_ltp,
                    "current_greeks": option.current_greeks.as_dict(),
                }
                for option in self.active_call_options
            ],
            "active_put_options": [
                {
                    "strike": option.strike,
                    "option_type": option.option_type.value,
                    "active_qty": option.active_qty,
                    "premium_received": option.premium_received,
                    "current_ltp": option.current_ltp,
                    "current_greeks": option.current_greeks.as_dict(),
                }
                for option in self.active_put_options
            ],
            "aggregate_greeks": self.aggregate_greeks().as_dict(),
            "exit_triggers": self.exit_triggers,
        }

        load_combine_save_json_data(position_status, file_path, default_structure=list)


def generate_optimized_result(
    greeks: np.ndarray, weights: np.ndarray, idx: np.ndarray
) -> np.ndarray:
    optimized_result = np.round(
        (greeks[idx] * weights.reshape(-1, 1)).sum(
            axis=0,
        ),
        4,
    )
    return optimized_result


def generate_optimized_weight_array(
    number_of_rows: int, indices: np.ndarray, weights: np.ndarray
) -> np.ndarray:
    # Step 1: Create a new zero-filled column
    new_column = np.zeros((number_of_rows, 1))

    # Step 2: Insert new values at specified indices
    new_column[indices] = weights.reshape(-1, 1)

    return new_column


def greek_hygiene_check(
    target_greeks: Greeks, counter_greeks: Greeks, option_type: OptionType
) -> Greeks:
    """Currently only handles delta and gamma"""
    target_delta = getattr(target_greeks, "delta")
    counter_delta = getattr(counter_greeks, "delta")

    target_gamma = getattr(target_greeks, "gamma")
    counter_gamma = getattr(counter_greeks, "gamma")

    if np.isnan(target_delta):
        if option_type == OptionType.CALL:
            setattr(target_greeks, "delta", counter_delta + 1)
        elif option_type == OptionType.PUT:
            setattr(target_greeks, "delta", counter_delta - 1)

    if np.isnan(target_gamma):
        setattr(target_greeks, "gamma", counter_gamma)

    return target_greeks


def efficient_ltp_for_options(
    options: list[Option] | set[Option],
) -> dict[Option, float]:
    """
    Fetches the latest trading prices (LTPs) for a set of options.

    :param options: A list of Option objects.
    :return: A dictionary mapping each unique option to its latest trading price (LTP).
    """
    # Fetch the LTP for each unique option
    tokens = [option.token for option in options]

    split_tokens = [tokens[i : i + 50] for i in range(0, len(tokens), 50)]

    all_quotes = []
    for i, split in enumerate(split_tokens):
        all_quotes.append(fetch_quotes(split))
        if i + 1 < len(split_tokens):
            sleep(1)

    all_quotes = [quote for quotes in all_quotes for quote in quotes]

    ltp_cache = {
        option: quote["ltp"]
        for quote in all_quotes
        for option in options
        if option.token == quote["symbolToken"]
    }

    return ltp_cache


def efficient_ltp_for_strangles(strangles: list[Strangle]) -> dict[Option, float]:
    """
    Fetches the latest trading prices (LTPs) for a set of options extracted from a list of strangles.

    :param strangles: A list of Strangle objects.
    :return: A dictionary mapping each unique option to its latest trading price (LTP).
    """
    # Create a set of all distinct options from the strangles
    options = set(
        option
        for strangle in strangles
        for option in (strangle.call_option, strangle.put_option)
    )

    # Fetch the LTP for each unique option
    ltp_cache = efficient_ltp_for_options(options)
    return ltp_cache


def get_range_of_strangles(
    underlying: Index,
    call_strike_offset: float | int = 0,
    put_strike_offset: float | int = 0,
    expiry: str = None,
    strike_range: int = 10,
):
    if expiry is None:
        expiry = underlying.current_expiry

    if call_strike_offset == -put_strike_offset:  # Straddle
        strikes = underlying.get_active_strikes(strike_range, call_strike_offset)
        return [Straddle(strike, underlying.name, expiry) for strike in strikes]
    else:
        call_strike_range = underlying.get_active_strikes(
            strike_range, call_strike_offset
        )
        put_strike_range = underlying.get_active_strikes(
            strike_range, put_strike_offset
        )
        pairs = product(call_strike_range, put_strike_range)
        strangles = [
            Strangle(pair[0], pair[1], underlying.name, expiry) for pair in pairs
        ]
        return strangles


def filter_strangles_by_delta(
    deltas: dict[Strangle, tuple[float, float]],
    delta_range: tuple[float, float],
) -> dict[Strangle, tuple[float, float]]:
    """Filtering for strangles with delta between delta_range"""
    min_range = delta_range[0]
    max_range = delta_range[1]
    filtered = {
        strangle: deltas[strangle]
        for strangle in deltas
        if all([min_range <= abs(delta) <= max_range for delta in deltas[strangle]])
    }  # Condition is that both call and put delta should be within the range

    return filtered


def most_equal_strangle(
    underlying: Index,
    call_strike_offset: float | int = 0,
    put_strike_offset: float | int = 0,
    disparity_threshold: float = 1000,
    exit_time: tuple[int, int] = (15, 25),
    range_of_strikes: int = 4,
    expiry: str = None,
    notification_url: str = None,
) -> Strangle | Straddle | None:
    if expiry is None:
        expiry = underlying.current_expiry

    strangles = get_range_of_strangles(
        underlying,
        call_strike_offset=call_strike_offset,
        put_strike_offset=put_strike_offset,
        expiry=expiry,
        strike_range=range_of_strikes,
    )
    # logger.info(f"{underlying.name} prospective strangles: {strangles}")

    # Define the price disparity function
    def price_disparity(strangle):
        call_ltp = ltp_cache.get(strangle.call_option, np.nan)
        put_ltp = ltp_cache.get(strangle.put_option, np.nan)
        return abs(call_ltp - put_ltp) / min(call_ltp, put_ltp)

    tracked_strangle = None

    last_notified_time = current_time() - timedelta(minutes=6)
    while current_time().time() < time(*exit_time):
        # If there's no tracked strangle update all prices and find the most equal strangle
        if tracked_strangle is None:
            ltp_cache = efficient_ltp_for_strangles(strangles)
            most_equal, min_disparity = min(
                ((s, price_disparity(s)) for s in strangles), key=lambda x: x[1]
            )
            if min_disparity < 0.10:
                tracked_strangle = most_equal

        # If there's a tracked strangle, check its disparity
        else:
            ltp_cache = {
                tracked_strangle.call_option: tracked_strangle.call_option.fetch_ltp(),
                tracked_strangle.put_option: tracked_strangle.put_option.fetch_ltp(),
            }
            most_equal = tracked_strangle
            min_disparity = price_disparity(tracked_strangle)
            if min_disparity >= 0.10:
                tracked_strangle = None

        logger.info(
            f"Most equal strangle: {most_equal} with disparity {min_disparity} "
            f"and prices {ltp_cache[most_equal.call_option]} and {ltp_cache[most_equal.put_option]}"
        )
        if last_notified_time < current_time() - timedelta(minutes=5):
            notifier(
                f"Most equal strangle: {most_equal} with disparity {min_disparity} "
                f"and prices {ltp_cache[most_equal.call_option]} and {ltp_cache[most_equal.put_option]}",
                notification_url,
                "INFO",
            )
            logger.info(f"Most equal ltp cache: {ltp_cache}")
            last_notified_time = current_time()
        # If the lowest disparity is below the threshold, return the most equal strangle
        if min_disparity < disparity_threshold:
            return most_equal
        else:
            pass
        sleep(0.5)

    else:
        return None


def approve_execution(
    underlying: Index,
    override_expiry_day_restriction: bool,
) -> bool:
    """Used in long-standing strategies to check if the strategy is eligible for execution"""

    current_expiry_tte = time_to_expiry(underlying.current_expiry, in_days=True)
    if current_expiry_tte < 1:
        return True
    # If current expiry is more than 1 day away, then the strategy is not eligible
    # unless override_expiry_day_restriction is True
    elif current_expiry_tte >= 1 and not override_expiry_day_restriction:
        return False


def most_even_delta_strangle(
    underlying: Index,
    delta_range: tuple[float, float] = (0.0, 100),
    expiry: str = None,
    strike_range: int = 6,
) -> tuple[Strangle | Straddle, float] | tuple[None, np.nan]:
    strangles = get_range_of_strangles(
        underlying,
        call_strike_offset=0.001,  # Setting a small offset to force return Strangle instead of Straddle
        put_strike_offset=0.001,
        expiry=expiry,
        strike_range=strike_range,
    )
    strangle_deltas: dict = calculate_strangle_deltas(underlying, strangles)
    strangle_deltas: dict = filter_strangles_by_delta(strangle_deltas, delta_range)
    unevenness: dict = calculate_unevenness_of_deltas(strangle_deltas)
    logger.info(
        f"{current_time()} {underlying.name} strangle deltas: {strangle_deltas}"
    )
    logger.info(
        f"{current_time()} {underlying.name} unevenness of deltas: {unevenness} "
    )
    # Checking if the unevenness dictionary is empty
    if not unevenness:
        return None, np.nan
    target_strangle: Strangle | Straddle = min(unevenness, key=unevenness.get)
    minimum_unevenness: float = unevenness[target_strangle]
    return target_strangle, minimum_unevenness


def calculate_strangle_deltas(
    index: Index, strangles: list[Strangle | Straddle]
) -> dict[Strangle, tuple[float, float]]:
    underlying_ltp = index.fetch_ltp()
    option_prices: dict[Option, float] = efficient_ltp_for_strangles(strangles)
    # Now determining the prevailing interest rate
    if [
        strangle for strangle in strangles if isinstance(strangle, Straddle)
    ]:  # Randomly choosing the first straddle
        synthetic_future_price = (
            strangles[0].call_strike
            + option_prices[strangles[0].call_option]
            - option_prices[strangles[0].put_option]
        )
    else:
        synthetic_future_price = None

    interest_rate = index.get_basis_for_expiry(
        strangles[0].expiry,
        underlying_price=underlying_ltp,
        future_price=synthetic_future_price,
    )

    option_greeks = {
        option: option.fetch_greeks(
            spot=underlying_ltp, price=option_prices[option], r=interest_rate
        )
        for option in option_prices
    }

    strangle_deltas = {
        strangle: (
            option_greeks[strangle.call_option].delta,
            option_greeks[strangle.put_option].delta,
        )
        for strangle in strangles
    }

    return strangle_deltas


def calculate_unevenness_of_deltas(
    deltas: dict[Strangle, tuple[float, float]],
) -> dict[Strangle, float]:
    # Filter for any nan values
    deltas = {
        strangle: deltas[strangle]
        for strangle in deltas
        if not any(np.isnan(deltas[strangle]))
    }

    return {
        strangle: (max(np.abs(deltas[strangle])) / min(np.abs(deltas[strangle])))
        for strangle in deltas
    }


def is_in_final_stage(
    underlying: Index,
    strangle: Strangle,
    itm_steps: int,
) -> bool:
    """Equal delta helper function"""
    return (strangle.put_strike - strangle.call_strike) == (itm_steps * underlying.base)


def check_for_universal_exit(
    strangle: Strangle,
    call_avg: float,
    put_avg: float,
    final_sl: float,
    final_stage: bool,
) -> bool:
    """Equal delta helper function"""
    if final_stage:
        move = check_for_move(strangle, call_avg, put_avg, final_sl)
        if move:
            return True
        else:
            return False
    else:
        return False


def check_for_move(
    strangle: Strangle, call_avg: float, put_avg: float, sl: float
) -> bool | Option:
    """Equal delta helper function"""
    call_ltp, put_ltp = strangle.fetch_ltp()
    call_move = (call_ltp / call_avg) - 1
    put_move = (put_ltp / put_avg) - 1
    if call_move > sl:
        return strangle.put_option
    elif put_move > sl:
        return strangle.call_option
    else:
        return False


def identify_new_option(
    underlying: Index, strangle: Strangle, option_to_buy: Option
) -> bool | Option:
    """Equal delta helper function"""
    counter_part = (
        strangle.put_option
        if option_to_buy.option_type == OptionType.CALL
        else strangle.call_option
    )

    strike_range = underlying.get_active_strikes(10)

    prospective_sell_options = [
        Option(strike, option_to_buy.option_type, underlying.name, strangle.expiry)
        for strike in strike_range
    ]

    counter_part_ltp = counter_part.fetch_ltp()

    prospective_sell_options = efficient_ltp_for_options(prospective_sell_options)

    # The new option should be such that its price is closest to the counterparts price
    new_option = min(
        prospective_sell_options,
        key=lambda x: abs(prospective_sell_options[x] - counter_part_ltp),
    )

    return new_option


def check_for_overlap(
    underlying: Index, new_option: Option, strangle: Strangle, itm_steps: int
) -> bool:
    """Equal delta helper function"""
    counter_part = (
        strangle.put_option
        if new_option.option_type == OptionType.CALL
        else strangle.call_option
    )
    overlap = (
        counter_part.strike - new_option.strike
        if new_option.option_type == OptionType.CALL
        else new_option.strike - counter_part.strike
    )
    return overlap > (
        itm_steps * underlying.base
    )  # Is the new option more than n steps ITM?


def move_one_leg(
    underlying: Index,
    strangle: Strangle,
    option_to_buy: Option,
    new_option: Option,
    number_of_lots: int,
    strategy_tag: str,
    notification_url: str,
) -> tuple[Strangle, float]:
    """Equal delta helper function"""
    if option_to_buy == new_option:
        notifier(
            f"Option to buy and new option are the same. No trade required",
            notification_url,
        )
        return strangle, new_option.fetch_ltp()

    place_option_order_and_notify(
        option_to_buy,
        "BUY",
        number_of_lots,
        "LIMIT",
        order_tag=strategy_tag,
        webhook_url=notification_url,
    )
    _avg_price = place_option_order_and_notify(
        new_option,
        "SELL",
        number_of_lots,
        "LIMIT",
        order_tag=strategy_tag,
        webhook_url=notification_url,
        return_avg_price=True,
    )
    call_strike, put_strike = (
        (new_option.strike, strangle.put_strike)
        if option_to_buy.option_type == OptionType.CALL
        else (strangle.call_strike, new_option.strike)
    )
    return (
        Strangle(call_strike, put_strike, underlying.name, strangle.expiry),
        _avg_price,
    )


def calculate_pnl_for_strategy(
    data: list[dict],
    strategy_name: str,
    underlying: str = "",
    flexible_matching: bool = False,
    after_time: datetime | None = None,
) -> float:
    """
    Calculate the PnL for a provided strategy name.

    :param data: List of order dictionaries.
    :param underlying: The underlying symbol.
    :param strategy_name: The exact name of the strategy or a partial name if flexible_matching is True.
    :param flexible_matching: If True, the function will search for order tags containing the strategy_name string.
    :param after_time: If provided, the function will only consider orders placed after this time.
    :return: The total PnL for the strategy.
    """

    if flexible_matching:
        # Include any order with a tag that contains the strategy_name
        filtered_orders = [
            order
            for order in data
            if strategy_name.lower() in order.get("ordertag", "").lower()
            and order.get("tradingsymbol").startswith(underlying)
        ]
    else:
        # Match the strategy name exactly
        filtered_orders = [
            order
            for order in data
            if order.get("ordertag") == strategy_name
            and order.get("tradingsymbol").startswith(underlying)
        ]

    if after_time is not None:
        filtered_orders = [
            order
            for order in filtered_orders
            if datetime.strptime(order.get("updatetime"), "%d-%b-%Y %H:%M:%S")
            > after_time
        ]

    # Calculate the PnL
    total_pnl = sum(
        (float(order["averageprice"]) * int(order["filledshares"]))
        * (-1 if order["transactiontype"] == "BUY" else 1)
        for order in filtered_orders
    )

    return total_pnl


@log_error(notify=True)
def notify_pnl(
    strategy_name: str,
    start_time: datetime,
    underlying: Index,
    notification_url: str,
    additional_info: str = "",
) -> None:
    sleep(10)  # Wait for the exit orders to reflect with average prices
    orderbook: list = fetch_book("orderbook", from_api=True)
    filtered_orderbook = filter_orderbook_by_time(orderbook, start_time=start_time)
    total_pnl: float = calculate_pnl_for_strategy(
        data=filtered_orderbook,
        strategy_name=strategy_name,
        underlying=underlying.name,
        flexible_matching=True,
    )
    notifier(
        f"{underlying.name} strategy {strategy_name} exited. Total pnl: {total_pnl}. {additional_info}",
        notification_url,
        "INFO",
    )


def load_current_straddle(
    underlying_str, user_id: str, file_appendix: str
) -> tuple[Straddle | None, int]:
    """Load current position for a given underlying, user and strategy (file_appendix)."""

    # Loading current position
    trade_data = load_json_data(
        f"{user_id}\\{underlying_str}_{file_appendix}.json",
        default_structure=dict,
    )
    trade_data = trade_data.get(underlying_str, {})
    buy_strike = trade_data.get("strike", None)
    buy_expiry = trade_data.get("expiry", None)
    buy_quantity = trade_data.get("quantity", 0)
    buy_straddle = (
        Straddle(strike=buy_strike, underlying=underlying_str, expiry=buy_expiry)
        if buy_strike is not None and buy_expiry is not None
        else None
    )
    return buy_straddle, buy_quantity


def sleep_until_next_action(
    interval_minutes: int,
    exit_time: tuple[int, int],
    special_condition: Callable = lambda: False,
    tasks_to_perform: list[Callable] = None,
) -> None:
    time_now = current_time()
    if tasks_to_perform is None:
        tasks_to_perform = []

    # Determining the next timestamp
    if isinstance(interval_minutes, int):
        next_timestamp = (time_now + timedelta(minutes=interval_minutes)).replace(
            second=0, microsecond=0
        ) - timedelta(
            seconds=5
        )  # 5 seconds buffer
    elif isinstance(interval_minutes, float):
        next_timestamp = time_now + timedelta(minutes=interval_minutes)
    else:
        raise ValueError("Invalid interval_minutes value")
    next_timestamp = min(
        next_timestamp,
        current_time().replace(
            hour=exit_time[0], minute=exit_time[1], second=0, microsecond=0
        ),
    )

    for task in tasks_to_perform:
        task()

    while current_time() < next_timestamp:
        if special_condition():
            return
        sleep(1)


def filter_out_illiquid_options(
    options: list[ActiveOption], timedelta_minutes: float | int = 3
) -> list[ActiveOption]:
    try:
        if LiveFeeds.price_feed_connected() and all(
            [
                option.token in LiveFeeds.price_feed.data_bank.copy()
                for option in options
            ]
        ):
            return [
                option
                for option in options
                if current_time()
                - LiveFeeds.price_feed.data_bank[option.token].get(
                    "last_traded_datetime", current_time()
                )
                < timedelta(minutes=timedelta_minutes)
            ]
        else:
            return back_up_illiquid_filter(options, timedelta_minutes)

    except Exception as e:
        logger.error(f"Error in filter_out_illiquid_options: {e}", exc_info=True)
        return back_up_illiquid_filter(options, timedelta_minutes)


def back_up_illiquid_filter(
    options: list[ActiveOption], timedelta_minutes: float | int = 3
):
    quotes = fetch_quotes([option.token for option in options], structure="dict")
    return [
        option
        for option in options
        if current_time()
        - datetime.strptime(quotes[option.token]["exchTradeTime"], "%d-%b-%Y %H:%M:%S")
        < timedelta(minutes=timedelta_minutes)
    ]


def process_stop_loss_order_statuses(
    order_book,
    order_ids,
    context="",
    notify_url=None,
):
    pending_text = "trigger pending"
    context = f"{context.capitalize()} " if context else ""

    statuses = lookup_and_return(order_book, "orderid", order_ids, "status")

    if not isinstance(statuses, np.ndarray) or statuses.size == 0:
        logger.error(f"Statuses is {statuses} for orderid(s) {order_ids}")

    if all(statuses == pending_text):
        return False, False

    elif all(statuses == "rejected") or all(statuses == "cancelled"):
        rejection_reasons = lookup_and_return(order_book, "orderid", order_ids, "text")
        if all(rejection_reasons == "17070 : The Price is out of the LPP range"):
            return True, False
        else:
            notifier(
                f"{context}Order(s) rejected or cancelled. Reasons: {rejection_reasons[0]}",
                notify_url,
                "ERROR",
            )
            raise Exception(f"Order(s) rejected or cancelled.")

    elif all(statuses == "pending"):
        sleep(5)
        order_book = fetch_book("orderbook")
        statuses = lookup_and_return(order_book, "orderid", order_ids, "status")

        if all(statuses == "pending"):
            try:
                cancel_pending_orders(order_ids, "NORMAL")
            except Exception as e:
                logger.error(
                    f"{context}Could not cancel orders with variety NORMAL: {e}"
                )
                try:
                    cancel_pending_orders(order_ids, "STOPLOSS")
                except Exception as e:
                    notifier(
                        f"{context}Could not cancel orders: {e}", notify_url, "ERROR"
                    )
                    raise Exception(f"Could not cancel orders: {e}")
            notifier(
                f"{context}Orders pending and cancelled. Please check.",
                notify_url,
                "ERROR",
            )
            return True, False

        elif all(statuses == "complete"):
            return True, True

        else:
            logger.error(
                f"Orders in unknown state. Statuses: {statuses}, Order ids: {order_ids}"
            )
            raise Exception(f"Orders in unknown state.")

    elif all(statuses == "complete"):
        return True, True

    else:
        notifier(
            f"{context}Orders in unknown state. Statuses: {statuses}",
            notify_url,
            "ERROR",
        )
        raise Exception(f"Orders in unknown state.")
