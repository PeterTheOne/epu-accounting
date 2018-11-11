import pandas as pd
import datetime
import re
import unicodedata


def lerp(a, b, x):
    return (x * a) + ((1-x) * b)


def clamp(num, min_value, max_value):
   return max(min(num, max_value), min_value)


def normalize_caseless(text):
    return unicodedata.normalize("NFKD", text.casefold())


def caseless_equal(left, right):
    return normalize_caseless(left) == normalize_caseless(right)


# TODO: min larger than max
def linear_conversion(old_value, old_min, old_max, new_min, new_max):
    new_value = ( (old_value - old_min) / (old_max - old_min) ) * (new_max - new_min) + new_min
    return clamp(abs(new_value), 0, 1)


def match_date(csv_dates, date, range_days=30, future_only=False):
    if date == False:
        return pd.Series([0] * len(csv_dates), index=csv_dates.index)
    weights = []
    for csv_date in csv_dates:
        weight = 1 - linear_conversion((csv_date - date).days, 0, datetime.timedelta(days=range_days).days, 0, 1)
        if future_only and csv_date < date:
            weight = 0
        weights.append( weight )
        #print(str(csv_date - date) + ' to ' + str(weight))
    weights = pd.Series(weights, index=csv_dates.index)
    return weights


def match_exact(csv_column, values):
    values = list(map(lambda v: normalize_caseless(v), values))
    weights = []
    for csv_row in csv_column:
        if len(values) > 0:
            if normalize_caseless(str(csv_row)) in values: # TODO: str cast?
                weight = 1
            else:
                weight = 0
        else:
            weight = 0
        weights.append( weight )
    weights = pd.Series(weights, index=csv_column.index)
    return weights


def match_keywords(csv_comments, keywords):
    weights = []
    pattern = '|'.join(keywords)
    for csv_comment in csv_comments:
        if len(keywords) > 0:
            matches = re.findall(pattern, str(csv_comment), re.IGNORECASE | re.MULTILINE)
            weight = linear_conversion(len(matches), 0, len(keywords), 0, 1)
        else:
            weight = 0
        weights.append( weight )
    weights = pd.Series(weights, index=csv_comments.index)
    return weights


def match_amount(csv_amounts, amount, abs=True, invert=False):
    weights = []
    for csv_amount in csv_amounts:
        if amount != False:
            if abs:
                diff = abs(csv_amount) - abs(amount)
            elif invert:
                diff = max(csv_amount, -amount) - min(csv_amount, -amount)
            else:
                diff = max(csv_amount, amount) - min(csv_amount, amount)
            weight = 1 - linear_conversion(diff, 0, 2, 0, 1)
        else:
            weight = 0
        weights.append( weight )
    weights = pd.Series(weights, index=csv_amounts.index)
    return weights
