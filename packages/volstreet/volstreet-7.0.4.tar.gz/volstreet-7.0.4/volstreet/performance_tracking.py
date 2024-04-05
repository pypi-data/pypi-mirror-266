import os
import json
import pandas as pd
import re
from volstreet.database_connection import BaseDBConnection
from volstreet.vslogging.parsing import parse_jsonl_file


class PerformanceTracker(BaseDBConnection):
    def __init__(self, *credentials):
        super().__init__(*credentials)

    @property
    def prefix(self):
        return "TRADE_DB"


def process_delta_file(data: list[dict]) -> float:
    return sum([entry["pnl"] for entry in data if "exit_time" in entry])


def return_strategy_data(user: str, strat: str) -> pd.DataFrame:
    # Add user to path
    user_files = os.listdir(user)
    strangle_files = [file for file in user_files if strat in file]

    strat_data = pd.DataFrame()
    for file in strangle_files:
        with open(f"{user}\\{file}", "r") as f:
            data = json.load(f)
        d = pd.DataFrame(data)
        if "trend" in strat:
            matches = re.findall(r"([A-Z0-9a-z]+)", file)
            index = [*filter(lambda x: "NIFTY" in x, matches)][0]
            d["Index"] = index
        strat_data = pd.concat([strat_data, d])

    return strat_data


def track_order_placement_time(path: str) -> pd.DataFrame:
    times = pd.DataFrame()

    for log in os.listdir(path):
        df = parse_jsonl_file(f"{path}\\{log}")
        orders = df[df.message.str.contains("Time taken for place_order_params")]
        _times = orders.message.apply(
            lambda x: float(x.split(": ")[1].split(" seconds")[0])
        ).to_frame()
        _times["timestamp"] = pd.to_datetime(orders.timestamp)
        times = pd.concat([times, _times])

    return times
