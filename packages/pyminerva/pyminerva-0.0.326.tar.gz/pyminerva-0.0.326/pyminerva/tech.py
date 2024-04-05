# Copyright 2023-2025 Jeongmin Kang, jarvisNim @ GitHub
# See LICENSE for details.
'''
Prgram 명: technical Analysis 만들기
Author: jeongmin Kang
Mail: jarvisNim@gmail.com
History
- 20240228  Create
'''
import sys, os, time
import numpy as np
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
import yfinance as yf
import requests

from scipy import signal
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
from .utils import constant as cst
from . import base

'''
0. 공통영역 설정
'''
# logging
# base.log_batch.warning(sys.argv[0] + ' :: ' + str(datetime.today()))
# base.log_report.info('')
# base.log_report.info(sys.argv[0] + ' :: ' + str(datetime.today()))


# 오실로스코프형 그래프
tech_list_osilo = ['sma','ema','macd','adx','ppo','psar','ichmoku','stoch','roc','ao',
                   'obv','pvt','pvi','cmf','vwap','adosc','kvo','nvi','atr','rvi',]

tech_list_band = ['rsi','cci','willr','stochrsi','mfi','bbands','donchian','kc',]

#####################################
# funtions
#####################################

def check_go_upward(df, tech_type):
    result = False

    current_slope_degree = find_current_slope_degree(df, tech_type)
    if current_slope_degree >= 10:
        result = True

    return result


def check_go_downward(df, tech_type):
    result = False

    current_slope_degree = find_current_slope_degree(df, tech_type)
    if current_slope_degree <= -10:
        result = True

    return result


def find_tech_raw_list(TECH_LIST):
    result = []

    for group, techs  in TECH_LIST.items():  # tech_type 의 총 갯수를 확인.
        for tech in techs:
            result.append(tech)

    return result


def find_tech_graph_type(TECH_LIST):

    tech_raw_list = find_tech_raw_list(TECH_LIST)
    if len(tech_raw_list) == len(tech_list_osilo) + len(tech_list_band):
        pass
    else:
        base.log_batch.warning(f'TECH_LIST 와 tech_graph_type is unmatched.')

    return tech_list_osilo, tech_list_band


def find_current_slope_degree(df, tech_type):
    result = 0
    # 5일이동평균의 미분값
    ma = df[tech_type].rolling(window=5).mean()
    current_slope_degree = np.degrees(np.arctan((ma - ma.shift(3)).diff())[-1:])
    if tech_type in ['kvo', 'adosc', 'pvt', 'obv']:  # volume 기반이란 값자체가 크기 때문에 제외, not price.
        # print('        ', 'volume: ', current_slope_degree.values)
        result = 0  # 0 degree 로 간주
    else:
        # print('        ', 'slope: ', current_slope_degree.values)
        result = current_slope_degree.values

    return result

'''
천정 검증 여부 확인
  1) 최고종가, 죄고종가발생일자 찾기
  2) 최고종가 기준일기준 5일이전 3일 이동평균가와 최고가 간의 가격이 상승하되 상승율 각도가 10% 이상이면 OK-1
  3) 최고종가 기준일기준 5일이후 3일 이동평균가와 최고가 간의 가격이 하락하되 하락율 각도가 -10% 이상이면 OK-2
  4) 최고종가 기준일기준 5일이전 매일 거래량 간에 증가 true 가 3개 이상이고, 최대기간 평균거래량의 20% 이상이어야 OK-3
'''
def check_top(df, tech_type):
    result = False
    
    if tech_type not in df.columns:
        print(f'{tech_type} column not found.')
        return False
    if 'Volume' not in df.columns:
        print(f'Volume column not found.')
        return False
    
    # 1) 최고종가, 죄고종가발생일자 찾기
    check_colume = 'Close'
    ma_close = df['Close'].rolling(window=3).mean()
    ma_close.dropna(inplace=True)
    df_volume = df['Volume']   
    highest = ma_close[ma_close.values == max(ma_close)]
    date_index = df.index
    print(f'{highest} is highest.')
    
    # 2) 최고종가 기준일기준 5일이전 3일 이동평균가와 최고가 간의 가격이 상승하되 상승율 각도가 10% 이상이면 OK-1
    previous_5_days = date_index[date_index <= highest.index[0]][-6:]
    ma_previous_close = ma_close[previous_5_days]
    df_previous_volume = df_volume[previous_5_days]    
    print(f'ma_previous_close: {ma_previous_close}')
    print(f'df_previous_volume: {df_previous_volume}')
    decline_dgree = np.degrees(np.arctan((ma_close[previous_5_days][-1] - ma_close[previous_5_days][0])))
    print(f'decline_dgree: {decline_dgree}')
    if decline_dgree < -10:
        result = True
        
    # 3) 최고종가 기준일기준 5일이후 3일 이동평균가와 최고가 간의 가격이 하락하되 하락율 각도가 -10% 이상이면 OK-2
    after_5_days = date_index[date_index >= highest.index[0]][:6]
    ma_after_close = ma_close[after_5_days]
    print(f'ma_after_close: {ma_after_close}')
    increase_degree = np.degrees(np.arctan((ma_close[after_5_days][-1] - ma_close[after_5_days][0])))
    print(f'increase_degree: {increase_degree}')
    if increase_degree > 10:
        result = True
        
    # 4) 최고종가 기준일기준 5일이전 매일 거래량 간에 증가 true 가 3개 이상이고, 최대기간 평균거래량의 20% 이상이어야 OK-3
    tot_vol = 0
    differ = 0
    list_bigger = []

    for i, x in enumerate(df_previous_volume):
        tot_vol += x
        if i == 0:
            avrg_vol = df['Volume'].mean()
        else:
            differ = int(x - save_vol)
            print(f'differ: {differ}')
            if i > 1:
                if differ > save_differ and x > avrg_vol*0.8:
                    list_bigger.append('True')
                else:
                    list_bigger.append('False')


        save_vol = x
        save_differ = differ

    print(f'tot_vol: int({tot_vol})')
    print(f'list_bigger: {list_bigger}')
    count_true = list_bigger.count('True')
    print(f'count_true: {count_true}')
    if count_true >= 3:
        result = True
    else:
        result = False        
        
    return result



