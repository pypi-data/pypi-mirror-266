# Copyright 2023-2025 Jeongmin Kang, jarvisNim @ GitHub
# See LICENSE for details.

import sys, os
import pandas as pd
import numpy as np
import requests
import yfinance as yf
import warnings
import logging, logging.config, logging.handlers

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from fredapi import Fred

from .utils import constant as cst


'''
공통 영역
'''
warnings.filterwarnings('ignore')

now = datetime.today()
global to_date, to_date2, to_date3
to_date = now.strftime('%d/%m/%Y')
to_date2 = now.strftime('%Y-%m-%d')
to_date3 = now.strftime('%Y%m%d')
# print('to_date: ', to_date)
# print('to_date2: ', to_date2)
# print('to_date3: ', to_date3)

global from_date_LT, from_date_MT, from_date_ST, from_date_LT2, from_date_MT2, from_date_ST2, from_date_LT3, from_date_MT3, from_date_ST3
# Used to analyze during 3 months for short term
_date = now + relativedelta(months=-3)
from_date_ST = _date.strftime('%d/%m/%Y')
from_date_ST2 = _date.strftime('%Y-%m-%d')
from_date_ST3 = _date.strftime('%Y%m%d')

# Used to analyze during 5 years for middle term (half of 10year Economic cycle)
_date = now + relativedelta(years=-5)
from_date_MT = _date.strftime('%d/%m/%Y')
from_date_MT2 = _date.strftime('%Y-%m-%d')
from_date_MT3 = _date.strftime('%Y%m%d')

# Used to analyze during 50 years for long term (5times of 10year Economic cycle)
_date = now + relativedelta(years=-50)
from_date_LT = _date.strftime('%d/%m/%Y') 
from_date_LT2 = _date.strftime('%Y-%m-%d')
from_date_LT3 = _date.strftime('%Y%m%d')

# print('Short: ' + from_date_ST + '   Middle: ' + from_date_MT + '    Long: ' + from_date_LT)


# create a logger with the name from the config file. 
# This logger now has StreamHandler with DEBUG Level and the specified format in the logging.conf file
log_batch = logging.getLogger('batch')
log_report = logging.getLogger('report')
log_event = logging.getLogger('event')


utils_dir = os.getcwd() + '/batch/Utils'
reports_dir = os.getcwd() + '/batch/reports'
data_dir = os.getcwd() + '/batch/reports/data'
database_dir = os.getcwd() + '/database'
batch_dir = os.getcwd() + '/batch'
sys.path.append(utils_dir)
sys.path.append(reports_dir)
sys.path.append(data_dir)
sys.path.append(database_dir)
sys.path.append(batch_dir)

fred = Fred(api_key=cst.api_key)

#####################################
# funtions
#####################################

# ticker 별 거래량의 변동성을 확인해서 점수화하는 루틴,  최근 5일 거래량 평균이 200일 거래량 평균과의 변화율 리턴.
def score_volume_volatility(ticker:str, df, fast_period=5, long_period=200):
    result = 0  # 변동성

    if df.empty:
       result = 1
       return result
    else:
        print(f"['Volume'][-1]: {df['Volume'][-1]}")
        print(f"df['Volume'][-7:-2].mean() * 100: {df['Volume'][-7:-2].mean() * 100}")
        # 중국등 일부 국가에서 당일 또는 전일 거래량 수치가 1,000 을 나누지 않은 원숫자로 표현되면서 문제발생하여 이를  대응하기 위한 조건문
        if (df['Volume'][-1] > df['Volume'][-7:-2].mean() * 100):
            df['Volume'][-1] = df['Volume'][-1] / 1000
    
    try:
        short_vol = df['Volume'].ewm(span=fast_period, adjust=False).mean()
        long_vol = df['Volume'].ewm(span=long_period, adjust=False).mean()
        
        if pd.to_datetime(df.index[-1]).strftime('%Y-%m-%d') == to_date2:  # 오늘 일자는 제외
            sum_short_vol = short_vol[-6:-1].sum()
            sum_long_vol = long_vol[-6:-1].sum()            
        else:
            sum_short_vol = short_vol[-5:].sum()
            sum_long_vol = long_vol[-5:].sum()

        result = sum_short_vol / sum_long_vol
    except Exception as e:
        result = 1
    
    return round(result, 2)



