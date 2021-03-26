from upbit_helpers import *

import time

def load_candidates(candidates, refresh = False):
    if not refresh:
        assert len(candidates) == 0
    r = requests.get('https://api.upbit.com/v1/market/all')
    pairs = json.loads(r.content.decode('utf-8'))
    for it in pairs:
        symbol = it['market']
        base_currency = symbol[:symbol.find('-')] # KRW-XRP 이런 이름에서 '-'를 찾아 그 앞부분을 취한다.
        if base_currency != 'KRW': # KRW 기반이 아닌 건 스킵
            continue
        if refresh:
            if symbol not in candidates:
                print('@@@@@@@@@@@@@@@@@@@@ DEBUT OF {} {} {} !!!!!'.format(symbol, it['korean_name'], it['english_name']))
                candidates.append(symbol)
        else:
            assert symbol not in candidates
            print('{} {} {}'.format(symbol, it['korean_name'], it['english_name']))
            candidates.append(symbol)

def get_milliseconds(interval_name):
    unit = interval_name[-1:]
    amount = int(interval_name[0:-1])
#     log(unit, amount)
    if unit == 'm':
        return amount * 1000 * 60
    elif unit == 'h':
        return amount * 1000 * 60 * 60
    elif unit == 'D':
        return amount * 1000 * 60 * 60 * 24

# import matplotlib.pyplot as plt
# import matplotlib.gridspec as gridspec

# def mask_h(plt, x1, x2, min_y, max_y, color, alpha):
#     return plt.Rectangle((x1, min_y), x2 - x1, max_y - min_y, linewidth=0, alpha=alpha, edgecolor=color, facecolor=color)

# from mplfinance.original_flavor import plot_day_summary_ohlc
# from mplfinance.original_flavor import candlestick2_ohlc

# import colorsys

# def highlight_candle(ax, plt, i, dates, span_minutes, min_y, max_y, color):
#     ax.add_patch(mask_h(plt, dates[i] - (span_minutes/(24*60)/2), dates[i] + (span_minutes/(24*60)/2), min_y, max_y, color, 1.0))

# def draw(data, trends, price, ax, begin, end, i):
#     tic = time.perf_counter()

#     span_minutes = (data[1,0] - data[0,0]) / 60
#     print(span_minutes)

#     open = data[i,1]
#     close = data[i,2]
#     center = (open + close) / 2
#     min_y = center / 1.1
#     max_y = center * 1.1
#     # min_y = min(self.segment[begin:i,4])
#     # max_y = max(self.segment[begin:i,3])

#     plt.xticks([trends['dates'][i]], rotation=0)
#     ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
#     ax.set_ylim(bottom = min_y, top = max_y)

#     # for j in range(trends['sma5.maximas'].shape[1]):
#     #     if j >= begin and j < end:
#     #         highlight_candle(ax, plt, trends['sma5.maximas'][0,j], trends['dates'], span_minutes, min_y, max_y, 'red')

#     for j in range(len(trends['sma5.minimas'])):
#         k = trends['sma5.minimas'][j]
#         if k >= begin and k < end:
#             highlight_candle(ax, plt, k, trends['dates'], span_minutes, min_y, max_y, 'cyan')

#     highlight_candle(ax, plt, i, trends['dates'], span_minutes, min_y, max_y, 'yellow')

#     plot_day_summary_ohlc(ax, trends['ohlc'][begin:end])

#     # ax.plot(trends['hsma40'][trends['dates'][begin]:trends['dates'][end]], color = 'blue', linewidth = 2, label='High, 40-Day SMA')
#     # ax.plot(trends['lsma40'][trends['dates'][begin]:trends['dates'][end]], color = 'blue', linewidth = 2, label='Low, 40-Day SMA')
#     # ax.plot(trends['ema15'][trends['dates'][begin]:trends['dates'][end]], color = 'red', linestyle='--', linewidth = 2, label='Close, 15-Day EMA')
#     # ax.plot(trends['ema5'][trends['dates'][begin]:trends['dates'][end]], color = 'green', linestyle='--', linewidth = 2, label='Close, 5-Day EMA')