'''
바닥 검증 여부 확인
  10일간의 데이터를 가지고, 3일 이동평균을 기준으로 최저점을 찾고, 이 최저점 일자를 기준으로 이전일자의 거래량이 늘어나면서,
  최저점에서 최고 거래량을 보이고, 이후일자의 거래량이 유지 또는 늘어나는 성향을 가지고 있는지 여부.
  1) 최저종가, 죄저종가발생일자 찾기
  2) 최저종가 기준일기준 5일이전 3일 이동평균가와 최저가 간의 가격이 하락하되 하락율 각도가 -10% 이상이면 OK-1
  3) 최저종가 기준일기준 5일이후 3일 이동평균가와 최저가 간의 가격이 상승하되 상승율 각도가 10% 이상이면 OK-2
  4) 최저종가 기준일기준 5일이후 매일 거래량 간에 증가 true 가 3개 이상이고, 최대기간 평균거래량의 20% 이상이어야 OK-3
'''
def check_buttom(df, tech_type):
    result = False
    
    if tech_type not in df.columns:
        print(f'Close column not found.')
        return False
    
    if 'Volume' not in df.columns:
        print(f'Volume column not found.')
        return False

    if df[tech_type][-1:] >= 0:
        print(f'{tech_type} status is plus(+). No Buttom.')
        return False        
    
    # 1) 현재 tech_type 의 값이 (+)(-) 인지 확인후 이전일자로 돌아가며 극성이 변경되는 날짜를 start_date 로 하고,
    # 현재일자를 end_date 로 해서 그 사이에서의 최저종가, 죄저종가발생일자 찾기
    # 단, 현재상태가 (+)이면 바닥찾기는 의미없으므로 pass
    print(df[tech_type].shift(1) > 0) & (df[tech_type] < 0)

    ma_close = df['Close'].rolling(window=3).mean()
    ma_close.dropna(inplace=True)
    df_volume = df['Volume']
    lowest = ma_close[ma_close.values == min(ma_close)]
    date_index = df.index
    print(f'lowest: {lowest}')
    
    # 2) 최저종가 기준일기준 5일이전 3일 이동평균가와 최저가 간의 가격이 하락하되 하락율 각도가 -10% 이상이면 OK-1
    previous_5_days = date_index[date_index <= lowest.index[0]][-6:]
    ma_previous_close = ma_close[previous_5_days]
    df_previous_volume = df_volume[previous_5_days]
    print(f'ma_previous_close: {ma_previous_close}')
    print(f'df_previous_volume: {df_previous_volume}')
    decline_dgree = np.degrees(np.arctan((ma_close[previous_5_days][-1] - ma_close[previous_5_days][0])))
    print(f'decline_dgree: {decline_dgree}')
    if decline_dgree < -10:
        result = True
        
    # 3) 최저종가 기준일기준 5일이후 3일 이동평균가와 최저가 간의 가격이 상승하되 상승율 각도가 10% 이상이면 OK-2
    after_5_days = date_index[date_index >= lowest.index[0]][-6:]
    ma_after_close = ma_close[after_5_days]
    print(f'ma_after_close: {ma_after_close}')
    increase_degree = np.degrees(np.arctan((ma_close[after_5_days][-1] - ma_close[after_5_days][0])))
    print(f'increase_degree: {increase_degree}')
    if increase_degree > 10:
        result = True
        
    # 4) 최저종가 기준일기준 5일이전 매일 거래량 간에 증가 true 가 3개 이상이고, 최대기간 평균거래량 이상이어야 OK-3
    # 바닥에서 최대 거래량이 터질것이라고 예측.
    tot_vol = 0
    diff_vol = 0
    list_bigger = []

    for i, x in enumerate(df_previous_volume):
        tot_vol += x
        if i == 0:
            avrg_vol = df['Volume'].mean()
        else:
            diff_vol = int(x - save_vol)
            print(f'diff_vol: {diff_vol}')
            if i > 1:
                if diff_vol > save_differ and x > avrg_vol*0.8:
                    list_bigger.append('True')
                else:
                    list_bigger.append('False')


        save_vol = x
        save_differ = diff_vol

    print(f'tot_vol: int({tot_vol})')
    print(f'list_bigger: {list_bigger}')
    count_true = list_bigger.count('True')
    print(f'count_true: {count_true}')
    if count_true >= 3:
        result = True
    else:
        result = False
        
    return result


def find_decision_long_msg(tech_type, long_1, long_2, long_3, long_4):

    trend_indics = ['sma','ema','macd','adx','psar','ichmoku','obv','vwap','adosc','atr','donchian',
                    'rvi',]
    overBoughtSold_indics = ['rsi','stoch','willr','mfi','pvi',]
    trendReversal_indics = ['roc','ao','nvi','bbands','kc',]
    kReversal_indics = ['kvo','cmf',]

    # tech_howto: technical analysis 에서 어떤 용도로 사용하는지의 구분
    if tech_type in trend_indics:
        tech_howto = 'trend'
    elif tech_type in overBoughtSold_indics:
        tech_howto = 'overBoughtSold'
    elif tech_type in trendReversal_indics:
        tech_howto = 'trendReversal'
    elif tech_type in kReversal_indics:
        tech_howto = 'kReversal'
    else:
        tech_howto = None

    # latest date 찾기
    if long_1.empty & long_2.empty & long_3.empty & long_4.empty:
        latest_date = '2099-12-31' # 임시
        decision = 0
        decision_msg = '현상태 유지'
    else:
        if long_1.empty & long_2.empty & long_3.empty:
            latest_date = long_4.index[-1]
        elif long_1.empty & long_2.empty & long_4.empty:
            latest_date =long_3.index[-1]
        elif long_1.empty & long_3.empty & long_4.empty:
            latest_date =long_2.index[-1]
        elif long_2.empty & long_3.empty & long_4.empty:
            latest_date =long_1.index[-1]              
        elif long_1.empty & long_2.empty:
            latest_date = max(long_3.index[-1],long_4.index[-1])
        elif long_1.empty & long_3.empty:
            latest_date = max(long_2.index[-1],long_4.index[-1])
        elif long_1.empty & long_4.empty:
            latest_date = max(long_2.index[-1],long_3.index[-1]) 
        elif long_2.empty & long_3.empty:
            latest_date = max(long_1.index[-1],long_4.index[-1])
        elif long_2.empty & long_4.empty:
            latest_date = max(long_1.index[-1],long_3.index[-1])
        elif long_1.empty:
            latest_date = max(long_2.index[-1],long_3.index[-1],long_4.index[-1])
        elif long_2.empty:
            latest_date = max(long_1.index[-1],long_3.index[-1],long_4.index[-1])
        elif long_3.empty:
            latest_date = max(long_1.index[-1],long_2.index[-1],long_4.index[-1])
        elif long_4.empty:
            latest_date = max(long_1.index[-1],long_2.index[-1],long_3.index[-1])                
        else:
            latest_date = max(long_1.index[-1],long_2.index[-1],long_3.index[-1],long_4.index[-1])

        try:
            if latest_date == long_1.index[-1]:  # 분할매수 시작
                decision = 1
                if tech_howto == 'trend':
                    decision_msg = '분할매수 시작, 상승추세'
                elif tech_howto == 'overBoughtSold':
                    decision_msg = '분할매수 시작, 과매도 상태'
                elif tech_howto == 'trendReversal':
                    decision_msg = '분할매수 시작, 급격한 변화징후 없음'
                elif tech_howto == 'kReversal':
                    decision_msg = '분할매수 시작, k 반전없음'
                else:
                    decision_msg = '분할매수 시작...'
        except IndexError as e:
            pass

        try:    
            if latest_date == long_2.index[-1]:  # 분할매수 마무리
                decision = 2
                if tech_howto == 'trend':
                    decision_msg = '분할매수 끝, 옆으로 눕는 트랜드'
                elif tech_howto == 'overBoughtSold':
                    decision_msg = '분할매수 끝, 과매수 진행중'
                elif tech_howto == 'trendReversal':
                    decision_msg = '분할매수 끝, 특별한 반전징후 없음.'
                elif tech_howto == 'kReversal':
                    decision_msg = '분할매수 끝, k 상승반전 없음'
                else:
                    decision_msg = '분할매수 끝...'
        except IndexError as e:
            pass

        try:
            if latest_date == long_3.index[-1]:  # 분할매도 시작
                decision = 3
                if tech_howto == 'trend':
                    decision_msg = '분할매도 시작, 추세하락'
                elif tech_howto == 'overBoughtSold':
                    decision_msg = '분할매도 시작, 과매수'
                elif tech_howto == 'trendReversal':
                    decision_msg = '분할매도 시작, 하락반전'
                elif tech_howto == 'kReversal':
                    decision_msg = '분할매도 시작, k 하락반전'
                else:
                    decision_msg = '분할매도 시작'
        except IndexError as e:     
            pass

        try:
            if latest_date == long_4.index[-1]:  # 분할매도 마무리
                decision = 4
                if tech_howto == 'trend':
                    decision_msg = '분할매도 끝, 하락추세'
                elif tech_howto == 'overBoughtSold':
                    decision_msg = '분할매도 끝, 과매수'
                elif tech_howto == 'trendReversal':
                    decision_msg = '분할매도 끝, 반전징후 없음'
                elif tech_howto == 'kReversal':
                    decision_msg = '분할매도 끝, k 반전없음'            
                else:
                    decision_msg = '분할매도 끝...'
        except IndexError as e:      
            pass

    latest_date = pd.to_datetime(latest_date).date()

    return decision, decision_msg, latest_date


