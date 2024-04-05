import pandas as pd
import numpy as np
from enum import Enum
from sqlalchemy import text
from datetime import datetime, timedelta, time
from attrs import define, field
from volstreet.datamodule.eod_client import EODClient
from volstreet.utils import find_strike, make_directory_if_needed
from volstreet.blackscholes import call, put, calculate_strangle_iv
from volstreet.backtests.database import DataBaseConnection
from volstreet.backtests.underlying_info import UnderlyingInfo
from volstreet.backtests.tools import (
    nav_drawdown_analyser,
    prepare_index_prices_for_backtest,
)
from volstreet.vectorized_blackscholes import add_greeks_to_dataframe


class Signal(Enum):
    BUY = 1
    SELL = -1


@define
class BackTester(DataBaseConnection):
    eod_client: EODClient = field(factory=EODClient, repr=False)
    index_instances: dict = field(factory=dict, init=False, repr=False)

    def __attrs_post_init__(self):
        self._initialize_index_instances()
        super().__attrs_post_init__()

    def _initialize_index_instances(self):
        self.index_instances.update(
            {
                "NIFTY": UnderlyingInfo("NIFTY"),
                "BANKNIFTY": UnderlyingInfo("BANKNIFTY"),
                "FINNIFTY": UnderlyingInfo("FINNIFTY"),
                "MIDCPNIFTY": UnderlyingInfo("MIDCPNIFTY"),
            }
        )

    def fetch_nearest_expiry_from_date(
        self,
        index: str,
        date_time: str | datetime,
        threshold_days: int = 0,
        n_exp: int = 1,
    ) -> pd.DatetimeIndex | pd.Timestamp | None:
        if isinstance(date_time, str):
            date_time = pd.to_datetime(date_time)

        filtered_dates = self.index_instances[index].expiry_dates
        delta_days = (filtered_dates - date_time.replace(hour=00, minute=00)).days
        valid_indices = np.where(
            delta_days < threshold_days, np.inf, delta_days
        ).argsort()[:n_exp]

        nearest_exp_dates = filtered_dates[valid_indices].sort_values()

        if n_exp == 1:
            return nearest_exp_dates[0] if len(nearest_exp_dates) != 0 else None
        else:
            return nearest_exp_dates

    def historic_time_to_expiry(
        self,
        index: str,
        date_time: str | datetime,
        in_days: bool = False,
        threshold_days: int = 0,
        n_exp: int = 1,
    ) -> float | np.ndarray | None:
        """Return time left to expiry"""
        if in_days:
            multiplier = 365
            rounding = 0
        else:
            multiplier = 1
            rounding = 5

        if isinstance(date_time, str):
            date_time = pd.to_datetime(date_time)

        expiry = self.fetch_nearest_expiry_from_date(
            index=index,
            date_time=date_time.replace(hour=00, minute=00),
            threshold_days=threshold_days,
            n_exp=n_exp,
        )

        if expiry is None:
            return None
        else:
            time_left = (expiry - date_time) / timedelta(days=365)

        # Multiplying by the multiplier and rounding
        time_left = np.round(time_left * multiplier, rounding)
        return time_left

    @staticmethod
    def _melt_skeleton(df: pd.DataFrame) -> pd.DataFrame:
        # Step 1: Create a new DataFrame with square-up information if it exists

        if "square_up_timestamp" not in df.columns:
            concat_df = df[["timestamp", "expiry", "call_strike", "put_strike"]].copy()
        else:
            square_up_df = df[
                [
                    "square_up_timestamp",
                    "square_up_expiry",
                    "square_up_call_strike",
                    "square_up_put_strike",
                ]
            ].copy()

            # Step 2: Rename columns to match the original DataFrame
            square_up_df.rename(
                columns={
                    "square_up_timestamp": "timestamp",
                    "square_up_expiry": "expiry",
                    "square_up_call_strike": "call_strike",
                    "square_up_put_strike": "put_strike",
                },
                inplace=True,
            )

            # Concatenate the DataFrames
            concat_df = pd.concat([df, square_up_df])

        # Remove rows where any key columns are NaN
        concat_df.dropna(
            subset=["timestamp", "expiry", "call_strike", "put_strike"], inplace=True
        )

        # Step 4: Combine 'call_strike' and 'put_strike' into a single tuple column
        concat_df["strikes"] = list(
            zip(concat_df["call_strike"], concat_df["put_strike"])
        )

        # Drop the individual 'call_strike' and 'put_strike' columns as they are now redundant
        concat_df.drop(["call_strike", "put_strike"], axis=1, inplace=True)

        # Sort the DataFrame by timestamp for better readability and analysis
        concat_df.sort_values(by=["timestamp"], inplace=True)

        # Reset the index after sorting
        concat_df.reset_index(drop=True, inplace=True)

        return concat_df[["timestamp", "expiry", "strikes"]]

    def _fetch_option_prices_from_skeleton(
        self,
        skeleton: pd.DataFrame,
        index: str,
    ) -> pd.DataFrame:
        df = self._melt_skeleton(skeleton)

        query = self.generate_query_for_option_prices_df(
            index=index,
            df=df,
        )

        option_prices = self.fetch_option_prices(query)

        option_prices = (
            option_prices.groupby(["timestamp", "expiry", "strike", "option_type"])
            .close.first()
            .unstack(level="option_type")
            .reset_index()
        )

        return option_prices

    def get_option_prices_from_df(
        self,
        underlying: str | UnderlyingInfo,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        underlying = underlying if isinstance(underlying, str) else underlying.name
        cte_entries = generate_cte_entries_from_df(dataframe)
        query = convert_cte_entries_to_query(cte_entries, underlying)
        option_prices = self.fetch_option_prices(query)
        return option_prices

    def _build_option_chain_skeleton(
        self,
        underlying: UnderlyingInfo,
        index_prices: pd.DataFrame,
        num_strikes: int = 3,
        num_exp: int = 1,
        threshold_days_expiry: int | float = 1,
    ) -> pd.DataFrame:
        """Supply a dataframe with a datetime index and a open column."""

        df = index_prices.copy()
        if "timestamp" not in df.columns:
            # assert that the index is a datetime index
            assert isinstance(df.index, pd.DatetimeIndex)
            df.index.name = "timestamp"
            df = df.reset_index()

        # Finding ATM strike and renaming the columns
        df["atm_strike"] = df.open.apply(lambda x: find_strike(x, underlying.base))

        # Adding expiry
        df["expiry"] = df.timestamp.apply(
            lambda x: self.fetch_nearest_expiry_from_date(
                index=underlying.name,
                date_time=x,
                threshold_days=threshold_days_expiry,
                n_exp=num_exp,
            )
        )

        df["time_to_expiry"] = df.apply(
            lambda row: self.historic_time_to_expiry(
                index=underlying.name,
                date_time=row.timestamp,
                threshold_days=threshold_days_expiry,
                n_exp=num_exp,
            ),
            axis=1,
        )

        max_offset = (num_strikes - 1) // 2
        strike_offsets = [
            underlying.base * i for i in range(-max_offset, max_offset + 1)
        ]

        # Exploding the dataframe to include a list of closest strikes
        df["strike"] = df["atm_strike"].apply(
            lambda x: [x + offset for offset in strike_offsets]
        )

        df_exploded = df.explode("strike", ignore_index=True).explode(
            ["expiry", "time_to_expiry"], ignore_index=True
        )

        df_exploded["call_strike"] = df_exploded.strike

        df_exploded["put_strike"] = df_exploded.strike

        return df_exploded.astype(
            {
                "strike": "int",
                "call_strike": "int",
                "put_strike": "int",
                "time_to_expiry": "float",
            }
        )

    def build_option_chain(
        self,
        index: UnderlyingInfo,
        from_timestamp: str | datetime,
        to_timestamp: str | datetime,
        num_strikes: int = 3,
        num_exp: int = 1,
        threshold_days_expiry: int | float = 1,
        add_greeks: bool = False,
    ) -> pd.DataFrame:
        """Builds an option chain at a certain minute on a certain day."""

        index_prices = self.fetch_index_prices(
            index.name, from_timestamp=from_timestamp, to_timestamp=to_timestamp
        )
        index_prices = index_prices[["timestamp", "open"]]
        skeleton = self._build_option_chain_skeleton(
            index, index_prices, num_strikes, num_exp, threshold_days_expiry
        )
        option_prices = self.get_option_prices_from_df(index, skeleton)

        # Merging the two dataframes on the closest strikes and nearest expiry
        merged = pd.merge(
            skeleton,
            option_prices,
            on=["timestamp", "strike", "expiry"],
            how="left",
        )
        merged = merged[
            merged["timestamp"].dt.time != datetime.strptime("09:15", "%H:%M").time()
        ]

        if add_greeks:
            merged["r"] = calculate_moving_interest_rate(
                merged, "strike", "call_price", "put_price"
            )
            merged = add_greeks_to_dataframe(merged, r_col="r", use_one_iv=False)

        return merged

    def build_trade_df(
        self,
        underlying: UnderlyingInfo,
        trade_entry_time: tuple[int, int],
        square_up_time_delta: timedelta,
        threshold_days_expiry: (
            int | float
        ) = 1.1,  # A decimal on purpose because last timestamp in the database is 15:29
        strike_offset: float = 1,
        call_strike_offset: float | None = None,
        put_strike_offset: float | None = None,
        from_date: str | datetime = "2019-04-01",
        to_date: str | datetime = None,
        only_expiry: bool = False,
    ):
        """This function is intended to replace the overnight and quick straddle skeleton"""

        underlying_prices_full = self.fetch_index_prices(
            underlying.name, from_timestamp=from_date, to_timestamp=to_date
        )
        underlying_prices_full = underlying_prices_full.set_index("timestamp")
        if only_expiry:
            expiry_dates_set = set(underlying.expiry_dates.date)
            underlying_prices_full = underlying_prices_full[
                pd.Series(underlying_prices_full.index.date)
                .isin(expiry_dates_set)
                .values
            ]
        trade_entry_time = time(*trade_entry_time)
        underlying_prices = underlying_prices_full.between_time(
            trade_entry_time, trade_entry_time
        ).copy()
        if square_up_time_delta > timedelta(days=1):  # todo: simplify this
            if square_up_time_delta != timedelta(days=7):
                raise ValueError(
                    "When square_up_time_delta is greater than 1 day, it must be 7 days."
                )
            underlying_prices = underlying_prices.loc[
                [
                    _date in underlying.expiry_dates.date
                    for _date in underlying_prices.index.date
                ]
            ]  # Expiry to expiry

        # Crucial step
        underlying_prices["trade_id"] = range(len(underlying_prices))

        df = add_strikes(
            underlying,
            underlying_prices,
            strike_offset,
            call_strike_offset,
            put_strike_offset,
        )

        df.reset_index(inplace=True)

        # Add expiry
        df["expiry"] = df.timestamp.apply(
            lambda x: self.fetch_nearest_expiry_from_date(
                index=underlying.name,
                date_time=x,
                threshold_days=threshold_days_expiry,
                n_exp=1,
            )
        )

        # Add time to expiry
        df["time_to_expiry"] = df.apply(
            lambda row: self.historic_time_to_expiry(
                index=underlying.name,
                date_time=row.timestamp,
                threshold_days=threshold_days_expiry,
                n_exp=1,
            ),
            axis=1,
        )

        # Square up info

        # Square up timestamp
        if square_up_time_delta >= timedelta(days=1):
            df["square_up_timestamp"] = df.timestamp.shift(-1)

        else:
            df["square_up_timestamp"] = df.timestamp + square_up_time_delta

        df["spot_exit"] = df.square_up_timestamp.apply(
            lambda x: underlying_prices_full.open.get(x, np.nan)
        )

        # Square up columns
        df["square_up_expiry"] = df.expiry
        df["square_up_call_strike"] = df.call_strike
        df["square_up_put_strike"] = df.put_strike

        # Square-up time to expiry
        df["square_up_time_to_expiry"] = df.apply(
            lambda row: self.historic_time_to_expiry(
                index=underlying.name,
                date_time=row.square_up_timestamp,
                threshold_days=threshold_days_expiry - square_up_time_delta.days,
                n_exp=1,
            ),
            axis=1,
        )
        df = df.dropna()
        return df

    def backtest_trades(
        self,
        underlying: UnderlyingInfo,
        action: Signal,
        trade_entry_time: tuple[int, int],
        square_up_time_delta: timedelta,
        *args,
        **kwargs,
    ):
        f"""This function is intended to replace the overnight and quick straddle backtest
        For details on the arguments, see the build_trade_df function"""

        trades = self.build_trade_df(
            underlying, trade_entry_time, square_up_time_delta, *args, **kwargs
        )

        trades.drop(columns=["high", "low", "close"], inplace=True)

        # Generate CTE entries and convert to query
        cte_entries = generate_cte_entries_from_df(trades)
        query = convert_cte_entries_to_query(cte_entries, underlying.name)

        # Fetch, rearrange, and rename option prices
        option_prices = self.fetch_option_prices(query).reset_index()

        # Populate trades with prices
        trades_with_prices = populate_with_option_prices(
            trades, option_prices, has_square_up=True
        )

        trades = trades_with_prices.merge(
            trades[
                [
                    "trade_id",
                    "underlying",
                    "open",
                    "spot_exit",
                    "time_to_expiry",
                    "square_up_time_to_expiry",
                ]
            ],
            on="trade_id",
        )

        trades = trades.rename(columns={"open": "spot_entry"})

        # Calculating the pct change in price
        trades["pct_change"] = (trades.spot_exit / trades.spot_entry - 1) * 100

        # Calculating the initial and square up premiums
        trades["entry_premium"] = trades.call_price + trades.put_price
        trades["square_up_premium"] = (
            trades.square_up_call_price + trades.square_up_put_price
        )

        # Calculating profit
        trades["profit"] = (
            trades.square_up_premium - trades.entry_premium
        ) * action.value

        # Calculating the profit percentage
        trades["profit_percentage"] = (trades.profit / trades.spot_entry) * 100

        trades = trades.dropna()

        trades.set_index("timestamp", inplace=True)

        trades.index = pd.to_datetime(trades.index).date

        trades = nav_drawdown_analyser(
            trades, column_to_convert="profit_percentage", profit_in_pct=True
        )

        priority = [
            "spot_entry",
            "spot_exit",
            "pct_change",
            "profit",
            "profit_percentage",
            "rolling_cagr",
            "drawdown",
        ]

        trades = trades[
            priority + [col for col in trades.columns if col not in priority]
        ]

        return trades

    @staticmethod
    def prepare_option_chain_for_vol_surface(data_frame: pd.DataFrame) -> pd.DataFrame:
        def find_atm_iv(group):
            avg_iv = group[(group.strike == group.atm_strike)].avg_iv.values
            return avg_iv[0] if len(avg_iv) > 0 else np.nan

        data_frame = data_frame.dropna().copy()
        data_frame.rename(
            columns={"open": "spot", "CE": "call_price", "PE": "put_price"},
            inplace=True,
        )

        # Removing entries where the option price is less than the intrinsic value
        intrinsic_value = abs(data_frame["strike"] - data_frame["spot"])
        valid_entries = np.where(
            data_frame["spot"] > data_frame["strike"],
            data_frame["call_price"] > intrinsic_value,
            data_frame["put_price"] > intrinsic_value,
        )
        data_frame = data_frame[valid_entries]

        # Adding ivs
        data_frame[["call_iv", "put_iv", "avg_iv"]] = (
            data_frame.apply(
                lambda row: calculate_strangle_iv(
                    row.call_price,
                    row.put_price,
                    row.spot,
                    strike=row.strike,
                    time_left=row.time_to_expiry,
                ),
                axis=1,
            )
            .apply(pd.Series)
            .values
        )

        # Adding atm_iv for the timestamp
        atm_iv_for_timestamp = data_frame.groupby(["timestamp", "expiry"]).apply(
            find_atm_iv
        )
        timestamp_expiry_pairs = pd.MultiIndex.from_arrays(
            [data_frame.timestamp, data_frame.expiry]
        )
        data_frame["atm_iv"] = atm_iv_for_timestamp.loc[timestamp_expiry_pairs].values

        # Adding the distance feature
        data_frame["distance"] = data_frame["strike"] / data_frame["spot"] - 1

        # Adding the iv multiple feature
        data_frame["iv_multiple"] = data_frame["avg_iv"] / data_frame["atm_iv"]

        # Adding the distance squared feature
        data_frame["distance_squared"] = data_frame["distance"] ** 2

        # Adding the money-ness feature (ratio of spot price to strike price)
        data_frame["money_ness"] = data_frame["spot"] / data_frame["strike"]

        # Adding the interaction term between distance squared and time to expiry
        data_frame["distance_time_interaction"] = (
            data_frame["distance_squared"] * data_frame["time_to_expiry"]
        )

        return data_frame

    @staticmethod
    def backtest_trades_wip(
        group: pd.DataFrame,
        trigger_timestamps: pd.Series,
        action: int,
        target_pct: float | None = None,
        sl_pct: float = 0.003,
    ):
        # Work in progress
        """The group is a dataframe of the OHLC data for a single day."""

        # Filter trigger timestamps to the same date as the group
        trigger_timestamps = trigger_timestamps[
            trigger_timestamps.index.date == group.index[0].date()
        ]

        all_entries_in_group = []

        for trigger_time in trigger_timestamps.index:
            trade_info_dict = {"trigger_time": trigger_time}
            try:
                entry_price = group.loc[trigger_time, "close"]
            except KeyError:
                # If the trigger time is not in the group, skip it
                continue

            # Setting SL and TP prices
            sl_price = entry_price * (1 - sl_pct * action)
            target_price = (
                entry_price * (1 + target_pct * action)
                if target_pct
                else (np.inf if action == 1 else 0)
            )

            trade_info_dict.update(
                {
                    "trigger_price": entry_price,
                    "action": "BUY" if action == 1 else "SELL",
                    "stop_loss_price": sl_price,
                }
            )

            future_df = group.loc[trigger_time + timedelta(minutes=1) :]

            # Check for SL and TP hit using vectorized operations
            sl_hit = future_df.loc[
                (action == 1) & (future_df["low"] <= sl_price)
                | (action == -1) & (future_df["high"] >= sl_price)
            ]
            tp_hit = future_df.loc[
                (action == 1) & (future_df["high"] >= target_price)
                | (action == -1) & (future_df["low"] <= target_price)
            ]

            # Determine exit condition
            if not sl_hit.empty and (tp_hit.empty or sl_hit.index[0] < tp_hit.index[0]):
                # Stop-loss hit first
                trade_info_dict["returns"] = -sl_pct
                trade_info_dict["stop_loss_time"] = sl_hit.index[0]
                trade_info_dict["target_time"] = np.nan
            elif not tp_hit.empty:
                # Take-profit hit first or end-of-day exit
                trade_info_dict["returns"] = (target_price / entry_price - 1) * action
                trade_info_dict["target_time"] = tp_hit.index[0]
                trade_info_dict["target_price"] = future_df.loc[
                    tp_hit.index[0], "close"
                ]
                trade_info_dict["stop_loss_time"] = np.nan
            else:
                # Neither SL or TP hit, exit at the end of the day
                trade_info_dict["returns"] = (
                    future_df.iloc[-1]["close"] / entry_price - 1
                ) * action
                trade_info_dict["target_time"] = future_df.index[-1]
                trade_info_dict["target_price"] = future_df.iloc[-1]["close"]
                trade_info_dict["stop_loss_time"] = np.nan

            all_entries_in_group.append(trade_info_dict)

        all_entries_in_group = pd.DataFrame(all_entries_in_group)
        if all_entries_in_group.empty:
            return all_entries_in_group
        all_entries_in_group["exit_time"] = all_entries_in_group[
            ["target_time", "stop_loss_time"]
        ].max(axis=1)

        return all_entries_in_group

    def backtest_intraday_trend(
        self,
        underlying: str,
        from_date: datetime | str = None,
        vix_df=None,
        open_nth=0,
        beta=1,
        fixed_trend_threshold=None,
        stop_loss=0.3,
        max_entries=3,
        rolling_days=60,
        randomize=False,
    ):
        index_prices = self.fetch_index_prices(underlying, from_timestamp=from_date)
        index_prices = prepare_index_prices_for_backtest(index_prices)

        if vix_df is None:
            vix_df = self.eod_client.get_data("VIX", return_columns=["open", "close"])

        vix = vix_df.copy()
        vix["open"] = vix["open"] * beta
        vix["close"] = vix["close"] * beta

        open_prices = (
            index_prices.groupby(index_prices["timestamp"].dt.date)
            .apply(lambda x: x.iloc[open_nth])
            .open.to_frame()
        )
        open_data = open_prices.merge(
            vix["open"].to_frame(),
            left_index=True,
            right_index=True,
            suffixes=("", "_vix"),
        )

        if randomize:
            fixed_trend_threshold = 0.0001

        open_data["threshold_movement"] = fixed_trend_threshold or (
            open_data["open_vix"] / 48
        )
        open_data["upper_bound"] = open_data["open"] * (
            1 + open_data["threshold_movement"] / 100
        )
        open_data["lower_bound"] = open_data["open"] * (
            1 - open_data["threshold_movement"] / 100
        )
        open_data["day_close"] = index_prices.groupby(
            index_prices["timestamp"].dt.date
        ).close.last()

        daily_minute_vols = index_prices.groupby(
            index_prices["timestamp"].dt.date
        ).apply(lambda x: x["close"].pct_change().abs().mean() * 100)

        daily_minute_vols_rolling = daily_minute_vols.rolling(
            rolling_days, min_periods=1
        ).mean()

        daily_open_to_close_trends = index_prices.open.groupby(
            index_prices["timestamp"].dt.date
        ).apply(lambda x: (x.iloc[-1] / x.iloc[0] - 1) * 100)

        daily_open_to_close_trends_rolling = (
            daily_open_to_close_trends.abs().rolling(rolling_days, min_periods=1).mean()
        )

        rolling_ratio = daily_open_to_close_trends_rolling / daily_minute_vols_rolling

        open_data.columns = [
            "day_open",
            "open_vix",
            "threshold_movement",
            "upper_bound",
            "lower_bound",
            "day_close",
        ]
        index_prices[
            [
                "day_open",
                "open_vix",
                "threshold_movement",
                "upper_bound",
                "lower_bound",
                "day_close",
            ]
        ] = open_data.loc[index_prices["timestamp"].dt.date].values
        index_prices["change_from_open"] = (
            (index_prices["close"] / index_prices["day_open"]) - 1
        ) * 100

        def calculate_daily_trade_data(group):
            """The group is a dataframe"""

            all_entries_in_a_day = {}
            # Find the first index where the absolute price change crosses the threshold
            entry = 1
            while entry <= max_entries:
                # Filtering the dataframe to only include the rows after open nth
                group = group.iloc[open_nth:]
                idx = group[
                    abs(group["change_from_open"]) >= group["threshold_movement"]
                ].first_valid_index()
                if idx is not None:  # if there is a crossing
                    result_dict = {
                        "returns": 0,
                        "trigger_time": np.nan,
                        "trigger_price": np.nan,
                        "trend_direction": np.nan,
                        "stop_loss_price": np.nan,
                        "stop_loss_time": np.nan,
                    }
                    # Record the price and time of crossing the threshold
                    cross_price = group.loc[idx, "close"]
                    cross_time = group.loc[idx, "timestamp"]

                    # Determine the direction of the movement
                    if randomize:
                        direction = np.random.choice([-1, 1])
                    else:
                        direction = np.sign(group.loc[idx, "change_from_open"])

                    # Calculate the stoploss price
                    if stop_loss == "dynamic":
                        # Selecting previous days rolling ratio
                        current_rolling_ratio = rolling_ratio.loc[
                            : cross_time.date()
                        ].iloc[-1]
                        # Calculating the stop_loss pct
                        if current_rolling_ratio > 30:
                            stop_loss_pct = 0.3
                        elif current_rolling_ratio < 10:
                            stop_loss_pct = 0.5
                        else:
                            stop_loss_pct = ((30 - current_rolling_ratio) / 100) + 0.3
                    else:
                        stop_loss_pct = stop_loss

                    stoploss_price = cross_price * (
                        1 - (stop_loss_pct / 100) * direction
                    )
                    result_dict.update(
                        {
                            "trigger_time": cross_time,
                            "trigger_price": cross_price,
                            "trend_direction": direction,
                            "stop_loss_price": stoploss_price,
                        }
                    )
                    future_prices = group.loc[idx:, "close"]

                    if (direction == 1 and future_prices.min() <= stoploss_price) or (
                        direction == -1 and future_prices.max() >= stoploss_price
                    ):  # Stop loss was breached
                        result_dict["returns"] = -stop_loss_pct
                        stoploss_time_idx = (
                            future_prices[
                                future_prices <= stoploss_price
                            ].first_valid_index()
                            if direction == 1
                            else future_prices[
                                future_prices >= stoploss_price
                            ].first_valid_index()
                        )
                        stoploss_time = group.loc[stoploss_time_idx, "timestamp"]
                        result_dict["stop_loss_time"] = stoploss_time
                        all_entries_in_a_day[f"entry_{entry}"] = result_dict
                        group = group.loc[stoploss_time_idx:]
                        entry += 1
                    else:  # Stop loss was not breached
                        if direction == 1:
                            result_dict["returns"] = (
                                (group["close"].iloc[-1] - cross_price) / cross_price
                            ) * 100
                        else:
                            result_dict["returns"] = (
                                (group["close"].iloc[-1] - cross_price) / cross_price
                            ) * -100
                        all_entries_in_a_day[f"entry_{entry}"] = result_dict
                        break
                else:
                    break

            all_entries_in_a_day["total_returns"] = sum(
                [v["returns"] for v in all_entries_in_a_day.values()]
            )
            return all_entries_in_a_day

        # Applying the function to each day's worth of data
        returns = index_prices.groupby(index_prices["timestamp"].dt.date).apply(
            calculate_daily_trade_data
        )
        returns = returns.to_frame()
        returns.index = pd.to_datetime(returns.index)
        returns.columns = ["trade_data"]

        # merging with open_data
        merged = returns.merge(open_data, left_index=True, right_index=True)
        merged["total_returns"] = merged["trade_data"].apply(
            lambda x: x["total_returns"]
        )

        merged["predicted_trend"] = merged.trade_data.apply(
            lambda x: x.get("entry_1", {}).get("trend_direction", None)
        )

        # calculating prediction accuracy
        merged["actual_trend"] = daily_open_to_close_trends.apply(np.sign)
        merged["trend_match"] = merged.predicted_trend == merged.actual_trend
        merged["rolling_prediction_accuracy"] = (
            merged[~pd.isna(merged.predicted_trend)]
            .trend_match.expanding(min_periods=1)
            .mean()
        )
        merged["rolling_prediction_accuracy"] = merged[
            "rolling_prediction_accuracy"
        ].fillna(method="ffill")

        merged = nav_drawdown_analyser(
            merged, column_to_convert="total_returns", profit_in_pct=True
        )

        # calculating the minute vol
        merged["minute_vol"] = daily_minute_vols

        # calculating the open to close trend
        merged["open_to_close_trend"] = daily_open_to_close_trends

        merged["open_to_close_trend_abs"] = merged["open_to_close_trend"].abs()

        # calculating the ratio and rolling mean
        merged["minute_vol_rolling"] = daily_minute_vols_rolling
        merged["open_to_close_trend_rolling"] = daily_open_to_close_trends_rolling
        merged["ratio"] = merged["open_to_close_trend_abs"] / merged["minute_vol"]
        merged["rolling_ratio"] = rolling_ratio

        return merged


def generate_cte_entries(
    dataframe: pd.DataFrame,
    timestamp_col: str,
    strike_col: str,
    expiry_col: str,
    option_type: str,
):
    cte_entries = [
        f"('{row[timestamp_col]}'::timestamp, {row[strike_col]}::integer, '{row[expiry_col]}'::timestamp, '{option_type}'::text)"
        for _, row in dataframe.iterrows()
    ]
    return cte_entries


def generate_cte_entries_from_df(dataframe: pd.DataFrame) -> list:
    cte_entries = []

    for col in dataframe.columns:
        if "strike" in col:
            # Determine option type
            option_type = "CE" if "call" in col else "PE"

            # Determine the correct timestamp and expiry columns
            if "square_up" in col:
                timestamp_col = "square_up_timestamp"
                expiry_col = "square_up_expiry"
            else:
                timestamp_col = "timestamp"
                expiry_col = "expiry"

            # Generate CTE entries
            entries = generate_cte_entries(
                dataframe, timestamp_col, col, expiry_col, option_type
            )
            cte_entries.extend(entries)

    return cte_entries


def convert_cte_entries_to_query(
    cte_entries: list,
    underlying: str,
    cols_to_return: list | None = None,
) -> text:
    if cols_to_return is None:
        cols_to_return = ["timestamp", "expiry", "strike", "option_type", "close"]

    # Join the entries with a comma to create a single string
    cte_entries_str = ", ".join(cte_entries)
    columns_str = ", ".join([f"index_options.{x}" for x in cols_to_return])

    cte = f"WITH conditions AS (SELECT * FROM (VALUES {cte_entries_str}) AS t(timestamp, strike, expiry, option_type))"

    sql_query = text(
        f"""
        {cte}
        SELECT {columns_str}
        FROM index_options
        INNER JOIN conditions
        ON index_options.timestamp = conditions.timestamp 
           AND index_options.expiry = conditions.expiry
           AND index_options.strike = conditions.strike
           AND index_options.option_type = conditions.option_type
        WHERE index_options.underlying = '{underlying}';
        """
    )

    return sql_query


def add_strikes(
    underlying: UnderlyingInfo,
    df: pd.DataFrame,
    strike_offset: float = 0,
    call_strike_offset: float | None = None,
    put_strike_offset: float | None = None,
):
    """Offsets should be of the format of a multiplier. 1.02 for 2%, 0.98 for -2%"""

    df = df.copy()

    # Setting the strikes
    if call_strike_offset is None:
        call_strike_offset = strike_offset
    if put_strike_offset is None:
        put_strike_offset = strike_offset

    df["call_strike"] = df.open.apply(
        lambda x: find_strike(x * call_strike_offset, underlying.base)
    )
    df["put_strike"] = df.open.apply(
        lambda x: find_strike(x * put_strike_offset, underlying.base)
    )

    return df


def melt_frame(
    trade_df: pd.DataFrame,
    leg_type: str,
    square_up: bool,
) -> pd.DataFrame:
    timestamp_col = "square_up_timestamp" if square_up else "timestamp"
    expiry_col = "square_up_expiry" if square_up else "expiry"
    leg_cols = [
        col for col in trade_df.columns if f"{leg_type}" in col and "strike" in col
    ]
    melted_df = pd.melt(
        trade_df,
        ["trade_id", timestamp_col, expiry_col],
        leg_cols,
        f"{leg_type}_leg",
        f"strike",
    )

    melted_df[f"{leg_type}_leg"] = melted_df[f"{leg_type}_leg"].str.replace(
        "_strike", ""
    )

    return melted_df


def merge_with_option_prices(
    melted_df: pd.DataFrame,
    option_prices_df: pd.DataFrame,
    leg_type: str,
    square_up: bool,
) -> pd.DataFrame:
    """
    Merge the melted legs data with the option prices dataframe.
    """
    price_column = f"{leg_type}_price"
    timestamp_col = "square_up_timestamp" if square_up else "timestamp"
    expiry_col = "square_up_expiry" if square_up else "expiry"
    if square_up:
        option_prices_df = option_prices_df.rename(
            columns={
                "timestamp": "square_up_timestamp",
                "expiry": "square_up_expiry",
            }
        )

    return pd.merge(
        melted_df,
        option_prices_df[[timestamp_col, expiry_col, "strike", price_column]],
        left_on=[timestamp_col, expiry_col, "strike"],
        right_on=[timestamp_col, expiry_col, "strike"],
        how="left",
    )


def pivot_frame(
    merged_df: pd.DataFrame,
    leg_type: str,
    square_up: bool,
) -> pd.DataFrame:
    timestamp_col = "square_up_timestamp" if square_up else "timestamp"
    expiry_col = "square_up_expiry" if square_up else "expiry"

    pivoted = merged_df.pivot_table(
        index=["trade_id", timestamp_col, expiry_col],
        columns=f"{leg_type}_leg",
        values=[f"strike", f"{leg_type}_price"],
        aggfunc="first",
    )

    pivoted = pivoted.rename(columns={f"{leg_type}_price": "price"})

    pivoted.columns = [
        f"{col[1]}_{col[0]}" if col[0] in ["strike", "price"] else col[1]
        for col in pivoted.columns.values
    ]
    return pivoted.reset_index()


def add_option_prices_to_leg(trade_df, option_prices_df, leg_type, square_up=False):
    """
    A generalized function to process either trade or square-up legs.
    """
    if square_up:
        trade_df = trade_df.filter(regex="^square_up_|^trade_id$")
    else:
        # Filter out square-up columns
        trade_df = trade_df.filter(regex="^(?!square_up_)")

    legs_df = melt_frame(trade_df, leg_type, square_up)

    merged_df = merge_with_option_prices(legs_df, option_prices_df, leg_type, square_up)

    return pivot_frame(merged_df, leg_type, square_up)


def populate_with_option_prices(trade_df, option_prices_df, has_square_up=False):
    """
    Refactored function to process trade data and merge with option prices. The trade_df should
    contain the following columns:
    - trade_id
    - timestamp
    - expiry
    and call and put strike columns.
    """
    call_trades = add_option_prices_to_leg(trade_df, option_prices_df, "call")
    put_trades = add_option_prices_to_leg(trade_df, option_prices_df, "put")
    merged_trades = call_trades.merge(
        put_trades, on=["trade_id", "timestamp", "expiry"], how="left"
    )
    if not has_square_up:
        return merged_trades

    square_up_call_trades = add_option_prices_to_leg(
        trade_df, option_prices_df, "call", True
    )
    square_up_put_trades = add_option_prices_to_leg(
        trade_df, option_prices_df, "put", True
    )
    square_up_trades = square_up_call_trades.merge(
        square_up_put_trades,
        on=["trade_id", "square_up_timestamp", "square_up_expiry"],
        how="left",
    )
    merged_with_square_up = merged_trades.merge(
        square_up_trades,
        on=["trade_id"],
        how="left",
    )
    return merged_with_square_up


def generate_sample_skeleton(with_square_up=False, hedge_leg=None):
    """For testing purposes only"""
    # Sample data for Skeleton DataFrame
    # Timestamps
    timestamps = pd.date_range(start="2023-01-01", periods=10, freq="D")

    # Expiry dates, let's assume they are weekly
    expiries = pd.date_range(start="2023-01-10", periods=2, freq="W")

    # Strike prices
    call_strikes = np.linspace(100, 110, 3)
    put_strikes = np.linspace(100, 110, 3)

    # Creating a grid of all combinations
    skeleton_data = pd.MultiIndex.from_product(
        [timestamps, expiries, zip(call_strikes, put_strikes)],
        names=["timestamp", "expiry", "strikes"],
    ).to_frame(index=False)
    skeleton_data.drop_duplicates(subset=["timestamp"], inplace=True, keep="first")
    skeleton_data["call_strike"] = skeleton_data["strikes"].apply(lambda x: x[0])
    skeleton_data["put_strike"] = skeleton_data["strikes"].apply(lambda x: x[1])
    skeleton_data.drop(columns=["strikes"], inplace=True)

    if hedge_leg:
        skeleton_data[f"{hedge_leg}_hedge_strike"] = (
            skeleton_data[f"{hedge_leg}_strike"] + 5
            if hedge_leg == "call"
            else skeleton_data[f"{hedge_leg}_strike"] - 5
        )

    if with_square_up:
        # Adding square up columns to the skeleton data
        skeleton_data["square_up_timestamp"] = skeleton_data["timestamp"]
        skeleton_data["square_up_expiry"] = skeleton_data["expiry"].shift(1)
        skeleton_data["square_up_call_strike"] = skeleton_data["call_strike"].shift(1)
        skeleton_data["square_up_put_strike"] = skeleton_data["put_strike"].shift(1)
        if hedge_leg:
            skeleton_data[f"square_up_{hedge_leg}_hedge_strike"] = skeleton_data[
                f"{hedge_leg}_hedge_strike"
            ].shift(1)
    skeleton_data["trade_id"] = range(1, len(skeleton_data) + 1)
    return skeleton_data


def generate_sample_option_prices():
    """For testing purposes only"""
    timestamps = pd.date_range(start="2023-01-01", periods=10, freq="D")

    expiries = pd.date_range(start="2023-01-10", periods=2, freq="W")

    option_df_strikes = np.arange(90, 150, 5)
    option_prices_data = pd.MultiIndex.from_product(
        [timestamps, expiries, option_df_strikes],
        names=["timestamp", "expiry", "strike"],
    ).to_frame(index=False)
    option_prices_data["call_price"] = np.random.uniform(5, 15, len(option_prices_data))
    option_prices_data["put_price"] = np.random.uniform(3, 10, len(option_prices_data))

    return option_prices_data


def calculate_atm_ivs(
    backtester: BackTester,
    underlying: UnderlyingInfo,
    from_timestamp: str | datetime,
    to_timestamp: str | datetime,
) -> pd.DataFrame:
    def _calculate_averages(group):
        # Calculate the average 'r', 'call_iv', and 'put_iv', ignoring missing values
        avg_r = group["r"].mean(skipna=True)
        avg_call_iv = group["call_iv"].mean(skipna=True)
        avg_put_iv = group["put_iv"].mean(skipna=True)

        # Return a Series with the calculated averages
        day_averages = pd.Series(
            {
                "r": avg_r,
                "call_iv": avg_call_iv,
                "put_iv": avg_put_iv,
            }
        )

        day_averages = day_averages.interpolate(method="linear")
        day_averages = day_averages.fillna(method="ffill").fillna(method="bfill")

        return day_averages

    option_chain = backtester.build_option_chain(
        underlying, from_timestamp, to_timestamp
    )
    option_chain["r"] = calculate_moving_interest_rate(option_chain)
    df = add_greeks_to_dataframe(option_chain, r_col="r")
    averages = df.groupby(["timestamp", "expiry"]).apply(_calculate_averages)
    averages["atm_iv"] = np.mean(averages[["call_iv", "put_iv"]], axis=1)
    averages["underlying"] = underlying.name
    averages = averages.reset_index()
    averages = averages.drop(columns=["call_iv", "put_iv"])
    return averages


def store_atm_ivs(*args, **kwargs):
    ivs = calculate_atm_ivs(*args, **kwargs)
    underlying = ivs.underlying[0]
    from_timestamp = ivs.timestamp.min()
    to_timestamp = ivs.timestamp.max()
    directory = f"data\\atm_ivs\\{underlying}"
    file_name = f"{underlying}_atm_ivs_{from_timestamp.strftime('%Y-%m-%d')}_{to_timestamp.strftime('%Y-%m-%d')}.csv"
    full_path = f"{directory}\\{file_name}"
    make_directory_if_needed(full_path)
    ivs.to_csv(full_path)


def calculate_moving_interest_rate(
    dataframe: pd.DataFrame,
    strike_col: str = "strike",
    call_price_col: str = "call_price",
    put_price_col: str = "put_price",
) -> np.ndarray:
    dataframe = dataframe.copy()

    dataframe["synthetic_rate"] = (
        dataframe[strike_col] + dataframe[call_price_col] - dataframe[put_price_col]
    )
    dataframe["r"] = ((dataframe["synthetic_rate"] / dataframe["open"]) - 1) * (
        1 / dataframe["time_to_expiry"]
    )

    # Removing infinities
    r = np.where(
        dataframe["r"] == np.inf,
        50,
        np.where(dataframe["r"] == -np.inf, -50, dataframe["r"]),
    )

    return r.astype(float)


def calculate_intrinsic_value(df, open_col, strike_col, is_call=True):
    """Calculate the intrinsic value for options."""
    if is_call:
        return np.maximum(0, df[open_col] - df[strike_col])
    else:
        return np.maximum(0, df[strike_col] - df[open_col])


def calculate_option_price(
    df, open_col, strike_col, time_to_expiry_col, iv_col, is_call=True
):
    """Calculate the option price using a model (e.g., Black-Scholes)."""
    if is_call:
        return call(
            df[open_col], df[strike_col], df[time_to_expiry_col], 0.05, df[iv_col]
        )
    else:
        return put(
            df[open_col], df[strike_col], df[time_to_expiry_col], 0.05, df[iv_col]
        )


def fill_option_prices(
    df, price_col, strike_col, time_to_expiry_col, iv_col, open_col, is_call=True
):
    """Fill missing option prices in the DataFrame."""
    short_expiry = df[time_to_expiry_col] < (0.5 / (364 * 24))
    intrinsic = calculate_intrinsic_value(df, open_col, strike_col, is_call)
    option_price = calculate_option_price(
        df, open_col, strike_col, time_to_expiry_col, iv_col, is_call
    )

    df[price_col] = np.where(
        df[price_col].isna() & short_expiry,
        intrinsic,
        np.where(df[price_col].isna(), option_price, df[price_col]),
    )
    return df


def fill_missing_option_prices(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Fill regular call and put prices
    df = fill_option_prices(
        df, "call_price", "call_strike", "time_to_expiry", "iv", "open", is_call=True
    )
    df = fill_option_prices(
        df, "put_price", "put_strike", "time_to_expiry", "iv", "open", is_call=False
    )

    # Fill square up call and put prices
    df = fill_option_prices(
        df,
        "square_up_call_price",
        "square_up_call_strike",
        "square_up_time_to_expiry",
        "iv",
        "open",
        is_call=True,
    )
    df = fill_option_prices(
        df,
        "square_up_put_price",
        "square_up_put_strike",
        "square_up_time_to_expiry",
        "iv",
        "open",
        is_call=False,
    )

    return df