#     ax.plot(trends['sma5'][trends['dates'][begin]:trends['dates'][end]], color = 'magenta', linewidth = 1, label='5')
#     ax.plot(trends['sma10'][trends['dates'][begin]:trends['dates'][end]], color = 'navy', linewidth = 1, label='10')
#     ax.plot(trends['sma20'][trends['dates'][begin]:trends['dates'][end]], color = 'orange', linewidth = 1, label='20')
#     ax.plot(trends['sma60'][trends['dates'][begin]:trends['dates'][end]], color = 'red', linewidth = 1, label='60')
#     ax.plot(trends['sma120'][trends['dates'][begin]:trends['dates'][end]], color = 'grey', linewidth = 1, label='120')

#     # for index, value in trends['sma20.diff.diff'].items():
#     #     if math.isnan(value):
#     #         value = 0
#     #     print(index, value)
#     #     # saturation = math.log(abs(value) * 100) * 0.3 if value != 0 else 0
#     #     saturation = value * 1000
#     #     saturation = abs(saturation) if abs(saturation) < 1.0 else 1.0
#     #     saturation = math.sqrt(math.sqrt(saturation))
#     #     saturation = saturation * 0.3
#     #     if value > 0:
#     #         color = colorsys.hsv_to_rgb(0.3, saturation, 1.0)
#     #     else:
#     #         color = colorsys.hsv_to_rgb(1.0, saturation, 1.0)
#     #     ax.add_patch(mask_h(plt, index - (span_minutes/(24*60)/2), index + (span_minutes/(24*60)/2), min_y, max_y, color, 1.0))

#     plt.axhline(price, color='red')

#     toc = time.perf_counter()
#     print('{:.3f} ms'.format((toc - tic) * 1000))

# from scipy.signal import argrelextrema

# def get_maximas(trend):
#     # print(trend.fillna(0).to_numpy())
#     return np.asarray(argrelextrema(trend.fillna(0).to_numpy(), np.greater_equal, order = 5))

# def get_minimas(trend):
#     # print(trend.fillna(0).to_numpy())
#     return np.asarray(argrelextrema(trend.fillna(0).to_numpy(), np.less_equal, order = 5))

import matplotlib.dates as mdates