def find_decision_short_msg(tech_type, short_1, short_2, short_3, short_4):

    trend_indics = ['sma','ema','macd','adx','psar','ichmoku','obv','vwap','adosc','atr','donchian',
                    'rvi',]
    overBoughtSold_indics = ['rsi','stoch','willr','mfi','pvi',]
    trendReversal_indics = ['roc','ao','nvi','bbands','kc',]
    kReversal_indics = ['kvo','cmf',]

    # tech_howto: technical analysis 에서 어떤 용도로 사용하는지의 구분
    if tech_type in trend_indics:
        tech_howto = 'trend'
    elif tech_type in overBoughtSold_indics:
        tech_howto = 'overBoughtSold'
    elif tech_type in trendReversal_indics:
        tech_howto = 'trendReversal'
    elif tech_type in kReversal_indics:
        tech_howto = 'kReversal'
    else:
        tech_howto = None

    # latest date 찾기
    if short_1.empty & short_2.empty & short_3.empty & short_4.empty:
        latest_date = '2099-12-31' # 임시
        decision = 0
        decision_msg = '대기'
    else:
        if short_1.empty & short_2.empty & short_3.empty:
            latest_date = short_4.index[-1]
        elif short_1.empty & short_2.empty & short_4.empty:
            latest_date = short_3.index[-1]
        elif short_1.empty & short_3.empty & short_4.empty:
            latest_date = short_2.index[-1]
        elif short_2.empty & short_3.empty & short_4.empty:
            latest_date = short_1.index[-1]              
        elif short_1.empty & short_2.empty:
            latest_date = max(short_3.index[-1],short_4.index[-1])
        elif short_1.empty & short_3.empty:
            latest_date = max(short_2.index[-1],short_4.index[-1])
        elif short_1.empty & short_4.empty:
            latest_date = max(short_2.index[-1],short_3.index[-1]) 
        elif short_2.empty & short_3.empty:
            latest_date = max(short_1.index[-1],short_4.index[-1])
        elif short_2.empty & short_4.empty:
            latest_date = max(short_1.index[-1],short_3.index[-1])
        elif short_1.empty:
            latest_date = max(short_2.index[-1],short_3.index[-1],short_4.index[-1])
        elif short_2.empty:
            latest_date = max(short_1.index[-1],short_3.index[-1],short_4.index[-1])
        elif short_3.empty:
            latest_date = max(short_1.index[-1],short_2.index[-1],short_4.index[-1])
        elif short_4.empty:
            latest_date = max(short_1.index[-1],short_2.index[-1],short_3.index[-1])                
        else:
            latest_date = max(short_1.index[-1],short_2.index[-1],short_3.index[-1],short_4.index[-1])

        try:
            if latest_date == short_1.index[-1]:  # Short-분할매수 시작
                decision = -1
                if tech_howto == 'trend':
                    decision_msg = 'Short-분할매수 시작, 상승추세'
                elif tech_howto == 'overBoughtSold':
                    decision_msg = 'Short-분할매수 시작, 과매도 상태'
                elif tech_howto == 'trendReversal':
                    decision_msg = 'Short-분할매수 시작, 급격한 변화징후 없음'
                elif tech_howto == 'kReversal':
                    decision_msg = 'Short-분할매수 시작, k 반전없음'
                else:
                    decision_msg = 'Short-분할매수 시작...'
        except IndexError as e:
            pass

        try:    
            if latest_date == short_2.index[-1]:  # Short-분할매수 마무리
                decision = -2
                if tech_howto == 'trend':
                    decision_msg = 'Short-분할매수 끝, 옆으로 눕는 트랜드'
                elif tech_howto == 'overBoughtSold':
                    decision_msg = 'Short-분할매수 끝, 과매수 진행중'
                elif tech_howto == 'trendReversal':
                    decision_msg = 'Short-분할매수 끝, 특별한 반전징후 없음.'
                elif tech_howto == 'kReversal':
                    decision_msg = 'Short-분할매수 끝, k 상승반전 없음'
                else:
                    decision_msg = 'Short-분할매수 끝...'
        except IndexError as e:          
            pass

        try:
            if latest_date == short_3.index[-1]:  # Short-분할매도 시작
                decision = -3
                if tech_howto == 'trend':
                    decision_msg = 'Short-분할매도 시작, 추세하락'
                elif tech_howto == 'overBoughtSold':
                    decision_msg = 'Short-분할매도 시작, 과매수'
                elif tech_howto == 'trendReversal':
                    decision_msg = 'Short-분할매도 시작, 하락반정'
                elif tech_howto == 'kReversal':
                    decision_msg = 'Short-분할매도 시작, k 하락반전'
                else:
                    decision_msg = 'Short-분할매도 시작'
        except IndexError as e:         
            pass

        try:
            if latest_date == short_4.index[-1]:  # Short-분할매도 마무리
                decision = -4
                if tech_howto == 'trend':
                    decision_msg = 'Short-분할매도 끝, 하락추세'
                elif tech_howto == 'overBoughtSold':
                    decision_msg = 'Short-분할매도 끝, 과매수'
                elif tech_howto == 'trendReversal':
                    decision_msg = 'Short-분할매도 끝, 반전징후 없음'
                elif tech_howto == 'kReversal':
                    decision_msg = 'Short-분할매도 끝, k 반전없음'            
                else:
                    decision_msg = 'Short-분할매도 끝...'
        except IndexError as e:       
            pass

    latest_date = pd.to_datetime(latest_date).date()

    return decision, decision_msg, latest_date    


# yfinance 를 이용한 ticker 히스토리 데이터 가져오기
def get_tech_yf_hist(ticker, window):

    obj_yf_ticker = yf.Ticker(ticker)
    # History Data
    df_hist = obj_yf_ticker.history(period='36mo') # test: 10mo, real: 36mo
    try:
        df_hist['feature'] = signal.detrend(df_hist['Close'])  # 통계 정확성을 위한 주기성 시그널 제거용
        df_hist['mean'] = df_hist['feature'].rolling(window=window).mean()
        df_hist['std'] = df_hist['feature'].rolling(window=window).std()        
    except ValueError as e: # ValueError: cannot reshape array of size 0 into shape (0,newaxis)
            time.sleep(3.1)
            base.log_batch.error(f'{ticker} get_tech_yf_hist Value error 1: {e}')  # get_tech_yf_hist Value error 1: array must not contain infs or NaNs: 채권에서처럼 detrend 를 만들수 없는 오류
            df_hist = obj_yf_ticker.history(period='36mo') # test: 10mo, real: 36mo

    return df_hist


