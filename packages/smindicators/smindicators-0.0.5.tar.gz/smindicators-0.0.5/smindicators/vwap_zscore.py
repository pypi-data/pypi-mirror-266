import numpy as np
from pandas import DataFrame


def vwap_zscore(data: DataFrame, pds):
    volume_close = data['volume'] * data['close']
    mean = volume_close.rolling(window=pds).sum() / data['volume'].rolling(window=pds).sum()
    close_mean = data['close'] - mean
    close_mean_pow = close_mean.pow(2)
    close_mean_pow_sma = close_mean_pow.rolling(window=pds).mean()
    vwapsd = np.sqrt(close_mean_pow_sma)
    return close_mean / vwapsd