import pandas as pd
class Chart:
    def __init__(self):
        self.data = {}
        self.trends = {}

    def update_data(self, type, data):
        self.data[type] = data

    def update_trends(self, type):
        self.trends[type] = {}
        trends = self.trends[type]
        data = self.data[type]

        trends['dates'] = mdates.date2num([datetime.datetime.fromtimestamp(data[i,0]) for i in range(data.shape[0])])
        trends['ohlc'] = [[trends['dates'][i], data[i,1], data[i,3], data[i,4], data[i,2]] for i in range(data.shape[0])]

        # numpy array를 pandas DataFrame으로 바꾸면 pandas에서 제공하는 보다 편리한 기능들(아래 rolling, ewm 등)을 활용할 수 있다.
        trends['dataframe'] = pd.DataFrame(data=data[:,1:6], index=trends['dates'], columns=['open', 'close', 'high', 'low', 'volume'])

        # pandas DataFrame은 이런식으로 index 번호가 아닌, 위에서 columns 파라미터로 지정된 label로 각 column을 지정한다.
        # trends['hsma40'] = trends['dataframe']['high'].rolling(40).mean()
        # trends['lsma40'] = trends['dataframe']['low'].rolling(40).mean()
        # trends['ema15'] = trends['dataframe']['close'].ewm(15).mean()
        # trends['ema5'] = trends['dataframe']['close'].ewm(5).mean()

        trends['sma5'] = trends['dataframe']['close'].rolling(5).mean() # .rolling(3).mean().rolling(3).mean()
        trends['sma10'] = trends['dataframe']['close'].rolling(10).mean() # .rolling(3).mean().rolling(3).mean()
        trends['sma20'] = trends['dataframe']['close'].rolling(20).mean() # .rolling(3).mean().rolling(3).mean()
        trends['sma60'] = trends['dataframe']['close'].rolling(60).mean() # .rolling(3).mean().rolling(3).mean()
        trends['sma120'] = trends['dataframe']['close'].rolling(120).mean() # .rolling(3).mean().rolling(3).mean()
        trends['sma5v'] = trends['dataframe']['volume'].rolling(5).mean() # .rolling(3).mean().rolling(3).mean()
        trends['sma10v'] = trends['dataframe']['volume'].rolling(10).mean() # .rolling(3).mean().rolling(3).mean()
        trends['sma20v'] = trends['dataframe']['volume'].rolling(20).mean() # .rolling(3).mean().rolling(3).mean()
        trends['sma60v'] = trends['dataframe']['volume'].rolling(60).mean() # .rolling(3).mean().rolling(3).mean()
        trends['sma120v'] = trends['dataframe']['volume'].rolling(120).mean() # .rolling(3).mean().rolling(3).mean()

        # trends['sma5r20'] = trends['sma5'] - trends['sma20']
        # trends['sma10r20'] = trends['sma10'] - trends['sma20']

        trends['sma5.diff'] = trends['sma5'].diff() / trends['sma5'].shift(1) + 1
        trends['sma10.diff'] = trends['sma10'].diff() / trends['sma10'].shift(1) + 1
        trends['sma20.diff'] = trends['sma20'].diff() / trends['sma20'].shift(1) + 1
        trends['sma60.diff'] = trends['sma60'].diff() / trends['sma60'].shift(1) + 1
        trends['sma120.diff'] = trends['sma120'].diff() / trends['sma120'].shift(1) + 1
        trends['sma5v.diff'] = trends['sma5v'].diff() / trends['sma5v'].shift(1) + 1
        trends['sma10v.diff'] = trends['sma10v'].diff() / trends['sma10v'].shift(1) + 1
        trends['sma20v.diff'] = trends['sma20v'].diff() / trends['sma20v'].shift(1) + 1
        trends['sma60v.diff'] = trends['sma60v'].diff() / trends['sma60v'].shift(1) + 1
        trends['sma120v.diff'] = trends['sma120v'].diff() / trends['sma120v'].shift(1) + 1

        # trends['sma5r20.diff'] = trends['sma5r20'].diff() / trends['sma5r20'] + 1
        # trends['sma10r20.diff'] = trends['sma10r20'].diff() / trends['sma10r20'] + 1

        # trends['sma5.diff'] = trends['sma5.diff'].rolling(3).mean()
        # trends['sma10.diff'] = trends['sma10.diff'].rolling(3).mean()
        # trends['sma20.diff'] = trends['sma20.diff'].rolling(3).mean()
        # trends['sma60.diff'] = trends['sma60.diff'].rolling(3).mean()
        # trends['sma120.diff'] = trends['sma120.diff'].rolling(3).mean()

        trends['sma5.diff.diff'] = (trends['sma5'] / trends['sma5'].shift(1)) / (trends['sma5'] / trends['sma5'].shift(1)).shift(1)
        trends['sma10.diff.diff'] = (trends['sma10'] / trends['sma10'].shift(1)) / (trends['sma10'] / trends['sma10'].shift(1)).shift(1)
        trends['sma20.diff.diff'] = (trends['sma20'] / trends['sma20'].shift(1)) / (trends['sma20'] / trends['sma20'].shift(1)).shift(1)
        trends['sma60.diff.diff'] = (trends['sma60'] / trends['sma60'].shift(1)) / (trends['sma60'] / trends['sma60'].shift(1)).shift(1)
        trends['sma120.diff.diff'] = (trends['sma120'] / trends['sma120'].shift(1)) / (trends['sma120'] / trends['sma120'].shift(1)).shift(1)
        trends['sma5v.diff.diff'] = (trends['sma5v'] / trends['sma5v'].shift(1)) / (trends['sma5v'] / trends['sma5v'].shift(1)).shift(1)
        trends['sma10v.diff.diff'] = (trends['sma10v'] / trends['sma10v'].shift(1)) / (trends['sma10v'] / trends['sma10v'].shift(1)).shift(1)
        trends['sma20v.diff.diff'] = (trends['sma20v'] / trends['sma20v'].shift(1)) / (trends['sma20v'] / trends['sma20v'].shift(1)).shift(1)
        trends['sma60v.diff.diff'] = (trends['sma60v'] / trends['sma60v'].shift(1)) / (trends['sma60v'] / trends['sma60v'].shift(1)).shift(1)
        trends['sma120v.diff.diff'] = (trends['sma120v'] / trends['sma120v'].shift(1)) / (trends['sma120v'] / trends['sma120v'].shift(1)).shift(1)

        # trends['sma5r20.diff.diff'] = trends['sma5r20.diff'].diff() / trends['sma5r20.diff'] + 1
        # trends['sma10r20.diff.diff'] = trends['sma10r20.diff'].diff() / trends['sma10r20.diff'] + 1

        # trends['sma5.diff.diff'] = trends['sma5.diff.diff'].rolling(2).mean()
        # trends['sma10.diff.diff'] = trends['sma10.diff.diff'].rolling(2).mean()
        # trends['sma20.diff.diff'] = trends['sma20.diff.diff'].rolling(2).mean()
        # trends['sma60.diff.diff'] = trends['sma60.diff.diff'].rolling(2).mean()
        # trends['sma120.diff.diff'] = trends['sma120.diff.diff'].rolling(2).mean()

        # trends['sma5.maximas'] = get_maximas(trends['dates'], trends['sma5.diff'], trends['sma5.diff.diff'])
        # trends['sma10.maximas'] = get_maximas(trends['dates'], trends['sma10.diff'], trends['sma10.diff.diff'])
        # trends['sma20.maximas'] = get_maximas(trends['dates'], trends['sma20.diff'], trends['sma20.diff.diff'])
        # trends['sma60.maximas'] = get_maximas(trends['dates'], trends['sma60.diff'], trends['sma60.diff.diff'])
        # trends['sma120.maximas'] = get_maximas(trends['dates'], trends['sma120.diff'], trends['sma120.diff.diff'])
        # trends['sma5r20.maximas'] = get_maximas(trends['dates'], trends['sma5r20.diff'], trends['sma5r20.diff.diff'])

        # trends['sma5.minimas'] = get_minimas(trends['dates'], trends['sma5.diff'], trends['sma5.diff.diff'])
        # trends['sma10.minimas'] = get_minimas(trends['dates'], trends['sma10.diff'], trends['sma10.diff.diff'])
        # trends['sma20.minimas'] = get_minimas(trends['dates'], trends['sma20.diff'], trends['sma20.diff.diff'])
        # trends['sma60.minimas'] = get_minimas(trends['dates'], trends['sma60.diff'], trends['sma60.diff.diff'])
        # trends['sma120.minimas'] = get_minimas(trends['dates'], trends['sma120.diff'], trends['sma120.diff.diff'])
        # trends['sma5r20.minimas'] = get_minimas(trends['dates'], trends['sma5r20.diff'], trends['sma5r20.diff.diff'])

        # trends['sma120.diff'] = trends['sma120'].diff() / trends['sma120']

    def need_update(self, type):
        # return True
        if type not in self.data:
            return True
        now = time.time()
        last_candle_timestamp = self.data[type][-1,TIMESTAMP_INDEX]
        seconds_elapsed_since_last_candle_begin = now - last_candle_timestamp
        interval_seconds = get_milliseconds(type) / 1000
        if interval_seconds * 2 - seconds_elapsed_since_last_candle_begin < 60:
            print('{} {:.0f}'.format(str(datetime.datetime.fromtimestamp(last_candle_timestamp)), seconds_elapsed_since_last_candle_begin))
            return True
        return False
    
    # def draw(self, type, ax, price, begin, end, i):
    #     draw(self.data[type], self.trends[type], price, ax, begin, end, i)