# yfinance 를 이용한 statesments 데이터 가져오기
def get_tech_yf_fin(ticker, timeframe='Q', statement='I'):

    obj_yf_ticker = yf.Ticker(ticker)
    # Financial Data: 이 정보는 finviz 에서 분기단위 + 4개분기 더 제공하여 대체됨. (finviz fobidden 시 활용가능) 20240309
    if statement in ['I', 'B', 'C']: # Income statement, Balance sheet, Cash flow
        if statement == 'I':
            if timeframe == 'A':
                data = obj_yf_ticker.income_stmt  # income_stmt == financials
            else:  # 'Q' 분기별
                data = obj_yf_ticker.quarterly_income_stmt  # 손익계산서
        elif timeframe == 'B':  # Balance sheet
            if timeframe == 'A':
                data = obj_yf_ticker.balance_sheet
            else:# 'Q' 분기별
                data = obj_yf_ticker.quarterly_balance_sheet
        else:  # 'C': Cash flow
            if timeframe == 'A':
                data = obj_yf_ticker.cashflow
            else:# 'Q' 분기별
                data = obj_yf_ticker.quarterly_cashflow
    else:
        return None

    data = data.T
    # reset index (date) into a column
    data = data.reset_index()
    # Rename old index from '' to Date
    data.columns = ['Date', *data.columns[1:]]
    data.set_index('Date', inplace=True)

    return data


# yfinance 를 이용한 stastics 데이터 가져오기
def get_tech_yf_stastics(ticker):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"
    }
    url = f"https://finance.yahoo.com/quote/{ticker}/key-statistics"
    soup = BeautifulSoup(requests.get(url, headers=headers).content, "html5lib")

    data = []
    for i, table in enumerate(soup.select("table")):
        th_row = [th.text for th in table.find_all("th")]   
    #     print(th_row)
        for j, tr in enumerate(table.select("tr:has(td)")):
            td_row = [td.text for td in tr.find_all("td")]
    #         print(td_row)
            data.append(td_row)
    #     print()
        
    df = pd.DataFrame(columns=['Item','Value'], data=data)
    df.reset_index(names=['Item'], drop=True, )
    
    return df


# yfinance 를 이용한 Analysis 데이터 가져오기
def get_tech_yf_analysis(ticker):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"
    }
    url = f"https://finance.yahoo.com/quote/{ticker}/analysis?p={ticker}"
    soup = BeautifulSoup(requests.get(url, headers=headers).content, "html5lib")

    for i, table in enumerate(soup.select("table")):
        th_row = [th.text for th in table.find_all("th")]
    #     print(th_row)
        data = []
        for j, tr in enumerate(table.select("tr:has(td)")):
            td_row = [td.text for td in tr.find_all("td")]
    #         print(td_row)
            data.append(td_row)
        
        if i == 0:
            df_earnings_est = pd.DataFrame(data=data, columns=th_row)
        elif i == 1:
            df_revenue_est = pd.DataFrame(data=data, columns=th_row)
        elif i == 2:
            df_earnings_hist = pd.DataFrame(data=data, columns=th_row)
        elif i == 3:
            df_eps_trend = pd.DataFrame(data=data, columns=th_row)
        elif i == 4:
            df_eps_revi = pd.DataFrame(data=data, columns=th_row)        
        elif i == 5:
            df_growth_est= pd.DataFrame(data=data, columns=th_row)
        else:
            print(f'i error')
    
    return [df_earnings_est, df_revenue_est, df_earnings_hist, df_eps_trend, df_eps_revi, df_growth_est]


