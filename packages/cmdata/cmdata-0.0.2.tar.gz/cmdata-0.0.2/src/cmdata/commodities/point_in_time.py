import functools
import typing

import numpy
import pandas

from cmdata import common

MIN_LAG = 3
MAX_LAG = 90


def read(path: str) -> pandas.DataFrame:
    """
    Reads a commodity pack point-in-time dataset

    :param path: a path

    :return: a pandas DataFrame
    """
    df = pandas.read_csv(path, parse_dates=['activity_date', 'publication_timestamp'])

    return df


def select_increments(df: pandas.DataFrame,
                      asof=typing.Optional[pandas.Timestamp]) -> pandas.DataFrame:
    """
    Select only the increments in `df` that are
    at or before `asof`.

    This step removes the possibility of look-ahead-bias
    by explicitly removing any data that depends on
    information observed after `asof`.

    :param df: pandas.DataFrame containing a CM point-in-time dataset
    :param asof: date; any increments later than this date will
                 be removed from `df`

    :return: pandas.DataFrame containing a CM point-in-time dataset
             excluding any increments after `asof`
    """
    if asof is not None:
        # use .copy() to avoid a SettingWithCopyWarning
        df = df[df.publication_timestamp <= asof].copy()

    return df


def add_lag_column(df: pandas.DataFrame) -> pandas.DataFrame:
    """
    Adds a lag column, computed as

        lag = date(publication_timestamp) - activity_date

        note: activity_date > publication_timestamp

    This lag represents how many days of information
    have gone into the assessment of the row.

    Longer lags := more information processed := better estimate

    :param df: pandas.DataFrame containing a CM point-in-time dataset

    return: pandas.DataFrame containing a CM point-in-time dataset with
            an additional lag column
    """
    df['lag'] = (((df.publication_timestamp.dt.tz_convert(None) - df.activity_date) /
                  pandas.Timedelta('1D')).astype('int'))

    return df


def select_view(df: pandas.DataFrame,
                selector: typing.Callable[[pandas.DataFrame], pandas.DataFrame],
                asof: typing.Optional[typing.Union[str, pandas.Timestamp]] = None) -> pandas.DataFrame:
    """
    The Point-in-Time (PiT) data structure provides multiple
    estimates of the mass for a given activity_date, each for
    a different publication time.

    To create a view of the commodity flows one needs to pick
    exactly one of the (activity_date, publication_timestamp)s
    for each activity_date.

        Note: the PiT dataset is sparse, i.e., if a certain country
        direction has a zero mass for a given date, that data-point
        will be missing.

    The `asof` argument allows one to select only estimates
    that were available at or before `asof` in order to generate samples
    without look-ahead bias. If asof is None, all estimaes will
    be considered.

    :param df: pandas.DataFrame containing a CM point-in-time dataset
    :param selector: callable that returns the set of `(activity_date, lag)`
                     to be included in the view
    :param asof: optional date; any increments later than this date will
                 be excluded from the view

    :return: point-in-time view pandas.DataFrame
    """
    # select only the increments we're interested in
    df = select_increments(df, asof)
    # add a (convenience) lag column
    df = add_lag_column(df)

    # select exactly one estimate for each activity_date per (country, direction)
    #
    #  1: get the set of (activity_date, lag)s from the selector
    activity_date_and_lags = selector(df)
    #  2: get the distinct set of (country, direction)s
    country_direction = df[['country', 'direction']].drop_duplicates()
    # 3: the cross join of the two above are all the rows we want to
    #    keep
    cross = activity_date_and_lags.join(country_direction, how='cross')
    # 4: do the actual join - filling missing values with zero
    join_cols = ['activity_date', 'lag', 'country', 'direction']
    df = df.join(cross.set_index(join_cols), on=join_cols, how='inner').fillna(0.)

    # now convert to tabular form, which will also convert the
    #   dataset to a dense representation with missing
    #   activity_dates having zero mass
    df = df.pivot_table(index=['activity_date', 'lag'], columns=['direction', 'country'], values='mass').fillna(0.)
    df = df.reset_index('lag', drop=True)

    return df