async def update_charts(candidates, charts, type, action = None, service = None, loop = None):
    stale_count = 0
    stale_list = ''
    updated_count = 0
    for symbol in candidates:
        if symbol not in charts:
            charts[symbol] = Chart()
        chart = charts[symbol]
        if not chart.need_update(type):
            continue
        stale_count += 1
        if type[-1] == 'D':
            candles = get_day_candle(symbol)
        elif type[-1] == 'm':
            candles = get_minute_candle(symbol, type[:-1])
        chart.update_data(type, get_standard_minute_candles_history_upbit(candles))
        chart.update_trends(type)
        dt = candles[0]['candle_date_time_kst']
        timestamp = int(datetime.datetime(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]), int(dt[11:13]), int(dt[14:16]), int(dt[17:19])).timestamp())
        last_candle = [timestamp, candles[0]['opening_price'], None, candles[0]['high_price'], candles[0]['low_price'], candles[0]['candle_acc_trade_volume'], candles[0]['candle_acc_trade_price'], None, None, None]
        if not chart.need_update(type):
            updated_count += 1
            # if action is not None:
            #     await action(service, symbol, type, last_candle, loop)
        else:
            stale_list += symbol + ' '
        if action is not None:
            await action(service, symbol, type, last_candle, loop)
        print(type, symbol)
        await asyncio.sleep(0)
    remaining_stale_count = stale_count - updated_count
    now = time.time()
    print('{:>3} {} {:>3}/{:>3} {}'.format(type, datetime.datetime.utcfromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S'), updated_count, stale_count,
        stale_list if remaining_stale_count <= 20 else '({})'.format(remaining_stale_count)))

