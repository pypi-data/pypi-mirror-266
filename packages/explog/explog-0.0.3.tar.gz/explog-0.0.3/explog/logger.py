import os
import re
import json
import string
import random
import pandas as pd
import datetime as dt

from pathlib import Path


EXPS_DIRECTORY = Path("exps")
FORMAT = "[a-zA-Z][a-zA-Z0-9_/]*"
INFOS = ["_id", "_step", "_start"]


def _identifier(n):
    """
    Sample a random identifier.
    """
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def exp(*args, **kwargs):
    """
    Initialize an experiment.
    """
    return Experiment(*args, **kwargs)


def init(*args, **kwargs):
    """
    Alias for `exp`.
    """
    return exp(*args, **kwargs)


def log(*args, **logs):
    """
    Check that an experiment already exists.
    """
    if Experiment.current is None:
        raise AttributeError(
            "Initialize an experiment with `explog.exp` before logging.")

    # Log to current run
    Experiment.current.log(*args, **logs)


def exps():
    """
    Retrieve experiments.
    """
    exps = []
    files = EXPS_DIRECTORY.glob("*/config.json")
    for file in sorted(files, key=lambda x: os.path.getmtime(x)):
        try:
            exp = pd.read_json(file, lines=True, convert_dates=["_start"])
        except ValueError as e:
            print(f"Error while reading config file '{file}' ({e}). Skipped.")
            continue
        exps.append(exp)
    exps = pd.concat(exps, axis=0)
    exps = exps.set_index("_id")
    return exps


def runs():
    """
    Alias for `exps`.
    """
    return exps()


def dict_from_kwargs(config=None, **kwargs):
    """
    Returns dictionary from either a single dictionary or kwargs arguments.
    """
    # Check that inputs are keyword arguments or a dictionary
    if config and kwargs:
        raise ValueError("Usage: log(config) or log(**config).")

    # Parse dictionary
    if config is None:
        dictionary = kwargs
    elif isinstance(config, dict):
        dictionary = config
    else:
        try:
            dictionary = vars(config)
        except TypeError:
            raise ValueError("The provided argument should be a dictionary.")

    return dictionary


def logs(*columns, **filters):
    """
    """
    # Check columns names
    for column in columns:
        if not re.fullmatch(FORMAT, column):
            raise ValueError(f"Column '{column}' not in format '{FORMAT}'")
    columns = list(columns) + list(filters.keys())

    # Retrieve experiments logs
    logs = []
    files = EXPS_DIRECTORY.glob("*/logs.json")
    for file in sorted(files, key=lambda x: os.path.getmtime(x)):
        try:
            log = pd.read_json(file, lines=True)
        except ValueError as e:
            print(f"Error while reading log file '{file}' ({e}). Skipped.")
            continue
        log.index.name = "_step"
        log = log.reset_index()
        for key, val in filters.items():
            if key in log:
                log = log[log[key] == val]
        if columns:
            log = log.loc[:, log.columns.isin(columns + INFOS)]
        logs.append(log)
    logs = pd.concat(logs, axis=0)

    # Join configurations and logs
    logs = logs.merge(exps(), on="_id")

    # Filter rows
    for key, val in filters.items():
        logs = logs[logs[key] == val]

    # Set index
    logs = logs.set_index(["_id", "_step"])

    return logs


class Experiment:
    """
    """
    current = None

    def __init__(self, config=None, *args, id=None, **kwargs):
        # Parse inputs
        config = dict_from_kwargs(config=config, *args, **kwargs)

        # Check configuration keys
        for key in config.keys():
            if not re.fullmatch(FORMAT, key):
                raise ValueError(f"Column '{key}' not in format '{FORMAT}'")

        # Add information
        self.id = _identifier(8) if id is None else id
        info = {"_id": self.id, "_start": dt.datetime.now().isoformat()}

        # Check id does not exist
        path = EXPS_DIRECTORY / self.id
        if path.exists():
            raise ValueError(f"Experiment with id {self.id} already exist")
        else:
            path.mkdir()

        # Store configuration
        with open(EXPS_DIRECTORY / f"{self.id}/config.json", "a") as f:
            f.write(json.dumps(config | info) + "\n")

        # Store current instance in class
        Experiment.current = self

    def log(self, *args, **kwargs):
        """
        """
        # Parse inputs
        logs = dict_from_kwargs(*args, **kwargs)

        # Check logs keys
        for key in logs.keys():
            if not re.fullmatch(FORMAT, key):
                raise ValueError(f"Column '{key}' not in format '{FORMAT}'")

        # Add information
        info = {"_id": self.id, "_time": dt.datetime.now().isoformat()}

        logs_file = EXPS_DIRECTORY / f"{self.id}/logs.json"
        logs_file.touch()
        with open(logs_file, "a") as f:
            f.write(json.dumps(logs | info) + "\n")

    def logs(self, *columns):
        """
        """
        # Retrieve logged data for this run
        return logs(*columns, _id=self.id)