'''
Technical Analysis: 기술분석 유형에 따라 그래프 그리고, decision 판단하는 핵심 알고리즘
'''
def make_tech_plot(ticker, df, tech_type, TECH_LIST, idx):
    
    _df = df.copy() # 그래프만 그리면 되고, 본 df 에는 영향을 주지않기위해 복사본 만듬.
    # _df = _df.dropna()  # @@@ 그래프 종료일자까지 일부 그래프가 달라지는 현상이 있어 검증을 위해 제거

    h_limit = 70  # 밴드형 상단 기준선
    l_limit = 30  # 밴드형 하단 기준선
    base_limit = 0  # 기준선형 기준선
    permit_range = 0.01 # 20240318 0.02 -> 0.01, 
    result = 0  # 테크니컬 분석 결과, latest date 에 해당하는 분선결과 값: 2 매수시작, 1매수마무리, 0대기, -2매도시작, -1매도마무리

    tech_raw_list = find_tech_raw_list(TECH_LIST)

    plt.subplot(len(tech_raw_list), 1, idx)

    max_val = max(_df[tech_type])
    min_val = min(_df[tech_type])
    tech_list_osilo, tech_list_band = find_tech_graph_type(TECH_LIST)

    current_slope_degree = find_current_slope_degree(_df, tech_type)  # 현재 시점의 기울기 각도
    downward_true = check_go_downward(_df, tech_type)  # 현재 시점의 상향추세 여부
    upward_true = check_go_upward(_df, tech_type)  # 현재 시점의 하향추세 여부

    if tech_type in tech_list_osilo:  # 오실로스코프형 그래프
        
        if tech_type in ['obv','pvt','cmf','vwap','adosc']:  # Volume 베이스 들은 수치가 커서 지표그래프 안보임.
            pass
        else:
            plt.plot(_df.index, _df['Close'], color='royalblue')

        if tech_type == 'adx':
            offset = 25  # offset: DI+ 와 DI- 차이가 25% 이상 또는 이하이면 signal ON
            _df[tech_type] = _df[tech_type] - offset
            plt.plot(_df.index, _df['DMP_14'], color='orange')
            plt.plot(_df.index, _df['DMN_14'], color='orange')
        elif tech_type == 'stoch':
            h_limit = 85
            l_limit = 15            
            plt.plot(_df.index, _df['STOCHk_14_3_3'], color='orange')
            plt.plot(_df.index, _df['STOCHd_14_3_3'], color='orange')
            plt.axhline(y=h_limit, linestyle='--', lw=1.4, color='gray',)
            plt.axhline(y=l_limit, linestyle='--', lw=1.4, color='gray',)            

        plt.bar(_df.index, _df[tech_type], color=['g' if _df[tech_type].iloc[i] > base_limit else 'r' for i in range(len(_df))])

        '''
        ###############################################################################################
        #  핵심 로직이 구현된 곳으로 Minerva 디렉토리에 buyAndSell.jpg 의 의거하여 매수/매도 시그널 포착함. (2024-03-05)
        ###############################################################################################
        
        # 매수매도 신호포착 방법
          1. Long 투자
            - 분할매수 시작:1, 분할매수 중단: 2,  분할매도 시작: 3, 분할매도 끝: 4
          2. Short 투자
            - 분할매수 시작:-1, 분할매수 중단: -2,  분할매도 시작: -3, 분할매도 끝: -4
        '''
        # tech-type 의 그래프의 다시 3일 평균이동값: 미분의 미분값이랄까.... tech-type 의 기울기...
        # _df['tech_type_ewm'] = _df[tech_type].ewm(span=5, adjust=False, min_periods=5).mean()

        if _df[tech_type][-1:].values < 0:
            # ###################################################################################################
            # Short-분할매수 시작
            # baseline을 양에서 음으로 돌파하면 Short 분할매수단계 시작
            _df['pivot'] = np.where((_df[tech_type].shift(1) > 0) & (_df[tech_type] < 0), -1, 0)

            # Short-여전히 분할매수
            # 현재 상태값이 (-)이면서, 오늘부터 최근 3일간의 5일 이동평균값의 각도가 -10% 이상이면 여전히 분할매수 단계
            _df['pivot'] = np.where(((_df[tech_type][-1:].values < 0) & downward_true), -1, _df['pivot'])

            # Short-분할매수 중단
            # 현재 상태값이 (-)이지만, 최근 3일간의 5일 이동평균값의 각도가 +- 10% 범주내이면 Holding = 0
            _df['pivot'] = np.where(((_df[tech_type][-1:].values < 0) & (not downward_true)), -2, _df['pivot'])

            # Short-분할매도 시작
            # 현재 상태값이 (-)이면서, 오늘부터 최근 3일간의 5일 이동평균값의 각도가 +10% 이상이면 분할매도 시작
            _df['pivot'] = np.where((_df[tech_type] < 0) & upward_true, -3, _df['pivot'])

            # Short-분할매도 끝
            _df['pivot'] = np.where((_df[tech_type].shift(1) < 0) & (_df[tech_type] > 0), -4, _df['pivot'])    

        else:  # Long
            # ###################################################################################################
            # Long-분할매수 시작
            # baseline 을 음에서 양으로 돌파하면 분할매수단계 시작
            _df['pivot'] = np.where((_df[tech_type].shift(1) < 0) & (_df[tech_type] > 0), 1, 0)

            # Long-여전히 분할매수
            # 현재 상태값이 (+)이면서, 오늘부터 최근 3일간의 5일 이동평균값의 각도가 +10% 이상이면 여전히 분할매수 단계
            _df['pivot'] = np.where(((_df[tech_type][-1:].values > 0) & upward_true), 1, _df['pivot'])

            # Long-분할매수 중단
            # 현재 상태값이 (+)이지만, 최근 3일간의 5일 이동평균값의 각도가 +- 10% 범주내이면 Holding = 0
            _df['pivot'] = np.where(((_df[tech_type][-1:].values > 0) & (not upward_true)), 2, _df['pivot'])

            # Long-분할매도 시작
            # 현재 상태값이 (+)이면서, 오늘부터 최근 3일간의 5일 이동평균값의 각도가 -10% 이상이면 분할매도 시작
            _df['pivot'] = np.where((_df[tech_type] > 0) & downward_true, 3, _df['pivot'])

            # Long-분할매도 끝
            _df['pivot'] = np.where((_df[tech_type].shift(1) > 0) & (_df[tech_type] < 0), 4, _df['pivot'])         


        long_1 = _df[_df['pivot'] == 1] # Long-분할매수 시작
        long_2 = _df[_df['pivot'] == 2] # Long-분할매수 중단
        long_3 = _df[_df['pivot'] == 3] # Long-분할매도 시작
        long_4 = _df[_df['pivot'] == 4] # Long-분할매도 끝

        short_1 = _df[_df['pivot'] == -1] # Short-분할매수 시작
        short_2 = _df[_df['pivot'] == -2] # Short-분할매수 중단
        short_3 = _df[_df['pivot'] == -3] # Short-분할매도 시작
        short_4 = _df[_df['pivot'] == -4] # Short-분할매도 끝

        # if not long_1.empty:
        #     print('long_1: ', long_1.iloc[-1]['pivot'])
        # if not long_2.empty:            
        #     print('long_2: ', long_2.iloc[-1]['pivot'])
        # if not long_3.empty:            
        #     print('long_3: ', long_3.iloc[-1]['pivot'])
        # if not long_4.empty:            
        #     print('long_4: ', long_4.iloc[-1]['pivot'])

        # if not short_1.empty:
        #     print('short_1: ', short_1.iloc[-1]['pivot'])
        # if not short_2.empty:            
        #     print('short_2: ', short_2.iloc[-1]['pivot'])
        # if not short_3.empty:            
        #     print('short_3: ', short_3.iloc[-1]['pivot'])
        # if not short_4.empty:            
        #     print('short_4: ', short_4.iloc[-1]['pivot'])

        plt.axhline(y=base_limit, linestyle='--', color='red', linewidth=1)

        '''
        top과 Buttom 구간값을 기준으로 설정하는 밴드형인경우:
        밴드형인 경우는 long 만 가능할듯. 
        '''
    elif tech_type in tech_list_band:    
        # 디폴트 30 과 70 기준을 예외로 하는 경우
        if tech_type == 'cci':  
            h_limit = 100
            l_limit = -100
        elif tech_type == 'willr':
            h_limit = -20
            l_limit = -80

        plt.plot(_df.index, _df['Close'], color='royalblue')

        # 분할매수 시작:2, 분할매수 마무리: 1,  분할매도 시작: -2, 분할매도 마무리: -1
        # buttom에서 매수시그널 리포트, 분할매수 시작, 기준선 하단까지가 분할매수 마무리하고,
        # 그 상태로 홀딩하다다가,
        # top 에서 매도시그널 리포트, 분할매도 시작, 기준선 상단까지 분할매도 마무리하는 방식으로 전환: 20240305
        # _df['tech_type_ewm'] = _df[tech_type].ewm(span=5, adjust=False, min_periods=5).mean()

        if tech_type == 'bbands':  # 
            plt.plot(_df.index, _df['BBU_5_2.0'], color='orange')  # Upper line
            plt.plot(_df.index, _df['BBL_5_2.0'], color='orange')  # Lower line
            # print(_df)
            # 분할매도는 상단기준선 넘으면서 바로 시작 (Not top) 해서 top 에서 매도 마무리
            _df['pivot'] = np.where((_df[tech_type] >= _df['BBU_5_2.0']) & (_df[tech_type].shift(3) <= _df['BBU_5_2.0']).shift(3), 3, 0)
            # 분할매도 마무리
            _df['pivot'] = np.where((_df[tech_type] >= _df['BBU_5_2.0']) & (_df[tech_type].shift(3) >= _df['BBU_5_2.0']).shift(3) & \
                                    (current_slope_degree <= abs(permit_range)), 4, _df['pivot'])
            # 분할매수 시작은 Buttom 에서 시작해서 기준선 하단 통과시 매수 마무리
            _df['pivot'] = np.where((_df[tech_type] <= _df['BBL_5_2.0']) & (current_slope_degree <= abs(permit_range)) & \
                                    (_df[tech_type].shift(3) <= _df['BBL_5_2.0']).shift(3), 1, _df['pivot'])
            # 분할매수 마무리
            _df['pivot'] = np.where((_df[tech_type] <= _df['BBL_5_2.0']) & (_df[tech_type].shift(3) <= _df['BBL_5_2.0']).shift(3), 2, _df['pivot'])            
        
        elif tech_type == 'donchian':  # 
            plt.plot(_df.index, _df['DCU_20_20'], color='orange')  # Upper line
            plt.plot(_df.index, _df['DCL_20_20'], color='orange')  # Lower line
            # print(_df)
            # 분할매도는 상단기준선 넘으면서 바로 시작 (Not top) 해서 top 에서 매도 마무리
            _df['pivot'] = np.where((_df[tech_type] >= _df['DCU_20_20']) & (_df[tech_type].shift(3) <= _df['DCU_20_20']).shift(3), 3, 0)
            # 분할매도 마무리
            _df['pivot'] = np.where((_df[tech_type] >= _df['DCU_20_20']) & (_df[tech_type].shift(3) >= _df['DCU_20_20']).shift(3) & \
                                    (current_slope_degree <= abs(permit_range)), 4, _df['pivot'])
            # 분할매수 시작은 Buttom 에서 시작해서 기준선 하단 통과시 매수 마무리
            _df['pivot'] = np.where((_df[tech_type] <= _df['DCL_20_20']) & (current_slope_degree <= abs(permit_range)) & \
                                    (_df[tech_type].shift(3) <= _df['DCL_20_20']).shift(3), 1, _df['pivot'])
            # 분할매수 마무리
            _df['pivot'] = np.where((_df[tech_type] <= _df['DCL_20_20']) & (_df[tech_type].shift(3) <= _df['DCL_20_20']).shift(3), 2, _df['pivot'])  
        
        elif tech_type == 'kc':  # 
            plt.plot(_df.index, _df['KCUe_20_2'], color='orange')  # Upper line
            plt.plot(_df.index, _df['KCLe_20_2'], color='orange')  # Lower line
            # print(_df)
            # 분할매도는 상단기준선 넘으면서 바로 시작 (Not top) 해서 top 에서 매도 마무리
            _df['pivot'] = np.where((_df[tech_type] >= _df['KCUe_20_2']) & (_df[tech_type].shift(3) <= _df['KCUe_20_2']).shift(3), 3, 0)
            # 분할매도 마무리
            _df['pivot'] = np.where((_df[tech_type] >= _df['KCUe_20_2']) & (_df[tech_type].shift(3) >= _df['KCUe_20_2']).shift(3) & \
                                    (current_slope_degree <= abs(permit_range)), 4, _df['pivot'])
            # 분할매수 시작은 Buttom 에서 시작해서 기준선 하단 통과시 매수 마무리
            _df['pivot'] = np.where((_df[tech_type] <= _df['KCLe_20_2']) & (current_slope_degree <= abs(permit_range)) & \
                                    (_df[tech_type].shift(3) <= _df['KCLe_20_2']).shift(3), 1, _df['pivot'])
            # 분할매수 마무리
            _df['pivot'] = np.where((_df[tech_type] <= _df['KCLe_20_2']) & (_df[tech_type].shift(3) <= _df['KCLe_20_2']).shift(3), 2, _df['pivot'])  
        else:
            plt.plot(_df.index, _df[tech_type], color='orange')
            plt.axhline(y=h_limit, linestyle='--', lw=1.4, color='gray',)
            plt.axhline(y=l_limit, linestyle='--', lw=1.4, color='gray',)

            # ###################################################################################################
            # Long-분할매수 시작
            # baseline 을 음에서 양으로 돌파하면 분할매수단계 시작
            _df['pivot'] = np.where((_df[tech_type].shift(1) < 0) & (_df[tech_type] > 0), 1, 0)

            # Long-여전히 분할매수
            # 현재 상태값이 (+)이면서, 오늘부터 최근 3일간의 5일 이동평균값의 각도가 +10% 이상이면 여전히 분할매수 단계
            _df['pivot'] = np.where(((_df[tech_type][-1:].values > 0) & upward_true), 1, _df['pivot'])

            # Long-분할매수 중단
            # 현재 상태값이 (+)이지만, 최근 3일간의 5일 이동평균값의 각도가 +- 10% 범주내이면 Holding = 0
            _df['pivot'] = np.where(((_df[tech_type][-1:].values > 0) & (not upward_true)), 2, _df['pivot'])

            # Long-분할매도 시작
            # 현재 상태값이 (+)이면서, 오늘부터 최근 3일간의 5일 이동평균값의 각도가 -10% 이상이면 분할매도 시작
            _df['pivot'] = np.where((_df[tech_type] > 0) & downward_true, 3, _df['pivot'])

            # Long-분할매도 끝
            _df['pivot'] = np.where((_df[tech_type].shift(1) > 0) & (_df[tech_type] < 0), 4, _df['pivot'])        


        long_1 = _df[_df['pivot'] == 1] # Long-분할매수 시작
        long_2 = _df[_df['pivot'] == 2] # Long-분할매수 중단
        long_3 = _df[_df['pivot'] == 3] # Long-분할매도 시작
        long_4 = _df[_df['pivot'] == 4] # Long-분할매도 끝

        # if not long_1.empty:
        #     print(_1.iloc[-1]['pivot'])
        # if not long_2.empty:            
        #     print(_2.iloc[-1]['pivot'])
        # if not long_3.empty:            
        #     print(_3.iloc[-1]['pivot'])
        # if not long_4.empty:            
        #     print(_4.iloc[-1]['pivot'])

        for date in long_1.index:
            plt.axvline(date, color='g', linestyle='--', lw=1,  alpha=1)
        # for date inlong_2.index:
        #     plt.axvline(date, color='g', linestyle='--', lw=1,  alpha=1)

        for date in long_3.index:
            plt.axvline(date, color='r', linestyle='--', lw=1,  alpha=1) 
        # for date inlong_4.index:
        #     plt.axvline(date, color='r', linestyle='--', lw=1,  alpha=1)



    else:  # osilo 형도  band 형도 아닌 경우..// 
        print(f'{tech_type} is not found in tech_graph_type')
        base.log_batch.warning(f'{tech_type} is not found in tech_graph_type')

    try:  # 밴드형에서는 Short 포지션이 없으므로 오류 발생하므로 Pass !
        decision, decision_msg, latest_date = find_decision_short_msg(tech_type, short_1, short_2, short_3, short_4)
    except Exception as e:
        pass
    decision, decision_msg, latest_date = find_decision_long_msg(tech_type, long_1, long_2, long_3, long_4)
    print(f'{ticker} {tech_type}: {decision} / {latest_date}')

    plt.title(f"{ticker}: {tech_type} / {latest_date}  {decision_msg} ", fontdict={'fontsize':20, 'color':'g'})    
    plt.grid(lw=0.7, color='lightgray')
    # plt.xlabel(f'Last Date: {latest_date}', loc='right', fontsize=18)
    result = decision

    return latest_date, result


