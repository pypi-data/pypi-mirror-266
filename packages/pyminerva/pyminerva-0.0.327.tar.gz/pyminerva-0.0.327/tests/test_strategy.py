'''
Prgram 명: global(us+world) 의 ticker별 투자전력 시뮬레이션
Author: jeongmin Kang
Mail: jarvisNim@gmail.com
목적: global(us+world) 의 ticker별 투자전력 시뮬레이션 결과을 data table 에 저장하고, 이를 투자판단에 제공하고자 함.
주요 내용
- 
History
2024/03/11  Create
'''

import sys, os
utils_dir = os.getcwd() + '/batch/utils'
sys.path.append(utils_dir)

from time import perf_counter
from settings import *
from economics_db import make_strategy

import pygad

'''
0. 공통영역 설정
'''
import pyminerva as mi
import pandas_ta as ta

from pykrx import stock
from pykrx import bond


# def vb_genericAlgo_strategy(ticker:str, TIMEFRAMES:list):
#     result = None
#     # Constants
#     POPULATIONS = 20
#     GENERATIONS = 50
#     CASH = 1_000_000

#     # Configuration
#     np.set_printoptions(suppress=True)
#     pd.options.mode.chained_assignment = None

#     # Loading data, and split in train and test datasets
#     def get_data(timeframe):

#         df = pd.read_csv(base.data_dir + f'/{ticker}_hist_{timeframe}.csv')
#         if df.empty:
#             base.log_batch.error(f'Read csv file {ticker} / {timeframe} is Empty')
#             return None
#         else:            
#             df.ta.bbands(close=df['close'], length=20, append=True)
#             df = df.dropna()
#             df['high_limit'] = df['BBU_20_2.0'] + (df['BBU_20_2.0'] - df['BBL_20_2.0']) / 2
#             df['low_limit'] = df['BBL_20_2.0'] - (df['BBU_20_2.0'] - df['BBL_20_2.0']) / 2
#             df['close_percentage'] = np.clip((df['close'] - df['low_limit']) / (df['high_limit'] - df['low_limit']), 0, 1)
#             df['volatility'] = df['BBU_20_2.0'] / df['BBL_20_2.0'] - 1

#             if (timeframe == '1min') or (timeframe == '1hour'):
#                 train, test = train_test_split(df, test_size=0.25, random_state=1104)
#             else:
#                 _date = (datetime.now() - timedelta(days=365)).date().strftime('%Y-%m-%d')
#                 train = df[df['date'] < _date]
#                 test = df[df['date'] >= _date]

#         return train, test, df

    
#     # Define fitness function to be used by the PyGAD instance
#     def fitness_func(self, solution, sol_idx):
#         try:
#             # total reward 가 최대값을 갖을 수 있는 solution[0],[1],[2] 의 변수들을 찾아서 최적화(=> pygad.GA()를 통해서)
#             total_reward, _, _ = get_result(train, solution[0], solution[1], solution[2])
#         except:
#             reward = 0
#             pass
#         # Return the solution reward
#         return total_reward

#     # Define a reward function
#     def get_result(df, min_volatility, max_buy_pct, min_sell_pct):
#         # Generate a copy to avoid changing the original data
#         df = df.copy().reset_index(drop=True)

#         # Buy Signal
#         df['signal'] = np.where((df['volatility'] > min_volatility) & (df['close_percentage'] < max_buy_pct), 1, 0)
#         # Sell Signal
#         df['signal'] = np.where((df['close_percentage'] > min_sell_pct), -1, df['signal'])

#         # Remove all rows without operations, rows with the same consecutive operation, first row selling, and last row buying
#         result = df[df['signal'] != 0]
#         result = result[result['signal'] != result['signal'].shift()]
#         if (len(result) > 0) and (result.iat[0, -1] == -1): result = result.iloc[1:]
#         if (len(result) > 0) and (result.iat[-1, -1] == 1): result = result.iloc[:-1]