# max_snapshots = 10

# async def test(service, symbol, type, *_):
#     chart = charts[symbol]

#     past_size = 30
#     future_size = 20

#     snapshots_count = 0

#     for i in range(past_size, chart.data[type].shape[0] - future_size):
#         last_candle = chart.data[type][i]
#         if not service.history_condition(chart, i):
#             continue
#         if not service.this_candle_condition(last_candle, chart, i):
#             continue
#         if snapshots_count == 0:
#             fig = plt.figure(figsize=(20 * max_snapshots, 7))
#             gs_all = gridspec.GridSpec(1, max_snapshots, figure=fig)
#         if snapshots_count < max_snapshots:
#             ax = fig.add_subplot(gs_all[0, snapshots_count])
#             chart.draw(type, ax, last_candle[OPEN_INDEX], i - past_size, i + future_size, i)
#             snapshots_count += 1
#         print(symbol)
#         print(stringify_standard_candle(chart.data[type][i - 4]))
#         print(stringify_standard_candle(chart.data[type][i - 3]))
#         print(stringify_standard_candle(chart.data[type][i - 2]))
#         print(stringify_standard_candle(chart.data[type][i - 1]))
#         print(stringify_standard_candle(chart.data[type][i], bcolors.OKGREEN if chart.data[type][i, PRICE_HIGH_RATIO_INDEX] * 100 > 3 else bcolors.FAIL))
#         print(stringify_standard_candle(chart.data[type][i + 1]))
#         print(stringify_standard_candle(chart.data[type][i + 2]))
#         print(stringify_standard_candle(chart.data[type][i + 3]))

#     if snapshots_count > 0:
#         print('Rendering...')
#         try:
#             os.mkdir('output')
#         except OSError:
#             pass
#         fig.savefig("output/upbit-{}-{}.png".format(symbol, type), bbox_inches='tight', dpi=100)
#         plt.close(fig)
#         print('done')

def cancel_all_sell_orders(symbol = None):
    while True:
        unfulfilled_orders = get_orders('wait', symbol)
        n = 0
        for order in unfulfilled_orders:
            if order['side'] != 'ask':
                continue
            if order['ord_type'] != 'limit':
                continue
            n += 1
            uuid = order['uuid']
            print('매도 주문 취소: ', order['uuid'], order['side'], order['market'], order['price'], order['remaining_volume'], order['executed_volume'], order['paid_fee'])
            data = cancel_order(uuid)
            # print(data)
            if 'error' in data:
                print(data)
        if n == 0:
            break

upbit_min_trade_amount_krw = 5000
enforce_sell_last_timestamp = 0