'''
I. Technical Analysis

- 1. Trend
    Simple Moving Average (SMA)*
    Exponential Moving Average (EMA)*
    Weighted Moving Average (WMA)
    Moving Average Convergence Divergence (MACD)
    Average Directional Movement Index (ADX)*
    Vortex Indicator (VI)
    Trix (TRIX)
    Mass Index (MI)
    Detrended Price Oscillator (DPO)
    KST Oscillator (KST)
    Ichimoku Kinkō Hyō (Ichimoku)*
    Parabolic Stop And Reverse (Parabolic SAR)*
    Schaff Trend Cycle (STC)
    ZigZag Indicator.... (Not yet)

    
- 2. Momentum: https://medium.com/@crisvelasquez/top-6-momentum-indicators-in-python-bea0875e60a5
    Relative Strength Index (RSI)*
    Stochastic RSI (SRSI)
    True strength index (TSI)
    Ultimate Oscillator (UO)
    Stochastic Oscillator (SR)*
    Williams %R (WR)*
    Awesome Oscillator (AO)*
    Kaufman’s Adaptive Moving Average (KAMA)
    Rate of Change (ROC)*
    Percentage Price Oscillator (PPO)
    Percentage Volume Oscillator (PVO)
    Commodity Channel Index (CCI)*

    
- 3. Volume
    Money Flow Index (MFI)*
    Accumulation/Distribution Index (ADI)*
    On-Balance Volume (OBV)*
    Volume-price Trend (VPT)*    
    Chaikin Money Flow (CMF)*
    Force Index (FI)
    Ease of Movement (EoM, EMV)
    Negative Volume Index (NVI)*
    Volume Weighted Average Price (VWAP)*
    Ulcer Index (UI)
    Positive Volume Index (PVI)*
    Klinger Volume Oscillator(KVO)*

    
- 4. Volatility
    Average True Range (ATR)*
    Bollinger Bands (BB)*
    Donchian Channel (DC)*
    Keltner Channel (KC)*
    Relative Volatility Index (RVI).... (Not yet)
    Volatility Chaikin.... (Not yet)

'''

'''
1. Trend Indicators: https://medium.com/@crisvelasquez/top-6-trend-indicators-in-python-c922ac0674f9
'''
# Trend.Simple Moving Average (SMA)
# calculates the average price over a specific period, providing a smoothed representation of price movement.
# 특정 기간 동안의 평균 가격을 계산하여 가격 변동을 부드럽게 표현합니다.

def find_trend_slope(df, tech_type, latest_date):
    result = 0

    try:
        from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
        from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    try:
        from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
        if from_5day_ago_slope == 0:
            return result        
    except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
        from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해.
        if from_5day_ago_slope[0] == 0:
            return result

    slope = (from_latest_date_slope / from_5day_ago_slope) * 10

    return result


