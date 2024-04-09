import json
import pandas as pd
from volstreet.config import logger


def parse_jsonl_file(file_path: str) -> pd.DataFrame:
    with open(file_path, "r") as f:
        lines = f.readlines()
    lines = [line.rstrip("\n") for line in lines]
    logs = []
    for i, line in enumerate(lines):
        try:
            j = json.loads(line)
            logs.append(j)
        except json.JSONDecodeError:
            logger.error(
                f"Error in line number {i} of file {file_path}." " Skipping this line."
            )
    log_df = pd.DataFrame(logs)
    return log_df
