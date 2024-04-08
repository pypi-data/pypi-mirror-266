import pandas as pd
import os
import ftplib
import warnings
from datetime import datetime, timedelta
import re
from sqlalchemy import create_engine
import zipfile
from volstreet.config import logger


class FTPConnection:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.ftp = None

    def __enter__(self):
        self.ftp = ftplib.FTP(self.host)
        self.ftp.login(self.username, self.password)
        return self.ftp

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ftp.quit()


def find_zip_files(ftp, current_directory, zip_files=None):
    if zip_files is None:
        zip_files = []

    original_directory = ftp.pwd()
    try:
        ftp.cwd(current_directory)
        items = ftp.nlst()

        for item in items:
            if item.lower().endswith(".zip"):
                absolute_path = f"{ftp.pwd()}/{item}"
                zip_files.append(absolute_path)
            else:
                try:
                    ftp.cwd(item)
                    find_zip_files(ftp, "", zip_files)
                    ftp.cwd("..")
                except ftplib.error_perm:
                    continue
    finally:
        ftp.cwd(original_directory)

    return zip_files


# Cleaning the csv files
def parse_option_string_with_digits(option_string: str) -> dict[str, str]:
    """
    Parse the given option string to identify the underlying asset, expiry date, strike price, and option type.
    This version accommodates underlying symbols that may contain digits.

    Parameters:
        option_string (str): The option string to be parsed.

    Returns:
        dict[str, str]: A dictionary containing the parsed information.
    """
    # Using a non-greedy match for the underlying and a greedy match for the strike
    pattern = r"(.+?)(\d{2}[a-zA-Z]{3}\d{2})(\d+)([a-zA-Z]+)"
    match = re.match(pattern, option_string)

    if match:
        groups = match.groups()
        return {
            "underlying": groups[0],
            "expiry": groups[1],
            "strike": groups[2],
            "option_type": groups[3].upper(),
        }
    else:
        print(f"ERROR IN OPTION STRING {option_string}")
        return {"error": "Invalid option string format"}


def round_to_next_minute(time_str):
    """
    Round a time string (HH:MM:SS) to the next minute.
    """
    time_obj = datetime.strptime(time_str, "%H:%M:%S")
    # Add enough seconds to round to the next minute
    rounded_time_obj = time_obj + timedelta(seconds=(60 - time_obj.second))
    rounded_time_str = rounded_time_obj.strftime("%H:%M:%S")
    return rounded_time_str


def process_daily_prices(df):
    # Suppress the specific UserWarning
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        # Filtering out tickers that end in either -I.NFO or -II.NFO
        df = df[~df.Ticker.str.contains(r"(I|II|III|FUT).NFO$")]

        # Filtering for only indices
        df = df[df.Ticker.str.contains(r"^(.*?)NIFTY")]

    df[["underlying", "expiry", "strike", "option_type"]] = (
        df.Ticker.apply(parse_option_string_with_digits).apply(pd.Series).values
    )
    df.strike = df.strike.apply(int)
    df["Time"] = df["Time"].apply(round_to_next_minute)
    df["Date"] = pd.to_datetime(df.Date, dayfirst=True)
    df["Time"] = pd.to_timedelta(df.Time)
    df["timestamp"] = df["Date"] + df["Time"]
    df = df.drop(columns=["Ticker", "Date", "Time"])
    df = df[
        [
            "timestamp",
            "underlying",
            "expiry",
            "strike",
            "option_type",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "Open Interest",
        ]
    ]
    df.drop(columns=["Volume", "Open Interest"], inplace=True)

    df.columns = [name.lower() for name in df.columns]

    df["expiry"] = pd.to_datetime(df["expiry"], format="%d%b%y")
    df["expiry"] = df["expiry"] + timedelta(hours=15, minutes=30)

    return df