def sma(ticker, df, tech_type, TECH_LIST, idx):
    try:
        df[tech_type] = df.ta.sma(20) - df.ta.sma(200)
    except ValueError as e:  # 530107.KS: history 건수가 매우 적어 20일 또는 200일 이동평균을 구하지 못하는 오류
        base.log_batch.error(f'{ticker} Technical.sma Value error 1: {e}')
        return df, '2099-12-31', 0, 0
    
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Trend.Exponential Moving Average (EMA)
# gives more weight to recent prices, making it more responsive to new information.
# 최근 가격에 더 많은 가중치를 부여하여 새로운 정보에 더 잘 반응합니다.
def ema(ticker, df, tech_type, TECH_LIST, idx):
    try:
        df[tech_type] = df.ta.ema(20) - df.ta.ema(200)
    except ValueError as e:  # 530107.KS: history 건수가 매우 적어 20일 또는 200일 이동평균을 구하지 못하는 오류
        base.log_batch.error(f'{ticker} Technical.ema Value error 1: {e}')
        return df, '2099-12-31', 0, 0

    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Trend.Exponential Moving Average (EMA)
# shows the relationship between two moving averages of a security’s price.
# 증권 가격의 두 이동 평균 사이의 관계를 보여줍니다.
def macd(ticker, df, tech_type, TECH_LIST, idx):
    # Get the 26-day EMA of the closing price
    k = df['Close'].ewm(span=12, adjust=False, min_periods=12).mean()
    # Get the 12-day EMA of the closing price
    d = df['Close'].ewm(span=26, adjust=False, min_periods=26).mean()
    # Subtract the 26-day EMA from the 12-Day EMA to get the MACD
    macd = k - d
    # Get the 9-Day EMA of the MACD for the Trigger line
    macd_s = macd.ewm(span=9, adjust=False, min_periods=9).mean()
    # Calculate the difference between the MACD - Trigger for the Convergence/Divergence value
    df[tech_type] = (macd - macd_s)*10  # 폭이 너무 작아 크게 보이기 위해 *10
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Average Directional Movement Index (ADX):
# quantify the strength of a trend. 추세의 강도를 정량화합니다.
# The +DI and -DI lines can help identify the direction of the trend. 양의 방향 표시기(+DI) 및 음의 방향 표시기(-DI).
def adx(ticker, df, tech_type, TECH_LIST, idx):  # DMP_14(posituve) 와 DMN_14(negative) 두 개 칼럼 생성
    df.ta.adx(length=14, append=True)
    df[tech_type] = df['ADX_14']
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Parabolic Stop And Reverse (Parabolic SAR)
def psar(ticker, df, tech_type, TECH_LIST, idx):  # DMP_14(posituve) 와 DMN_14(negative) 두 개 칼럼 생성
    df.ta.psar(append=True)
    df['PSARl_0.02_0.2'] = df['PSARl_0.02_0.2'].fillna(0)
    df['PSARs_0.02_0.2'] = df['PSARs_0.02_0.2'].fillna(0)
    df[tech_type] = df['Close'] - (df['PSARl_0.02_0.2'] + df['PSARs_0.02_0.2'])  # PSARl_0.02_0.2 는 long 값, PSARl_0.02_0.2 는 short 값
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal


# Ichimoku Kinkō Hyō (Ichimoku)
# a trend-following indicator that provides entry and exit points.
# 진입점과 이탈점을 제공하는 추세추종 지표입니다.
def ichmoku(ticker, df, tech_type, TECH_LIST, idx):
    df.ta.ichimoku(append=True)
    # Tenkan Sen: ITS_9 > Kijun Sen: IKS_26 => Buy signal
    df[tech_type] = (df['ITS_9'] - df['IKS_26'])*5  # 폭이 너무 작아 크게 보이기 위해 *5
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal


'''
2. Momentum Indicators: https://medium.com/@crisvelasquez/top-6-momentum-indicators-in-python-bea0875e60a5
'''
# Momentum.Relative Strength Index (RSI) 
# measures the speed and change of price movements, oscillating between 0 and 100.
# 0과 100 사이에서 진동하는 가격 움직임의 속도와 변화를 측정합니다.
def rsi(ticker, df, tech_type, TECH_LIST, idx):    
    df[tech_type] = df.ta.rsi(14)
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Momentum.Stochastic Oscillator (STOCH): 
# comparing a particular closing price of a security to a range of its prices over a certain period of time.
# 특정 기간 동안의 특정 유가 증권 종가를 해당 가격 범위와 비교하는 것입니다.
def stoch(ticker, df, tech_type, TECH_LIST, idx):    
    df.ta.stoch(append=True)
    df[tech_type] = df['STOCHk_14_3_3'] - df['STOCHd_14_3_3']
    # print(df.tail())
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Momentum.Rate of Change (ROC) Momentum Oscillator
# measures the percentage change in price between the current price and the price a certain number of periods ago.
# 현재 가격과 특정 기간 전 가격 사이의 가격 변화율을 측정합니다.
def roc(ticker, df, tech_type, TECH_LIST, idx):    
    df.ta.roc(append=True)
    df[tech_type] = df['ROC_10']
    # print(df.tail())
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Momentum.Commodity Channel Index (CCI): identifies cyclical trends in securities 
# by comparing their current typical price (TP) to the average TP over a specific period, usually 20 days.
# 현재 일반 가격(TP)을 특정 기간(보통 20일) 동안의 평균 TP와 비교하여 증권의 순환 추세를 식별합니다.
def cci(ticker, df, tech_type, TECH_LIST, idx):    
    df.ta.cci(append=True)
    df[tech_type] = df['CCI_14_0.015']
    # print(df.tail())
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Momentum.Williams %R (WR): reflects the level of the close relative to the highest high for a set period.
# 일정 기간 동안 최고가 대비 종가 수준을 반영합니다.
def willr(ticker, df, tech_type, TECH_LIST, idx):    
    df.ta.willr(append=True)
    df[tech_type] = df['WILLR_14']
    # print(df.tail())
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Momentum.Awesome Oscillator (AO): designed to capture momentum in the market by comparing the recent market momentum with the general momentum over a wider frame of time.
# 최근 시장 모멘텀과 더 넓은 기간 동안의 일반적인 모멘텀을 비교하여 시장의 모멘텀을 포착합니다.
def ao(ticker, df, tech_type, TECH_LIST, idx):    
    df.ta.ao(append=True)
    df[tech_type] = df['AO_5_34']
    # print(df.tail())
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10

    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Momentum.Stochastic RSI (STOCHRSI)
def stochrsi(ticker, df, tech_type, TECH_LIST, idx):
    df.ta.stochrsi(append=True)    
    df[tech_type] = df['STOCHk_14_3_3'] - df['STOCHd_14_3_3']
    # print(df.tail())
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Momentum.Percentage Price Oscillator (PPO):
# "Stochastic RSI and Dynamic Momentum Index" was created by Tushar Chande and Stanley Kroll and published in Stock & Commodities V.11:5 (189-199)
# It is a range-bound oscillator with two lines moving between 0 and 100.
def ppo(ticker, df, tech_type, TECH_LIST, idx):    
    buf= df.ta.ppo(close=df['Close'], append=True)
    df[tech_type] = buf['PPO_12_26_9']
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10  # 잘 보이려고 확대
    
    return df, latest_date, slope, signal

