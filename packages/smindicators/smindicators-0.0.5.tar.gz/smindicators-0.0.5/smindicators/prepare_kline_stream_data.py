import pandas as pd
from pandas import DataFrame


def prepare_kline_stream_data(kline, data: DataFrame):
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']

    kline_data_formatted = [
        kline['t'],
        float(kline['o']),
        float(kline['h']),
        float(kline['l']),
        float(kline['c']),
        float(kline['v'])
    ]

    new_df = pd.DataFrame([kline_data_formatted], columns=columns)
    new_df['timestamp'] = pd.to_datetime(new_df['timestamp'], unit='ms')
    new_df.set_index('timestamp', inplace=True)

    return pd.concat([data, new_df])