#         # Calculate the reward / operation
#         result['total_reward'] = np.where(result['signal'] == -1, result['close'] - result['close'].shift(), 0)

#         # Generate the result
#         total_reward = result['total_reward'].sum()
#         wins = len(result[result['total_reward'] > 0])
#         losses = len(result[result['total_reward'] < 0])

#         return total_reward, wins, losses
    

#     # vb_genericAlgo_strategy main function
#     for timeframe in TIMEFRAMES:
#         try:
#             # Get Train and Test data for timeframe
#             train, test, df = get_data(timeframe)
#             # Process timeframe
#             base.log_report.info(f" vb_genericAlgo_strategy: {ticker} / {timeframe} ".center(60, "*"))
#         except KeyError as e: # 히스토리 레코드가 1건이라 볼린저밴드 20 을 만들수 없음.
#             base.log_batch.error(f"vb_genericAlgo_strategy Key Error ({ticker} / {timeframe}): {e}")
#             base.log_batch.error(f"vb_genericAlgo_strategy Key Error ({ticker} / {timeframe}): {e}")
#             continue
#         except Exception as e:
#             base.log_batch.error(f"vb_genericAlgo_strategy Error ({ticker} / {timeframe}): {e}")
#             base.log_batch.error(f"vb_genericAlgo_strategy Error ({ticker} / {timeframe}): {e}")

#         with tqdm(total=GENERATIONS) as pbar:
#             # Create Genetic Algorithm
#             ga_instance = pygad.GA(num_generations=GENERATIONS,
#                                 num_parents_mating=5,
#                                 fitness_func=fitness_func,
#                                 sol_per_pop=POPULATIONS,
#                                 num_genes=3,
#                                 gene_space=[{'low': 0, 'high':1}, {'low': 0, 'high':1}, {'low': 0, 'high':1}],
#                                 parent_selection_type="sss",
#                                 crossover_type="single_point",
#                                 mutation_type="random",
#                                 mutation_num_genes=1,
#                                 keep_parents=-1,
#                                 on_generation=lambda _: pbar.update(1),
#                                 )
#             # Run the Genetic Algorithm
#             ga_instance.run()


#         # log_report.info 정보가 너무 많아 TEST 결과 승률이 80% 이상인 경우만 display 하기 위하여 일부 display 순서 변경 20240122
#         try:
#             # Show details of the best solution.
#             solution, solution_fitness, _ = ga_instance.best_solution()

#             # Get Reward from test data
#             profit, wins, losses = get_result(test, solution[0], solution[1], solution[2])

#             win_rate = (wins/(wins + losses) if wins + losses > 0 else 0) * 100
#             if win_rate >= 80 and profit > 1200000:
#                 # 최적 변수값 찾기
#                 base.log_report.info(f' Volatility & Bollinger Band with Generic Algorithm Strategy: {ticker} Best Solution Parameters for {timeframe} Timeframe '.center(60, '*'))      
#                 base.log_report.info(f"Min Volatility   : {solution[0]:6.4f}")
#                 base.log_report.info(f"Max Perc to Buy  : {solution[1]:6.4f}")
#                 base.log_report.info(f"Min Perc to Sell : {solution[2]:6.4f}")

#                 # Show the final result
#                 base.log_report.info(f'***** {ticker} Result for timeframe {timeframe} (TEST) ')
#                 base.log_report.info(f'* Profit / Loss (B&H)      : {(test["close"].iloc[-1] - test["close"].iloc[0]) * (CASH // test["close"].iloc[0]):.2f}')
#                 base.log_report.info(f"* Profit / Loss (Strategy) : {profit:.2f}")
#                 base.log_report.info(f"* Wins / Losses  : {wins} / {losses}")
#                 base.log_report.info(f"* Win Rate       : {(100 * (wins/(wins + losses)) if wins + losses > 0 else 0):.2f}%")
#                 base.log_report.info("")

