from datetime import datetime
from importlib.resources import files
import json
import atexit
import logging
import logging.config
import os


def setup_logging():

    config_file = files("volstreet").joinpath("vslogging", "logging_config.json")
    with open(config_file) as f_in:
        config = json.load(f_in)
    directory = config["handlers"]["file_json"]["filename"]
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    config["handlers"]["file_json"]["filename"] = (
        directory + f"/{datetime.now().strftime('%Y-%m-%d')}.log.jsonl"
    )
    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")

    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)
