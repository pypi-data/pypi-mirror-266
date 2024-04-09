import datetime as dt
import os
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from warpzone.servicebus.data.client import DataMessage
from warpzone.transform.schema import generate_and_stringify_schema


def get_filepath(filename: str, subfolder: str = "data"):
    return Path(os.environ["PYTEST_CURRENT_TEST"]).parent / subfolder / filename


def parse_iso_datetime(values: pd.Series) -> pd.Series:
    if values.replace("", np.nan).dropna().empty:
        return values
    try:
        converted_values = pd.to_datetime(values)
    except (ValueError, TypeError):
        # if not possible to parse as datetime, return original values
        return values
    try:
        values_isoformat = converted_values.dropna().apply(pd.Timestamp.isoformat)
    except TypeError:
        return values
    if not (values_isoformat == values.dropna()).all():
        # if original values is not in ISO 8601 format, return original values
        return values
    return converted_values


def parse_iso_timedelta(values: pd.Series) -> pd.Series:
    try:
        converted_values = pd.to_timedelta(values)
    except (ValueError, TypeError):
        # if not possible to parse as time delta, return original values
        return values
    try:
        values_isoformat = converted_values.apply(pd.Timedelta.isoformat)
    except TypeError:
        return values
    if not (values_isoformat == values).all():
        # if original values is not in ISO 8601 format, return original values
        return values
    return converted_values


def read_pandas(
    filename: str,
    subfolder: str = "data",
) -> pd.DataFrame:
    """
    Read pandas DataFrame from test data.
    Datetimes and timedeltas are inferred automatically.

    Args:
        filename (str): CSV file with test data
        subfolder (str, optional): Subfolder relative to test being
            run currently (taken from  the environment variable PYTEST_CURRENT_TEST),
            from where to read the test data. Defaults to "data".
    """
    filepath = get_filepath(filename, subfolder)
    df = pd.read_csv(
        filepath,
        parse_dates=True,
        infer_datetime_format=True,
        keep_default_na=False,
        na_values=["nan"],
    )

    # try converting ISO 8601 strings to pd.Timestamp and pd.Timedelta
    df = df.apply(parse_iso_datetime)
    df = df.apply(parse_iso_timedelta)

    return df


def read_bytes(
    filename: str,
    subfolder: str = "data",
) -> bytes:
    """
    Read bytes from test data.

    Args:
        filename (str): File with test data
        subfolder (str, optional): Subfolder relative to test being
            run currently (taken from  the environment variable PYTEST_CURRENT_TEST),
            from where to read the test data. Defaults to "data".
    """
    filepath = get_filepath(filename, subfolder)
    return filepath.read_bytes()


def read_data_msg(
    filename: str,
    subject: str,
    message_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    timestamp: Optional[dt.datetime] = None,
    subfolder: str = "data",
) -> DataMessage:
    suffixes = Path(filename).suffixes
    if suffixes[0] == ".df":
        df = read_pandas(filename, subfolder)
        schema = generate_and_stringify_schema(df)
        return DataMessage.from_pandas(
            df=df,
            subject=subject,
            schema=schema,
            message_id=message_id,
            metadata=metadata,
            timestamp=timestamp,
        )
    else:
        return DataMessage(
            content=read_bytes(filename, subfolder),
            extension="".join(suffixes).replace(".", "", 1),
            subject=subject,
            message_id=message_id,
            metadata=metadata,
            timestamp=timestamp,
        )