#                 # graph @@@ 값 검증 추가 필요: 20240128
#                 graph = df.copy().reset_index(drop=True)
#                 graph = graph.sort_values(by='date')
#                 graph['date'] = pd.to_datetime(graph['date'])

#                 '''
#                 sells, buys, buf, buf2 .... 좀 더 주의깊게 재검증이 필요함. 일단 기능상 충족으로 넘어감. 20240128
#                 '''
#                 sells = graph[graph['close_percentage'] > 95]   # Selling Point
#                 buys = graph[graph['close_percentage'] < 5]   # Buying Point

#                 # graph 에서 sells를 뺀 나머지 구하기
#                 buf = pd.merge(graph, sells, how='outer', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1)
#                 # graph 에서 buys를 뺀 나머지 구하기
#                 buf2 = pd.merge(graph, buys, how='outer', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1) 
#                 # print(buf)

#                 plt.figure(figsize=(18, 6))
#                 plt.plot(graph['date'][-60:], graph['close'][-60:], label='주가', color='black')
#                 plt.plot(graph['date'][-60:], graph['high_limit'][-60:], label='상단 볼린저 밴드', linestyle='--', color='red')
#                 plt.plot(graph['date'][-60:], graph['low_limit'][-60:], label='하단 볼린저 밴드', linestyle='--', color='green')
#                 plt.scatter(buf['date'][-1:], buf['close'][-1:], color='red', label='Selling Point') # 특정 일자에 추가적인 점 플로팅
#                 plt.scatter(buf2['date'][-1:], buf2['close'][-1:], color='green', label='Buying Point') # 특정 일자에 추가적인 점 플로팅                
#                 # 그래프에 제목과 레이블 추가
#                 plt.title(f'Volatility({solution[0]:6.2f}) & BB with GA Strategy: Reward ({profit:.0f}), Wins/Losses ({wins:.0f}/{losses:.0f}), Win Rate ({win_rate:.2f}%)')
#                 plt.xlabel('날짜')
#                 plt.ylabel('가격')
#                 plt.grid()
#                 plt.legend()

#                 plt.savefig(base.reports_dir + f'/global_s0100_{ticker}_{timeframe}.png')

#                 # Get Reward from train data
#                 profit, wins, losses = get_result(train, solution[0], solution[1], solution[2])
#                 base.log_report.info(f'***** {ticker} Result for timeframe {timeframe} (TRAIN) ')
#                 base.log_report.info(f'* Profit / Loss (B&H)      : {(train["close"].iloc[-1] - train["close"].iloc[0]) * (CASH // train["close"].iloc[0]):.2f}')
#                 base.log_report.info(f"* Profit / Loss (Strategy) : {profit:.2f}")
#                 base.log_report.info(f"* Wins / Losses  : {wins} / {losses}")
#                 base.log_report.info(f"* Win Rate       : {win_rate:.2f}%")
#                 if timeframe == '1day':
#                     result = timeframe
#             else:
#                 pass
#         except Exception as e:
#             base.log_batch.error(' >>> Exception4: {}'.format(e))

#     return result

# strategy_list = ['timing', 'volatility_bollinger', 'vb_genericAlgo', 'vb_genericAlgo2', 'reversal',
#                  'trend_following', 'control_chart', 'gaSellHoldBuy']
# df_strg = pd.DataFrame(columns=['Country', 'Market', 'Busi', 
#                                 'timing', 'volatility_bollinger', 'vb_genericAlgo', 'vb_genericAlgo2', 'reversal', 
#                                 'trend_following', 'control_chart', 'gaSellHoldBuy'])