def enforce_sell(interval_minutes, unit_sell_amount_krw, upbit_min_trade_amount_with_buffer_krw, default_profit_ratio_min, default_profit_ratio_max):
    assert upbit_min_trade_amount_with_buffer_krw > upbit_min_trade_amount_krw
    global enforce_sell_last_timestamp
    now = time.time()
    if now - enforce_sell_last_timestamp < interval_minutes * 60:
        return
    # unfulfilled_orders = get_orders('wait')
    # print('=====================================================================')
    # print('미체결 주문:')
    # for it in unfulfilled_orders:
    #     print(it['uuid'], it['side'], it['market'], it['price'], it['remaining_volume'], it['executed_volume'], it['paid_fee'])
    print('=====================================================================')
    print('청산 오더 없는 잔고:')
    free_balances = get_free_balances()
    todolist = []
    for symbol in free_balances:
        it = free_balances[symbol]
        print('{:<10} {:>18.9f} {:>11.2f}'.format(symbol, it['amount'], it['price']))
        todolist.append([symbol, it['amount'] * it['price'], it['amount'], it['price']])
    todolist.sort(key=lambda x: x[1], reverse=True)
    print('=====================================================================')
    print('모든 코인 잔고에 대해 일괄로 {}원 단위 청산 주문 깔아놓기:'.format(unit_sell_amount_krw))
    for it in todolist:
        symbol = it[0]
        amount = it[2]
        price = it[3]
        n = math.floor(amount * price / unit_sell_amount_krw)
        if amount * price < upbit_min_trade_amount_krw:
            print('{:<10} 잔고 {:>11}원 어치 (평균매수단가 기준) - 매도 불가!'.format(symbol, int(amount * price)))
            continue
        print('{:<10} 잔고 {:>11}원 어치 (평균매수단가 기준) {:>4}분할 매도'.format(symbol, int(amount * price), n))
        remaining_amount = amount
        if n > 0:
            a1 = unit_sell_amount_krw / price
            expected_remainder = amount - n * a1
            remainder_big_enough = expected_remainder * price > upbit_min_trade_amount_with_buffer_krw # 짜투리가 가격이 좀 내려도 자체적으로 청산 가능한 크기
            price_ratio_step = (default_profit_ratio_max - default_profit_ratio_min) / max(n - 1, 1)
            for i in range(n if remainder_big_enough else n - 1):
                p1 = round_up_to_unit(price * (default_profit_ratio_max - i * price_ratio_step), get_upbit_krw_price_unit)
                print('청산 주문: {:<10} {:>18.9f} {:>11.2f}'.format(symbol, a1, p1))
                data2 = post_limit_order(symbol, -a1, p1)
                # if 'error' in data2:
                #     print(data2)
                remaining_amount -= a1
        else:
            assert amount * price >= upbit_min_trade_amount_krw
            remainder_big_enough = True
        if remainder_big_enough:
            print('* 짜투리는 별도 처리 (평균매수단가 기준 {}원 어치)'.format(int(remaining_amount * price)))
            # print('* 짜투리는 언제든 시장가 청산할 수 있도록 남겨둠  (평균매수단가 기준 {}원 어치)'.format(int(remaining_amount * price)))
        else:
            print('* 잔여 1회분은 짜투리를 붙여서 별도 처리 (평균매수단가 기준 {}원 어치)'.format(int(remaining_amount * price)))
            # print('* 잔여 1회분은 짜투리를 붙여서 언제든 시장가 청산할 수 있도록 남겨둠 (평균매수단가 기준 {}원 어치)'.format(int(remaining_amount * price)))
    free_balances = get_free_balances()
    todolist = []
    for symbol in free_balances:
        it = free_balances[symbol]
        # print('{:<10} {:>18.9f} {:>11.2f}'.format(symbol, it['amount'], it['price']))
        todolist.append([symbol, it['amount'] * it['price'], it['amount'], it['price']])
    todolist.sort(key=lambda x: x[1], reverse=True)
    print('=====================================================================')
    print('잔여분 오더:')
    for it in todolist:
        symbol = it[0]
        amount = it[2]
        price = it[3]
        if amount * price < upbit_min_trade_amount_krw:
            print('{:<10} 잔고 {:>11}원 어치 (평균매수단가 기준) - 매도 불가!'.format(symbol, int(amount * price)))
            continue
        print('{:<10} 잔고 {:>11}원 어치 (평균매수단가 기준)'.format(symbol, int(amount * price)))
        a1 = -amount
        p1 = round_up_to_unit(price * default_profit_ratio_min, get_upbit_krw_price_unit)
        print('청산 주문: {:<10} {:>18.9f} {:>11.2f}'.format(symbol, a1, p1))
        data2 = post_limit_order(symbol, a1, p1)
        # if 'error' in data2:
        #     print(data2)
    print('=====================================================================')
    print('여전히 청산에서 배제된 짜투리 잔고:')
    free_balances = get_free_balances()
    for symbol in free_balances:
        it = free_balances[symbol]
        print('{:<10} {:>18.9f} {:>11.2f}'.format(symbol, it['amount'], it['price']))
    enforce_sell_last_timestamp = now

def free_up_balance_amount_for_minimum_market_sell():
    pass

decay_ratio = 0.5
sensitivity_exponent = 40

