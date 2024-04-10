import typing

import pandas

def to_date(item: typing.Union[pandas.Timestamp, pandas.Series]) -> typing.Union[pandas.Timestamp, pandas.Series]:
    """
    Helper function to convert timestamp (or pandas.Series of timestamps) to a 'date'
    """
    if isinstance(item, pandas.Series):
        return pandas.to_datetime(pandas.to_datetime(item).dt.date)
    else:
        return pandas.to_datetime(pandas.to_datetime(item).date())