def keras_genericAlgo_strategy(ticker, TIMEFRAMES, solution, solution_idx):

    function_inputs = [4,-2,3.5,5,-11,-4.7]
    desired_output = 44 

    def fitness_func(solution, solution_idx):
        output = numpy.sum(solution*function_inputs)
        fitness = 1.0 / (numpy.abs(output - desired_output) + 0.000001)
        return fitness

    num_generations = 100
    num_parents_mating = 10
    sol_per_pop = 20
    num_genes = len(function_inputs)

    ga_instance = pygad.GA(num_generations=num_generations,
                        num_parents_mating=num_parents_mating,
                        fitness_func=fitness_func,
                        sol_per_pop=sol_per_pop,
                        num_genes=num_genes)

    ga_instance.run()

    ga_instance.plot_result()


    # result = None
    # # Constants
    # POPULATIONS = 20
    # GENERATIONS = 50
    # CASH = 1_000_000

    # # Configuration
    # np.set_printoptions(suppress=True)
    # pd.options.mode.chained_assignment = None

    # # Loading data, and split in train and test datasets
    # def get_data(timeframe):

    #     df = pd.read_csv(base.data_dir + f'/{ticker}_hist_{timeframe}.csv')
    #     if df.empty:
    #         base.log_batch.error(f'Read csv file {ticker} / {timeframe} is Empty')
    #         return None
    #     else:            
    #         df.ta.bbands(close=df['close'], length=20, append=True)
    #         df = df.dropna()
    #         df['high_limit'] = df['BBU_20_2.0'] + (df['BBU_20_2.0'] - df['BBL_20_2.0']) / 2
    #         df['low_limit'] = df['BBL_20_2.0'] - (df['BBU_20_2.0'] - df['BBL_20_2.0']) / 2
    #         df['close_percentage'] = np.clip((df['close'] - df['low_limit']) / (df['high_limit'] - df['low_limit']), 0, 1)
    #         df['volatility'] = df['BBU_20_2.0'] / df['BBL_20_2.0'] - 1

    #         if (timeframe == '1min') or (timeframe == '1hour'):
    #             train, test = train_test_split(df, test_size=0.25, random_state=1104)
    #         else:
    #             _date = (datetime.now() - timedelta(days=365)).date().strftime('%Y-%m-%d')
    #             train = df[df['date'] < _date]
    #             test = df[df['date'] >= _date]

    #     return train, test, df

    
    # # Define fitness function to be used by the PyGAD instance
    # def fitness_func(self, solution, sol_idx):
    #     try:
    #         # total reward 가 최대값을 갖을 수 있는 solution[0],[1],[2] 의 변수들을 찾아서 최적화(=> pygad.GA()를 통해서)
    #         total_reward, _, _ = get_result(train, solution[0], solution[1], solution[2])
    #     except:
    #         reward = 0
    #         pass
    #     # Return the solution reward
    #     return total_reward

    # # Define a reward function
    # def get_result(df, min_volatility, max_buy_pct, min_sell_pct):
    #     # Generate a copy to avoid changing the original data
    #     df = df.copy().reset_index(drop=True)

    #     # Buy Signal
    #     df['signal'] = np.where((df['volatility'] > min_volatility) & (df['close_percentage'] < max_buy_pct), 1, 0)
    #     # Sell Signal
    #     df['signal'] = np.where((df['close_percentage'] > min_sell_pct), -1, df['signal'])

    #     # Remove all rows without operations, rows with the same consecutive operation, first row selling, and last row buying
    #     result = df[df['signal'] != 0]
    #     result = result[result['signal'] != result['signal'].shift()]
    #     if (len(result) > 0) and (result.iat[0, -1] == -1): result = result.iloc[1:]
    #     if (len(result) > 0) and (result.iat[-1, -1] == 1): result = result.iloc[:-1]

    #     # Calculate the reward / operation
    #     result['total_reward'] = np.where(result['signal'] == -1, result['close'] - result['close'].shift(), 0)

    #     # Generate the result
    #     total_reward = result['total_reward'].sum()
    #     wins = len(result[result['total_reward'] > 0])
    #     losses = len(result[result['total_reward'] < 0])

    #     return total_reward, wins, losses
    

    # # vb_genericAlgo_strategy main function
    # for timeframe in TIMEFRAMES:
    #     try:
    #         # Get Train and Test data for timeframe
    #         train, test, df = get_data(timeframe)
    #         # Process timeframe
    #         base.log_report.info(f" vb_genericAlgo_strategy: {ticker} / {timeframe} ".center(60, "*"))
    #     except KeyError as e: # 히스토리 레코드가 1건이라 볼린저밴드 20 을 만들수 없음.
    #         base.log_batch.error(f"vb_genericAlgo_strategy Key Error ({ticker} / {timeframe}): {e}")
    #         base.log_batch.error(f"vb_genericAlgo_strategy Key Error ({ticker} / {timeframe}): {e}")
    #         continue
    #     except Exception as e:
    #         base.log_batch.error(f"vb_genericAlgo_strategy Error ({ticker} / {timeframe}): {e}")
    #         base.log_batch.error(f"vb_genericAlgo_strategy Error ({ticker} / {timeframe}): {e}")

    #     with tqdm(total=GENERATIONS) as pbar:
    #         # Create Genetic Algorithm
    #         ga_instance = pygad.GA(num_generations=GENERATIONS,
    #                             num_parents_mating=5,
    #                             fitness_func=fitness_func,
    #                             sol_per_pop=POPULATIONS,
    #                             num_genes=3,
    #                             gene_space=[{'low': 0, 'high':1}, {'low': 0, 'high':1}, {'low': 0, 'high':1}],
    #                             parent_selection_type="sss",
    #                             crossover_type="single_point",
    #                             mutation_type="random",
    #                             mutation_num_genes=1,
    #                             keep_parents=-1,
    #                             on_generation=lambda _: pbar.update(1),
    #                             )
    #         # Run the Genetic Algorithm
    #         ga_instance.run()


    #     # log_report.info 정보가 너무 많아 TEST 결과 승률이 80% 이상인 경우만 display 하기 위하여 일부 display 순서 변경 20240122
    #     try:
    #         # Show details of the best solution.
    #         solution, solution_fitness, _ = ga_instance.best_solution()

    #         # Get Reward from test data
    #         profit, wins, losses = get_result(test, solution[0], solution[1], solution[2])

    #         win_rate = (wins/(wins + losses) if wins + losses > 0 else 0) * 100
    #         if win_rate >= 80 and profit > 1200000:
    #             # 최적 변수값 찾기
    #             base.log_report.info(f' Volatility & Bollinger Band with Generic Algorithm Strategy: {ticker} Best Solution Parameters for {timeframe} Timeframe '.center(60, '*'))      
    #             base.log_report.info(f"Min Volatility   : {solution[0]:6.4f}")
    #             base.log_report.info(f"Max Perc to Buy  : {solution[1]:6.4f}")
    #             base.log_report.info(f"Min Perc to Sell : {solution[2]:6.4f}")

    #             # Show the final result
    #             base.log_report.info(f'***** {ticker} Result for timeframe {timeframe} (TEST) ')
    #             base.log_report.info(f'* Profit / Loss (B&H)      : {(test["close"].iloc[-1] - test["close"].iloc[0]) * (CASH // test["close"].iloc[0]):.2f}')
    #             base.log_report.info(f"* Profit / Loss (Strategy) : {profit:.2f}")
    #             base.log_report.info(f"* Wins / Losses  : {wins} / {losses}")
    #             base.log_report.info(f"* Win Rate       : {(100 * (wins/(wins + losses)) if wins + losses > 0 else 0):.2f}%")
    #             base.log_report.info("")

    #             # graph @@@ 값 검증 추가 필요: 20240128
    #             graph = df.copy().reset_index(drop=True)
    #             graph = graph.sort_values(by='date')
    #             graph['date'] = pd.to_datetime(graph['date'])

    #             '''
    #             sells, buys, buf, buf2 .... 좀 더 주의깊게 재검증이 필요함. 일단 기능상 충족으로 넘어감. 20240128
    #             '''
    #             sells = graph[graph['close_percentage'] > 95]   # Selling Point
    #             buys = graph[graph['close_percentage'] < 5]   # Buying Point

    #             # graph 에서 sells를 뺀 나머지 구하기
    #             buf = pd.merge(graph, sells, how='outer', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1)
    #             # graph 에서 buys를 뺀 나머지 구하기
    #             buf2 = pd.merge(graph, buys, how='outer', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1) 
    #             # print(buf)

    #             plt.figure(figsize=(18, 6))
    #             plt.plot(graph['date'][-60:], graph['close'][-60:], label='주가', color='black')
    #             plt.plot(graph['date'][-60:], graph['high_limit'][-60:], label='상단 볼린저 밴드', linestyle='--', color='red')
    #             plt.plot(graph['date'][-60:], graph['low_limit'][-60:], label='하단 볼린저 밴드', linestyle='--', color='green')
    #             plt.scatter(buf['date'][-1:], buf['close'][-1:], color='red', label='Selling Point') # 특정 일자에 추가적인 점 플로팅
    #             plt.scatter(buf2['date'][-1:], buf2['close'][-1:], color='green', label='Buying Point') # 특정 일자에 추가적인 점 플로팅                
    #             # 그래프에 제목과 레이블 추가
    #             plt.title(f'Volatility({solution[0]:6.2f}) & BB with GA Strategy: Reward ({profit:.0f}), Wins/Losses ({wins:.0f}/{losses:.0f}), Win Rate ({win_rate:.2f}%)')
    #             plt.xlabel('날짜')
    #             plt.ylabel('가격')
    #             plt.grid()
    #             plt.legend()

    #             plt.savefig(base.reports_dir + f'/global_s0100_{ticker}_{timeframe}.png')

    #             # Get Reward from train data
    #             profit, wins, losses = get_result(train, solution[0], solution[1], solution[2])
    #             base.log_report.info(f'***** {ticker} Result for timeframe {timeframe} (TRAIN) ')
    #             base.log_report.info(f'* Profit / Loss (B&H)      : {(train["close"].iloc[-1] - train["close"].iloc[0]) * (CASH // train["close"].iloc[0]):.2f}')
    #             base.log_report.info(f"* Profit / Loss (Strategy) : {profit:.2f}")
    #             base.log_report.info(f"* Wins / Losses  : {wins} / {losses}")
    #             base.log_report.info(f"* Win Rate       : {win_rate:.2f}%")
    #             if timeframe == '1day':
    #                 result = timeframe
    #         else:
    #             pass
    #     except Exception as e:
    #         base.log_batch.error(' >>> Exception4: {}'.format(e))

    # return result



