from typing import Iterable
import numpy as np
import pandas as pd


def compute_elapsed_seconds(epochs:pd.Series) -> pd.Series:
    return (epochs - epochs.iloc[0]).dt.total_seconds()

def compute_decimal_hours(epochs:pd.Series) -> pd.Series:
    return epochs.apply(lambda x: x.hour + x.minute / 60 + x.second / 3600)

def compute_rms(values:Iterable) -> float:
    """
    Compute the Root Mean Square of an array of values

    >>> array = [1, 2, 3, 4, 5]
    >>> compute_rms(array)
    3.3166247903554
    """
    return np.sqrt(np.mean(np.square(values)))