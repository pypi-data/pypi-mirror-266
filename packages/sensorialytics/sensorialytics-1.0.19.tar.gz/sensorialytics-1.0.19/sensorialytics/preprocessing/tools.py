#  tools.py
#  Project: sensorialytics
#  Copyright (c) 2021 Sensoria Health Inc.
#  All rights reserved

import numpy as np
import pandas as pd

__all__ = ['get_nans', 'get_single_valued_tsfresh']


def get_nans(df: pd.DataFrame, threshold: float = None):
    """
    :param df: pandas.DataFrame
    :param threshold: value in [0, 1] = percentage of nans to consider
    :return:
    """
    if threshold is None:
        threshold = 0.0

    nans_df = df.isna()
    nans_mean = nans_df.mean()
    nans_sum = nans_df.sum()

    nans = pd.concat({'mean': nans_mean,
                      'sum': nans_sum}, axis=1)

    nans = nans[nans['mean'] > threshold].sort_values('mean')

    return nans


def get_single_valued_tsfresh(db: pd.DataFrame):
    """
    Returns the columns containing just one value grouped by original feature.
    Useful to detect those tsfresh features which have been calculated in the
    wrong manner.
    :param db:
    :return:
    """

    uniques = db.nunique()
    uniques = uniques[uniques == 1]
    uniques.index = pd.MultiIndex.from_tuples(
        [x.split('__', 1) for x in uniques.index])

    uniques = uniques.unstack().T.replace(1.0, 'x').replace(np.nan, '')

    return uniques
