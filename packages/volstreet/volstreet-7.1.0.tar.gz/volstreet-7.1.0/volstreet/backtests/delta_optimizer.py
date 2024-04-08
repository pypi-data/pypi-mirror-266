import numpy as np
import pandas as pd
import pickle
from volstreet import (
    BackTester,
    UnderlyingInfo,
    logger,
    make_directory_if_needed,
)
from volstreet.strategies.optimization import (
    optimize_leg_v1,
)


def run_optimizer_historical(index: str, start_date: str) -> list:
    delta_target = 0.1
    bt = BackTester()
    save_dir = f"data\\optimizer_data"
    mega_list = []
    ui = UnderlyingInfo(index)
    expiries = ui.expiry_dates
    expiries = expiries[expiries <= "2024-02-26"]
    expiries = expiries[expiries > start_date]

    times = ["9:17", "10:00", "11:00", "12:00", "13:00", "14:40"]

    for expiry in expiries:
        for time in times:
            timestamp = f"{pd.to_datetime(expiry).strftime('%Y-%m-%d')} {time}"

            try:
                option_chain = bt.build_option_chain(
                    ui,
                    timestamp,
                    timestamp,
                    num_strikes=30,
                    threshold_days_expiry=0,
                    add_greeks=True,
                )
                call_data = option_chain.loc[
                    option_chain["call_delta"] < 0.58,
                    ["strike", "call_price", "call_delta", "call_gamma"],
                ]
                call_data_array = call_data.values

                put_data = option_chain.loc[
                    option_chain["put_delta"] > -0.58,
                    ["strike", "put_price", "put_delta", "put_gamma"],
                ]
                put_data_array = put_data.values

                for gamma_scaler in [1, 10, 20, 40, 60, 80, 100]:
                    call_result = optimize_leg_v1(
                        call_data_array[:, 2],
                        call_data_array[:, 3],
                        0.05,
                        delta_target,
                        gamma_scaler,
                    )

                    put_result = optimize_leg_v1(
                        put_data_array[:, 2],
                        put_data_array[:, 3],
                        0.05,
                        delta_target,
                        gamma_scaler,
                    )

                    # call_result = optimize_leg_v2(
                    #     call_data_array[:, 2], call_data_array[:, 3], delta_target
                    # )
                    #
                    # put_result = optimize_leg_v2(
                    #     put_data_array[:, 2], put_data_array[:, 3], delta_target
                    # )

                    # Adding the result to the dataframe
                    call_data["optimized_quantity"] = call_result.x
                    put_data["optimized_quantity"] = put_result.x

                    optimized_call_delta = np.dot(
                        call_data["optimized_quantity"], call_data["call_delta"]
                    )
                    optimized_call_gamma = np.dot(
                        call_data["optimized_quantity"], call_data["call_gamma"]
                    )
                    optimized_put_delta = np.dot(
                        put_data["optimized_quantity"], put_data["put_delta"]
                    )
                    optimized_put_gamma = np.dot(
                        put_data["optimized_quantity"], put_data["put_gamma"]
                    )
                    optimized_call_premium = np.dot(
                        call_data["optimized_quantity"], call_data["call_price"]
                    )
                    optimized_put_premium = np.dot(
                        put_data["optimized_quantity"], put_data["put_price"]
                    )

                    optimized_portfolio_delta = (
                        optimized_call_delta + optimized_put_delta
                    )
                    optimized_portfolio_gamma = (
                        optimized_call_gamma + optimized_put_gamma
                    )
                    optimized_portfolio_premium = (
                        optimized_call_premium + optimized_put_premium
                    )

                    data = {
                        "timestamp": timestamp,
                        "index": index,
                        "call_result": call_result,
                        "put_result": put_result,
                        "call_data": call_data,
                        "put_data": put_data,
                        "optimized_call_delta": optimized_call_delta,
                        "optimized_call_gamma": optimized_call_gamma,
                        "optimized_put_delta": optimized_put_delta,
                        "optimized_put_gamma": optimized_put_gamma,
                        "optimized_call_premium": optimized_call_premium,
                        "optimized_put_premium": optimized_put_premium,
                        "optimized_portfolio_delta": optimized_portfolio_delta,
                        "optimized_portfolio_gamma": optimized_portfolio_gamma,
                        "optimized_portfolio_premium": optimized_portfolio_premium,
                        "gamma_scaler": gamma_scaler,
                    }

                    file_name = f"{save_dir}\\{index}_{timestamp}_{gamma_scaler}.pkl"
                    make_directory_if_needed(file_name)
                    with open(file_name, "wb") as f:
                        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
                    mega_list.append(data)

            except Exception as e:
                logger.error(f"Error for {index} and {timestamp}: {e}")
                continue

    return mega_list
