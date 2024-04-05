# Copyright 2023-2025 Jeongmin Kang, jarvisNim @ GitHub
# See LICENSE for details.


from . import constant as cst


# Loading data, and split in train and test datasets
def get_data(ticker, window):

    ticker = yf.Ticker(ticker)
    df = ticker.history(period='36mo') # test: 10mo, real: 36mo
    df['feature'] = signal.detrend(df['Close'])
    df['mean'] = df['feature'].rolling(window=window).mean()    
    df['std'] = df['feature'].rolling(window=window).std()
    
    return df