'''
3. Volume Indicators: https://medium.com/@crisvelasquez/top-9-volume-indicators-in-python-e398791b98f9
'''
# Volume.On-Balance Volume (OBV)
# a cumulative indicator that relates volume to price change. 
# OBV increases or decreases during each trading day in line with whether the price closes higher or lower from the previous close.
# 거래량과 가격 변화를 연결하는 누적 지표입니다.
# OBV는 가격이 이전 종가보다 높게 또는 낮게 마감되는지 여부에 따라 각 거래일 동안 증가하거나 감소합니다.
def obv(ticker, df, tech_type, TECH_LIST, idx):    
    df.ta.obv(append=True)
    df['OBV_EMA'] = df['OBV'].ewm(span=30).mean()  # 20-day EMA of OBV
    df[tech_type] = df['OBV'] - df['OBV_EMA']
    # print(df.tail())
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Volume.Volume Price Trend (VPT)
# integrates volume with the percentage change in price, cumulatively indicating the trend’s strength and direction.
# 거래량과 가격 변동률을 통합하여 추세의 강도와 방향을 누적적으로 나타냅니다.
def pvt(ticker, df, tech_type, TECH_LIST, idx):    
    df.ta.pvt(append=True)
    df['PVT_MA'] = df['PVT'].rolling(window=30).mean()  # 20-day moving average
    df[tech_type] = df['PVT'] - df['PVT_MA']
    # print(df.tail())
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Volume.Positive Volume Index (PVI)
# @@@quantifies the percentage rate at which volume changes over a specific period, comparing current volume to volume from n days ago.
# @@@n일 전의 거래량과 현재 거래량을 비교하여 특정 기간 동안 거래량이 변경되는 비율을 정량화합니다.
def pvi(ticker, df, tech_type, TECH_LIST, idx):    
    df.ta.pvi(append=True)
    df['PVI_1_MA'] = df['PVI_1'].rolling(window=30).mean()  # 20-day moving average
    df[tech_type] = df['PVI_1'] - df['PVI_1_MA']
    # print(df.tail())
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Volume.Chaikin Money Flow (CMF)
# integrates price and volume to measure the buying and selling pressure over a specified period, typically 20 days.
# 특정 기간(일반적으로 20일) 동안의 매수 및 매도 압력을 측정하기 위해 가격과 거래량을 통합합니다.
def cmf(ticker, df, tech_type, TECH_LIST, idx):    
    df.ta.cmf(append=True)
    df[tech_type] = df['CMF_20']
    # print(df.tail())
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Volume.Volume-Weighted Average Price (VWAP)
# gives the average price a stock has traded at during the day, weighted by volume
# 거래량에 따라 가중치를 적용하여 하루 동안 주식이 거래된 평균 가격을 제공합니다.
def vwap(ticker, df, tech_type, TECH_LIST, idx):
    df.ta.vwap(append=True)
    df[tech_type] = df['Close'] - df['VWAP_D']
    # print(df.tail())
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Volume.Accumulation/Distribution Oscillator (ADOSC)
# designed to reflect the cumulative flow of money into or out of a security, factoring in both the volume and the price movement.
# 거래량과 가격 변동을 모두 고려하여 증권 안팎으로의 누적 자금 흐름을 반영하도록 설계되었습니다.
def adosc(ticker, df, tech_type, TECH_LIST, idx):
    df.ta.adosc(append=True)
    df[tech_type] = df['ADOSC_3_10']
    # print(df.tail())
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Volume.Money Flow Index (MFI)
# a technical momentum indicator that combines price and volume to assess the buying or selling pressure on an asset. 
# 자산에 대한 매수 또는 매도 압력을 평가하기 위해 가격과 거래량을 결합하는 기술적 모멘텀 지표입니다.
def mfi(ticker, df, tech_type, TECH_LIST, idx):
    df[tech_type] = df.ta.mfi(close=df['Close'],length=14, append=True)
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Volume.Klinger Volume Oscillator (KVO)
# It is designed to predict price reversals in a market by comparing volume to price
# 거래량과 가격을 비교하여 시장의 가격 반전을 예측하도록 설계되었습니다.
def kvo(ticker, df, tech_type, TECH_LIST, idx):
    df.ta.kvo(append=True)
    df[tech_type] = df['KVO_34_55_13']
    # print(df.tail())
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Volume.Negative Volume Index (NVI)
# cumulative indicator that increases when the volume decreases compared to the previous session, suggesting that the “smart money” is active.
# 이전 세션에 비해 거래량이 감소할 때 증가하는 누적 지표로 '스마트머니'가 활성화되었음을 시사한다.
def nvi(ticker, df, tech_type, TECH_LIST, idx):
    df.ta.nvi(append=True)
    df['NVI_1_SMA'] = df['NVI_1'].rolling(window=20).mean()    
    df[tech_type] = df['NVI_1'] - df['NVI_1_SMA']
    # print(df.tail())
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal


'''
4. Volatility Indicators: https://medium.com/@crisvelasquez/top-6-volatility-indicators-in-python-14fbd7bf92d8
'''
# Volatility.Average True Range (ATR)
# quantifies market volatility by averaging the range of price movements.
# 가격 변동 범위를 평균하여 시장 변동성을 정량화합니다.
def atr(ticker, df, tech_type, TECH_LIST, idx):
    df.ta.atr(append=True)
    df['ATRr_14_MA'] = df['ATRr_14'].rolling(window=20).mean()    
    df[tech_type] = df['ATRr_14'] - df['ATRr_14_MA']
    # print(df.tail())
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Volatility.Bollinger Bands (BB)
# provide insights into market volatility and overbought/oversold conditions.
# 시장 변동성과 과매수/과매도 상태에 대한 통찰력을 제공합니다.
def bbands(ticker, df, tech_type, TECH_LIST, idx):    
    df.ta.bbands(append=True)
    df[tech_type] = df['Close']
    # print(df.tail())
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)    
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Volatility.Donchian Channels (DONCHAIN)
# are based on the highest high and lowest low, offering a view of market range and volatility.
# 최고가와 최저가를 기반으로 하며 시장 범위와 변동성에 대한 시각을 제공합니다.
def donchian(ticker, df, tech_type, TECH_LIST, idx):    
    df.ta.donchian(append=True)
    df[tech_type] = df['Close']
    # print(df.tail())
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)    
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Volatility.Keltner Channels (KC)
# use ATR for band setting, making them sensitive to volatility spikes.
# 밴드 설정에 ATR을 사용하여 변동성 급증에 민감하게 만듭니다.
def kc(ticker, df, tech_type, TECH_LIST, idx):    
    df.ta.kc(append=True)
    df[tech_type] = df['Close']
    # print(df.tail())
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)    
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal

# Volatility.Relative Volatility Index (RVI)
# volatility measurement that mirrors the RSI but uses standard deviation.
# RSI를 반영하지만 표준편차를 사용하는 변동성 측정입니다.
def rvi(ticker, df, tech_type, TECH_LIST, idx):
    df.ta.rvi(append=True)
    df['RVI_14_SMA'] = df['RVI_14'].rolling(window=20).mean()    
    df[tech_type] = df['RVI_14'] - df['RVI_14_SMA']
    # print(df.tail())
    latest_date, signal = make_tech_plot(ticker, df, tech_type, TECH_LIST, idx)
    slope = find_trend_slope(df, tech_type, latest_date)
    # try:
    #     from_latest_date_slope = base.trend_detector(df, tech_type, latest_date)
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_latest_date_slope = (df[tech_type] - df[tech_type].shift(10)) / 10
    # try:
    #     from_5day_ago_slope = base.trend_detector(df, tech_type, base.get_working_day_before(5))
    # except Exception as e:  # lastest_date 가 짧아 np.polyfit 함수 오류로 인한 수작업 기울기 구하기.
    #     from_5day_ago_slope = (df[tech_type] - df[tech_type].shift(3)) / 3 # 더 빠른 반응을 위해. 

    # slope = (from_latest_date_slope / from_5day_ago_slope) * 10
    
    return df, latest_date, slope, signal