# financial modeling 에서 stock hitory 가져와 csv 파일로 저장하기까지. 
def get_stock_history_by_fmp(ticker:str, periods:list):  # period: 1min, 5min, 15min, 30min, 1hour, 4hour, 1day

    for period in periods:
        url = f'https://financialmodelingprep.com/api/v3/historical-chart/{period}/{ticker}?from={from_date_MT2}&to={to_date2}&apikey={cst.fmp_key}'
        try:
            buf = requests.get(url).json()
            df = pd.DataFrame(buf, columns=['date', 'open', 'low','high','close','volume'])
            if df.empty:
                return df
            df['ticker'] = ticker
            df.to_csv(data_dir + f'/{ticker}_hist_{period}.csv', index=False)
        except Exception as e:
            print('Exception: {}'.format(e))
        
    return df


# yahoo finance 에서 stock hitory 가져와 csv 파일로 저장하기까지. 단, 1day 만 가능. 
def get_stock_history_by_yfinance(ticker:str, timeframes:list):

    for timeframe in timeframes:
        try:
            if timeframe == '1min':
                _interval = "1m"                
                _period = "7d"  # yahoo: Only 7 days worth of 1m granularity data
            elif timeframe == '1hour':
                _interval = "1h"
                _period = "3mo"
            else:
                _interval = "1d"
                _period = "3y"

            df = yf.download(tickers=ticker, period=_period, interval=_interval)


            df = df.reset_index()
            if df.empty:
                return df
 
            df['ticker'] = ticker

            new_columns = ['date', 'open', 'high','low','close', 'adj close', 'volume', 'ticker']  # yfinance 에서는 column 명이 대문자.
            df.columns = new_columns

            df.to_csv(data_dir + f'/{ticker}_hist_{timeframe}.csv', index=False, mode='w')

        except Exception as e:
            print('Exception: {}'.format(e))
        
    return df


# 오늘부터 워킹데이 n일 전의 날짜를 얻는 함수
def get_working_day_before(duaration):
    # 오늘 날짜 구하기
    today = datetime.today()

    # 워킹데이 days일 전 날짜 구하기
    working_days_to_subtract = duaration
    working_days_count = 0
    result = today

    while working_days_count < working_days_to_subtract:
        result -= timedelta(days=1)
        if result.weekday() < 5:  # 월요일(0)부터 금요일(4)까지의 날짜만 고려
            working_days_count += 1

    return result.strftime("%Y-%m-%d")


# 트렌드 디텍터
def trend_detector(data, col, tp_date_from, tp_date_to=to_date2, order=1):
    tp_date_from = pd.Timestamp(tp_date_from,).tz_localize('US/Eastern')
    tp_date_to = pd.Timestamp(tp_date_to,).tz_localize('US/Eastern')
    buf = np.polyfit(np.arange(len(data[tp_date_from:tp_date_to].index)), data[col][tp_date_from:tp_date_to], order)
    slope = buf[-2]
    
    return float(slope)


# Tipping Point 인자 추자: 20220913
def trend_detector_for_series(df, tp_date_from, tp_date_to=to_date2, order=1):
    tp_date_from = pd.Timestamp(tp_date_from,).tz_localize('US/Eastern')
    tp_date_to = pd.Timestamp(tp_date_to,).tz_localize('US/Eastern')  
    data = df[df.index >= tp_date_from.strftime('%Y-%m-%d')]
    buf = np.polyfit(np.arange(len(data[tp_date_from:tp_date_to].index)), data[tp_date_from:tp_date_to], order)
    slope = buf[-2]
    
    return float(slope)