def extract_zipped_files(directory, remove: bool = False):
    for filename in os.listdir(directory):
        if filename.endswith(".zip"):
            # Construct the full path to the ZIP file
            zip_path = os.path.join(directory, filename)

            # Open the ZIP file
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(directory)

            if remove:
                # Remove the ZIP file
                os.remove(zip_path)


def process_file(file_path):
    file_name = os.path.basename(file_path).split("_")[2]
    existing_files = os.listdir(os.path.join("option_prices", "all"))
    if f"{file_name}" in map(
        lambda x: os.path.basename(x), existing_files
    ):  # If the file already exists, skip it
        return
    destination = os.path.join("option_prices", "all", file_name)
    df = pd.read_csv(file_path)
    df = process_daily_prices(df)
    df.to_csv(destination, index=False)


def process_folder(folder_path):
    for day in os.listdir(folder_path):
        day_file = os.path.join(folder_path, day)
        process_file(day_file)


def process_year(year_path):
    for month in os.listdir(year_path):
        month_folder = os.path.join(year_path, month)
        process_folder(month_folder)


def prepare_option_prices(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], dayfirst=True)
    df.sort_values(["timestamp", "underlying", "strike", "option_type"], inplace=True)
    return df


def insert_csv_to_db(csv_file: str, engine_url: str) -> None:
    engine = create_engine(engine_url)

    # Read the CSV file
    df = pd.read_csv(csv_file)
    df.drop(columns=["volume", "open_interest"], inplace=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["expiry"] = pd.to_datetime(df["expiry"], format="%d%b%y")
    df["expiry"] = df["expiry"] + timedelta(hours=15, minutes=30)

    df.to_sql("index_options", con=engine, if_exists="append", index=False)

    logger.info(f"Inserted {csv_file} into the database")


def get_new_daily_data(
    database_connection, remote_base_directory, local_base_directory
):
    host = os.getenv("GDFL_FTP_HOST")
    username = os.getenv("GDFL_FTP_USER")
    password = os.getenv("GDFL_FTP_PASS")

    dates_present = database_connection.execute_query(
        "SELECT DISTINCT DATE(timestamp) FROM index_options"
    )
    dates_present = [date[0] for date in dates_present]

    new_files = []  # List to keep track of new files
    for attempt in range(3):
        try:
            with FTPConnection(host, username, password) as ftp:
                zip_files = find_zip_files(ftp, remote_base_directory)
                dates_of_files = [
                    file.split("_")[4].rstrip(".zip") for file in zip_files
                ]
                dates_of_files = [
                    datetime.strptime(date, "%d%m%Y").date() for date in dates_of_files
                ]
                for file, date in zip(zip_files, dates_of_files):
                    zip_name = file.split("/")[-1]
                    if date not in dates_present:
                        logger.info(f"Downloading {zip_name}")
                        local_path = os.path.join(local_base_directory, zip_name)
                        with open(local_path, "wb") as local_file:
                            ftp.retrbinary("RETR " + file, local_file.write)
                        new_files.append(zip_name)  # Add the new file to the list
            return new_files
        except ftplib.error_temp as e:
            logger.warning(f"Error in downloading data from GDFL: {e}")
    logger.error("Failed to download data from GDFL")


def upload_option_data(processed_data, database_connection):
    with create_engine(database_connection._alchemy_engine_url).connect() as conn:
        processed_data.to_sql("index_options", conn, if_exists="append", index=False)


def unzip_file(zip_path, csv_filename):
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        with zip_file.open(csv_filename) as csv_file:
            df = pd.read_csv(csv_file)
    return df


def process_and_upload_zip_file(
    local_directory: str, zip_file_name: str, database_connection
):
    local_file_path = os.path.join(local_directory, zip_file_name)
    csv_name = zip_file_name.split(".")[0] + ".csv"
    csv_data = unzip_file(local_file_path, csv_name)
    processed_data = process_daily_prices(csv_data)
    upload_option_data(processed_data, database_connection)