def decay_sell_orders(charts, decay_base_interval_minutes, service, symbol = None):
    unfulfilled_orders = get_orders('wait', 100, symbol)
    # print(unfulfilled_sell_orders)
    for order in unfulfilled_orders:
        if order['side'] != 'ask':
            continue
        if order['ord_type'] != 'limit':
            continue
        uuid = order['uuid']
        symbol = order['market']
        price = float(order['price'])
        amount = float(order['remaining_volume'])
        timestamp = datetime.datetime.strptime(order['created_at'], '%Y-%m-%dT%H:%M:%S%z')
        # print(order)
        last = charts[symbol].data['1m'][-1,CLOSE_INDEX]
        now = time.time()
        age_minutes = (now - timestamp.timestamp()) / 60
        # print('{} {:<10} {:>18.9f} {:>11} {:>11} {:>6.2f}% {} {} {:>3}:{:0>2}'.format(
        #     uuid, symbol, amount, price, last, distance * 100 - 100,
        #     timestamp, timestamp.strftime('%Y-%m-%d %H:%M:%S %Z'), ))
        print('========================================================================================================================================')
        print('{:<9} 현재 {:>14.2f} KRW           {:>11}'.format(symbol, last, datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')))
        print('대상 매도 주문 {:>14.2f} KRW ({:>6.1f}×) {:>11} {:<12} {:>18.9f} {}'.format(
            price, price / last, timestamp.strftime('%Y-%m-%d %H:%M:%S'), '({}:{:0>2} 경과)'.format(int(age_minutes / 60), int(age_minutes % 60)), amount, uuid))
        narrow_trend_coefficient = service.get_narrow_trend_coefficient(charts, symbol) ** sensitivity_exponent
        wide_trend_coefficient = service.get_wide_trend_coefficient(charts, symbol) ** sensitivity_exponent
        adjusted_decay_interval_minutes = decay_base_interval_minutes * narrow_trend_coefficient * wide_trend_coefficient
        new_price = round_up_to_unit(last + (price - last) * (decay_ratio ** (age_minutes / adjusted_decay_interval_minutes)), get_upbit_krw_price_unit)
        print('   재주문 가격 {:>14.2f} KRW'.format(new_price))
        print('----------------------------------------------------------------------------------------------------------------------------------------')
        print('단기( 1분봉 차트) 추세 가속도 지표: {:>6.3f} |              매도-현재가 기본 반감기: {:4.1f} 분'.format(
            narrow_trend_coefficient, decay_base_interval_minutes))
        print('장기(30분봉 차트) 추세 가속도 지표: {:>6.3f} | 단기 및 장기 추세 가속도 반영 반감기: {:>4.1f} 분 '.format(
            wide_trend_coefficient, adjusted_decay_interval_minutes))
        print(new_price, price)
        error = 0.00001
        if abs(new_price - price) / price < error:
            continue
        data = cancel_order(uuid)
        if 'error' in data:
            print(data)
            # {'error': {'message': , 'name': 'order_not_found'}}
            if data['error']['message'] == '주문을 찾지 못했습니다.':
                continue
        assert 'error' not in data
        seamless = True
        data2 = post_limit_order(symbol, -amount, new_price)
        max_tries = 20
        tries = 1
        while 'error' in data2:
            seamless = False
            print(data2)
            if tries == max_tries:
                break
            data2 = post_limit_order(symbol, -amount, new_price)
            tries += 1
        # assert seamless

def market_sell_available_amount(symbol):
    free_balances = get_free_balances()
    # print(free_balances)
    if symbol not in free_balances:
        return
    a1 = free_balances[symbol]['amount']
    if a1 == 0:
        return
    data = post_market_sell_order(symbol, a1)
    print(data)

def cancel_cheapest_sell_order(symbol):
    unfulfilled_orders = get_orders('wait', symbol)
    unfulfilled_orders = [it for it in unfulfilled_orders if it['side'] == 'ask']
    if len(unfulfilled_orders) == 0:
        return
    print('============================================================================================================================')
    print('미체결 주문:')
    unfulfilled_orders.sort(key=lambda x: float(x['price']))
    for it in unfulfilled_orders:
        print(it['uuid'], it['side'], it['market'], it['price'], it['remaining_volume'], it['executed_volume'], it['paid_fee'])
    cheapest_order = unfulfilled_orders[0]
    cancel_order(cheapest_order['uuid'])
    unfulfilled_orders = get_orders('wait', symbol)
    unfulfilled_orders = [it for it in unfulfilled_orders if it['side'] == 'ask']
    print('============================================================================================================================')
    print('미체결 주문:')
    unfulfilled_orders.sort(key=lambda x: float(x['price']))
    for it in unfulfilled_orders:
        print(it['uuid'], it['side'], it['market'], it['price'], it['remaining_volume'], it['executed_volume'], it['paid_fee'])