#
# view_selectors need to define which `(activity_date, lag)` combinations are
#   included in the view. `lag` is a proxy for the publication timestamp.
#
# The point-in-time dataset has several increments of the same `activity_date`
#   and the role of the view_selector is to pick which increment it wants to
#   include in the view for each `activity_date`. I.e., within a view,
#   each `activity_date` can only be associated with a single increment,
#   i.e., a single lag.
#
def fixed_lag_view_selector(df: pandas.DataFrame, lag: int) -> pandas.DataFrame:
    """
    Returns a data-frame of {`activity_date`, `lag`} containing
    the (activity_date, lag) combinations that we want to keep
    in the dataset view.

    Here we are selecting a view that has a FIXED lag, i.e., we
    only select activity_dates that have the same lag of `lag`.

    This means we select one activity_date per increment.

    :param df: pandas.DataFrame containing a CM point-in-time dataset
    :param lag: lag to be included in the view

    :return: pandas.DataFrame[activity_date, lag]
    """
    # find the earliest and latest increment in `df`
    min_publication = common.to_date(df.publication_timestamp.min())
    max_publication = common.to_date(df.publication_timestamp.max())

    # based on the earliest and latest increments find the
    #   range of activity_dates we expect to see, which is the
    #   increment date minus the requested lag for both of them
    min_activity_date = min_publication - pandas.Timedelta(f'{lag}D')
    max_activity_date = max_publication - pandas.Timedelta(f'{lag}D')

    # generate dataframe of activity_dates and lags
    return pandas.DataFrame({'activity_date': pandas.date_range(min_activity_date, max_activity_date),
                             'lag': lag})


def standard_view_selector(df: pandas.DataFrame, min_lag: int = MIN_LAG, max_lag: int = MAX_LAG) -> pandas.DataFrame:
    """
    Returns a data-frame of {`activity_date`, `lag`} containing
    the (activity_date, lag) combinations that we want to keep
    in the dataset view.

    Here we are selecting the increment for each activity_date
    that incorporates the most information, i.e., activity_dates
    with a lag of 90 (which is the maximum lag possible in the
    CargoMetrics point-in-time datasets).

    If a max_lag activity_date does not exist for a given increment
    (which will be the case for the estimates at the leading edge
    of time) pick the activity_date with the maximum available lag.

    :param df: pandas.DataFrame containing a CM point-in-time dataset
    :param min_lag: minimum lag to be included in the view (default 3)
    :param max_lag: maximum lag to be included in the view (default 90)

    :return: pandas.DataFrame[activity_date, lag]
    """
    min_publication, max_publication = df.publication_timestamp.min(), df.publication_timestamp.max(),
    min_activity_date = common.to_date(min_publication - pandas.Timedelta(f'{max_lag}D'))
    max_activity_date = common.to_date(max_publication - pandas.Timedelta(f'{min_lag}D'))

    # generate the range of activity dates in the view
    activity_dates = pandas.date_range(min_activity_date, max_activity_date)
    # for each activity_date select the lag as
    #   min( max_lag, max(publication_date) - activity_date )
    lags = numpy.minimum(((common.to_date(max_publication) - activity_dates) /
                          pandas.Timedelta('1D')).astype('int'), max_lag)

    return pandas.DataFrame({'activity_date': activity_dates,
                             'lag': lags})


def fixed_lag_view(df: pandas.DataFrame,
                   lag: int,
                   asof: typing.Optional[typing.Union[str, pandas.Timestamp]] = None) -> pandas.DataFrame:
    """
    Generates  a fixed lag view at lag `lag` from a point-in-time
    dataset.

    :param df: pandas.DataFrame containing a CM point-in-time dataset
    :param lag: lag to be included in the view
    :param asof: optional date; any increments later than this date will
                 be excluded from the view

    :return: pandas.DataFrame containing the fixed-lag view
    """
    selector = functools.partial(fixed_lag_view_selector, lag=lag)

    return select_view(df, selector, asof=asof)


def standard_view(df: pandas.DataFrame,
                  min_lag: int = 3,
                  max_lag: int = MAX_LAG,
                  asof: typing.Optional[typing.Union[str, pandas.Timestamp]] = None) -> pandas.DataFrame:
    """
    Generates the CargoMetrics standard view, i.e., incorporating most
    information available at time `asof`, from a point-in-time dataset.

    This is the same view form which the weekly and monthly commodity
    pack products are derived.

    The view is a "most information" view because it uses the latest
    and greatest information, i.e., input data, available at `asof`,
    which in turn allows the model to make the best possible assessment
    of maritime trade for each activity date

    :param df: pandas.DataFrame containing a CM point-in-time dataset
    :param min_lag: minimum lag to be included in the view (default 3)
    :param max_lag: maximum lag to be included in the view (default 90)
    :param asof: optional date; any increments later than this date will
                 be excluded from the view

    :return: pandas.DataFrame containing the fixed-lag view
    """
    selector = functools.partial(standard_view_selector, min_lag=min_lag, max_lag=min(MAX_LAG, max_lag))

    return select_view(df, selector, asof=asof)
    
