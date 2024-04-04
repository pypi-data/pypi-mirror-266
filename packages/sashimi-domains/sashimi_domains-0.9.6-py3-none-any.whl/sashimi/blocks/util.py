# Sashimi - Study of the organisation and evolution of a corpus
#
# Author(s):
# * Ale Abdo <abdo@member.fsf.org>
#
# License:
# [GNU-GPLv3+](https://www.gnu.org/licenses/gpl-3.0.html)
#
# Project:
# <https://en.wikiversity.org/wiki/The_dynamics_and_social_organization_of
#  _innovation_in_the_field_of_oncology>
#
# Reference repository for this file:
# <https://gitlab.com/solstag/sashimi>
#
# Contributions are welcome, get in touch with the author(s).

import numpy as np
import pandas

phi = (1 + 5**0.5) / 2  # the golden ratio


def sorted_hierarchical_block_index(blocks, levels, level):
    return sorted(
        tuple(reversed(x))
        for x in (
            blocks[list(levels[levels.index(level) :])]  # list() in case passed a tuple
            .groupby(level)
            .first()
            .itertuples()
        )
    )


def make_normalization_factor(kind):
    """
    Returns a function to get the normalization factor for a set of values
    """
    if kind is None:
        return lambda vals: 1
    elif kind == "bylevel":
        return lambda vals: vals.loc[np.isfinite(vals)].abs().sum() or 1
    elif kind == "bylevelmax":
        return lambda vals: vals.loc[np.isfinite(vals)].abs().max() or 1
    else:
        raise ValueError


def make_normalization_factor_js():
    return """
    function make_normalization_factor(kind) {
        if (kind == "bylevelmax") {
            return value => Math.max(...value.map(Math.abs).filter(Number.isFinite)) || 1
        } else if (kind == "bylevel") {
            const sum = (a, b) => a + b
            return value => value.map(Math.abs).filter(Number.isFinite).reduce(sum, 0) || 1
        } else {
            return value => 1
        }
    }
    """


def try_time_index(series):
    is_time, series = try_datetime(series)
    if is_time:
        series, xindex = try_period_get_range(series)
    else:
        xindex = series.drop_duplicates().sort_values()
    return series, xindex


def is_time_type(series):
    return issubclass(series.dtype.type, (np.datetime64, pandas.Period))


def try_datetime(series):
    is_time = is_time_type(series)
    if is_time:
        return is_time, series
    if series.dropna().map(lambda x: isinstance(x, str)).all():
        try:
            series = to_datetimeindex(series)
            is_time = True
        except Exception:
            pass
    if is_time:
        return is_time, series
    if not issubclass(series.dtype.type, np.number):
        try:
            series = series.astype(int)
        except Exception:
            series = series.astype(float)
        except Exception:
            pass
    if issubclass(series.dtype.type, np.number):
        try:
            if series.min().ge(1678) and series.max().le(2262):
                series.loc[series.notna()] = series.dropna().astype(int).astype(str)
                series = to_datetimeindex(series)
            elif series.min() < 0 or series.max() > 999999:
                series = to_datetimeindex(series, unit="s")
            is_time = True
        except Exception:
            pass
    return is_time, series


def to_datetimeindex(series, **kwargs):
    return pandas.DatetimeIndex(pandas.to_datetime(series, dayfirst=True, **kwargs))


def try_period_get_range(series):
    if issubclass(series.dtype.type, pandas.Period):
        full_range = pandas.period_range(series.min(), series.max())
    elif issubclass(series.dtype.type, np.datetime64) and (freq := get_freq(series)):
        full_range = pandas.period_range(series.min(), series.max(), freq=freq)
        series = series.to_period(freq=freq)
    else:
        full_range = series.drop_duplicates().sort_values()
    full_range.name = series.name
    return series, full_range


def get_freq(series):
    valid = series.dropna()
    return (
        "A"
        if (valid.is_year_start.all() or valid.is_year_end.all())
        else "M"
        if (valid.is_month_start.all() or valid.is_month_end.all())
        else "D"
        if valid.is_normalized
        else False
    )


def btype_to_name(btype, plural=False):
    if btype == "doc":
        return "documents" if plural else "document"
    if btype == "ter":
        return "terms" if plural else "term"
    if btype == "ext":
        return "elements" if plural else "element"