'''
Main Fuction
'''

if __name__ == "__main__":

    # buf = df_strg
    # print(buf)
    print('------')
    for nation, assets in WATCH_TICKERS2.items():  # 국가별

        # if nation in ['EU']:  # 몇 가지 정보가 존재하지 않아 제외
        #     continue
        log_report.info(f' {nation}')
        for asset_grp in assets:  # 국가별 / 자산별 /

            for asset, tickers in asset_grp.items():  # 리스트에서 키와 아이템 분리용 => 딕셔너리 of 리스트 형태 자료구조론임.

                for ticker in tickers:  # 국가별 / 자산별 / ETF별

                    if ticker == '':
                        continue
                    # settings.py 에서 get_stock_history_by_fmp with timeframe 파일 만들어 줌.
                    log_report.info('')
                    log_report.info(f' ##### {ticker}')

                    df = mi.get_stock_history_by_fmp(ticker, TIMEFRAMES)
                    if df.empty:  # fmp 에서 읽지 못하면 다음에는 yfinance 에서 읽도록 보완함. 
                        log_batch.error(f'{ticker} df by fmp is empty')

                        df = mi.get_stock_history_by_yfinance(ticker, TIMEFRAMES)
                        
                        log_report.info("dataframe from yfinance")
                        log_report.info(df.tail())
                    
                    # try:  # Type Error: 530107.KS
                    #     # chagnge_date 날짜가 있으면 투자 적격으로 판단
                    #     change_date, change_rate = mi.timing_strategy(ticker, 20, 200) # 200일 이평 vs 20일 이평
                    # except TypeError as e:
                    #     change_date = None
                    #     change_rate = None                        
                    #     log_batch.error(f'timing strategy can not make ema : {ticker}')

                    # # win_result_vb = '1day' 받으면 투자 적격으로 판단
                    # win_result_vb = mi.volatility_bollinger_strategy(ticker, TIMEFRAMES) # 임계값 찾는 Generic Algorithm 보완했음.
                    # # win_result_vbg = '1day' 받으면 투자 적격으로 판단
                    start = perf_counter()
                    win_result_vbg = mi.vb_genericAlgo_strategy(ticker, TIMEFRAMES) # Bolinger Band Strategy + 임계값 찾는 Generic Algorithm       
                    end = perf_counter()
                    time_ga = end - start
                    print(f"time_ga: {time_ga}")

                    start = perf_counter()
                    win_result_vbg = keras_genericAlgo_strategy(ticker, TIMEFRAMES)
                    end = perf_counter()
                    time_keras = end - start
                    print(f"time_keras: {time_keras}")
                    # win_result_vbg2 = '1day' 받으면 투자 적격으로 판단
                    # win_result_vbg2 = mi.vb_genericAlgo2_strategy(ticker, TIMEFRAMES) # Bolinger Band Strategy + 임계값 찾는 Generic Algorithm           
                    # # win_result_rv = '1day' 받으면 투자 적격으로 판단
                    # win_result_rv = mi.reversal_strategy(ticker, TIMEFRAMES) 
                    # # win_result_tf = 'BUY' 받으면 투자 적격으로 판단
                    # win_result_tf = mi.trend_following_strategy(ticker, TIMEFRAMES)  # 단기 매매 아님. 중장기 매매 기법, 1day 데이터만으로 실행
                    # # win_result_cc = 매수 추천한 숫자로 투자적격 판단
                    # win_result_cc = mi.control_chart_strategy(ticker)
                    # # win_result_gshb = '1day' 받으면 투자 적격으로 판단
                    # win_result_gshb = mi.gaSellHoldBuy_strategy(ticker)

                    print('=== Strategy Simulation End ===')

                    buf['Country'] = [nation]
                    buf['Market'] = [asset]
                    buf['Busi'] = [ticker]
                
                    # if change_date != None:
                    #     buf['timing'] = [1]
                    # else:
                    #     buf['timing'] = [0]
                        
                    # if win_result_vb == '1day':
                    #     buf['volatility_bollinger'] = [1]
                    # else:
                    #     buf['volatility_bollinger'] = [0]

                    if win_result_vbg == '1day':
                        buf['vb_genericAlgo'] = [1]
                    else:
                        buf['vb_genericAlgo'] = [0]

                    # if win_result_vbg2 == '1day':
                    #     buf['vb_genericAlgo2'] = [1]
                    # else:
                    #     buf['vb_genericAlgo2'] = [0]

                    # if win_result_rv == '1day':
                    #     buf['reversal'] = [1]
                    # else:
                    #     buf['reversal'] = [0]

                    # if win_result_tf == 'BUY':
                    #     buf['trend_following'] = [1]
                    # else:
                    #     buf['trend_following'] = [0]

                    # buf['control_chart'] = [win_result_cc]

                    # if win_result_gshb == '1day':
                    #     buf['gaSellHoldBuy'] = [1]
                    # else:
                    #     buf['gaSellHoldBuy'] = [0]
                    print(buf)
                    df_strg = pd.concat([df_strg, buf], axis=0)

                    sleep(2)

    print(df_strg)
    make_strategy(df_strg)  # Strg 테이블 구성작업