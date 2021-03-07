from upbit_helpers import *

import time

candidates = []

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

load_candidates(candidates)

load_candidates(candidates, True)

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


import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

def mask_h(plt, x1, x2, min_y, max_y, color, alpha):
    return plt.Rectangle((x1, min_y), x2 - x1, max_y - min_y, linewidth=0, alpha=alpha, edgecolor=color, facecolor=color)

from mplfinance.original_flavor import plot_day_summary_ohlc
from mplfinance.original_flavor import candlestick2_ohlc

def draw(data, trends, ax, begin, end, i):
    tic = time.perf_counter()

    span_minutes = (data[1,0] - data[0,0]) / 60
    print(span_minutes)

    open = data[i,1]
    close = data[i,2]
    center = (open + close) / 2
    min_y = center / 1.05
    max_y = center * 1.05
    # min_y = min(self.segment[begin:i,4])
    # max_y = max(self.segment[begin:i,3])

    plt.xticks([trends['dates'][i]], rotation=0)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    ax.set_ylim(bottom = min_y, top = max_y)

    ax.add_patch(mask_h(plt, trends['dates'][i] - (span_minutes/(24*60)/2), trends['dates'][i] + (span_minutes/(24*60)/2), min_y, max_y, 'yellow', 1.0))

    plot_day_summary_ohlc(ax, trends['ohlc'][begin:end])

    ax.plot(trends['hsma40'][trends['dates'][begin]:trends['dates'][end]], color = 'blue', linewidth = 2, label='High, 40-Day SMA')
    ax.plot(trends['lsma40'][trends['dates'][begin]:trends['dates'][end]], color = 'blue', linewidth = 2, label='Low, 40-Day SMA')
    ax.plot(trends['ema15'][trends['dates'][begin]:trends['dates'][end]], color = 'red', linestyle='--', linewidth = 2, label='Close, 15-Day EMA')
    ax.plot(trends['ema5'][trends['dates'][begin]:trends['dates'][end]], color = 'green', linestyle='--', linewidth = 2, label='Close, 5-Day EMA')
    # ax.plot(self.ema60[self.dates[begin]:self.dates[end]], color = 'purple', linestyle='--', linewidth = 2, label='Close, 60-Day EMA')

    toc = time.perf_counter()
    print('{:.3f} ms'.format((toc - tic) * 1000))

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
        trends['hsma40'] = trends['dataframe']['high'].rolling(40).mean()
        trends['lsma40'] = trends['dataframe']['low'].rolling(40).mean()
        trends['ema15'] = trends['dataframe']['close'].ewm(15).mean()
        trends['ema5'] = trends['dataframe']['close'].ewm(5).mean()

    def need_update(self, type):
        return True
        if type not in self.data:
            return True
        now = time.time()
        last_candle_timestamp = self.data[type][-1,TIMESTAMP_INDEX]
        seconds_elapsed_since_last_candle_begin = now - last_candle_timestamp
        interval_seconds = get_milliseconds(type) / 1000
        if interval_seconds * 2 - seconds_elapsed_since_last_candle_begin < 5:
            # print('{} {:.0f}'.format(str(datetime.datetime.fromtimestamp(last_candle_timestamp)), seconds_elapsed_since_last_candle_begin))
            return True
        return False
    
    def draw(self, type, ax, begin, end, i):
        draw(self.data[type], self.trends[type], ax, begin, end, i)

charts = {}

async def update_charts(type, do_your_thing = None):
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
            if do_your_thing is not None:
                await do_your_thing(symbol, last_candle)
        else:
            stale_list += symbol + ' '
        # print(symbol)
    remaining_stale_count = stale_count - updated_count
    now = time.time()
    print('{:>3} {} {:>3}/{:>3} {}'.format(type, datetime.datetime.utcfromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S'), updated_count, stale_count,
        stale_list if remaining_stale_count <= 20 else '({})'.format(remaining_stale_count)))

max_snapshots = 10

def test(symbol, last_candle):
    chart = charts[symbol]

    past_size = 100
    future_size = 20

    snapshots_count = 0

    type = '1m'
    for i in range(past_size, chart.data[type].shape[0] - future_size):
        if not history_condition(chart, i):
            continue
        # if not this_candle_condition(history[i], series, i):
        #     continue
        if snapshots_count == 0:
            fig = plt.figure(figsize=(20 * max_snapshots, 7))
            gs_all = gridspec.GridSpec(1, max_snapshots, figure=fig)
        if snapshots_count < max_snapshots:
            ax = fig.add_subplot(gs_all[0, snapshots_count])
            chart.draw(type, ax, i - past_size, i + future_size, i)
            snapshots_count += 1
        print(symbol)
        print(stringify_standard_candle(chart.data[type][i - 4]))
        print(stringify_standard_candle(chart.data[type][i - 3]))
        print(stringify_standard_candle(chart.data[type][i - 2]))
        print(stringify_standard_candle(chart.data[type][i - 1]))
        print(stringify_standard_candle(chart.data[type][i], bcolors.OKGREEN if chart.data[type][i, PRICE_HIGH_RATIO_INDEX] * 100 > 3 else bcolors.FAIL))
        print(stringify_standard_candle(chart.data[type][i + 1]))
        print(stringify_standard_candle(chart.data[type][i + 2]))
        print(stringify_standard_candle(chart.data[type][i + 3]))

    if snapshots_count > 0:
        print('Rendering...')
        fig.savefig("output/upbit-{}-{}.png".format(symbol, type), bbox_inches='tight', dpi=100)
        plt.close(fig)
        print('done')

decay_interval_minutes = 5
decay_ratio = 0.90

def enforce_sell():
    data = get_free_balances()
    for symbol in data:
        amount = data[symbol]['amount']
        price = data[symbol]['price']
        if amount * price < 10000:
            continue
        data2 = post_limit_order(symbol, -amount, round_up_to_unit(price * 2, get_upbit_krw_price_unit))
        # print(data2)

def decay_sell_orders():
    unfulfilled_sell_orders = get_orders('wait')
    # print(unfulfilled_sell_orders)
    for order in unfulfilled_sell_orders:
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
        distance = last / price
        now = time.time()
        age_minutes = (now - timestamp.timestamp()) / 60
        print('{} {:<10} {:>15.6f} {:>11} {:>11} {:>6.2f}% {} {} {:>3}:{:0>2}'.format(
            uuid, symbol, amount, price, last, distance * 100 - 100,
            timestamp, timestamp.strftime('%Y-%m-%d %H:%M:%S %Z'), int(age_minutes / 60), int(age_minutes % 60)))
        if age_minutes > decay_interval_minutes:
            data = cancel_order(uuid)
            if 'error' in data:
                print(data)
            data = post_limit_order(symbol, -amount, round_up_to_unit(last + (price - last) * decay_ratio, get_upbit_krw_price_unit))
            if 'error' in data:
                print(data)

def history_condition(chart, i = 0):
    return True
    match = True

    wide_trend = chart.trends['1m']['ema15']
    narrow_trend = chart.trends['1m']['ema5']
    dates = chart.trends['1m']['dates']

    if wide_trend[dates[i-1]] / wide_trend[dates[i-1-20]] < 1.000:
        return False
    if narrow_trend[dates[i-1]] / narrow_trend[dates[i-1-5]] < 1.000:
        return False

    past_n = 10
    previous_diff = None
    for j in range(past_n):
        diff = wide_trend[dates[i-1-j]] - narrow_trend[dates[i-1-j]]
        if diff < 0:
            return False
        # if not (previous_diff is None or previous_diff > diff):
        #     return False
        previous_diff = diff

    return match

def this_candle_condition(this_candle, chart, i = 0):
    match = True

    wide_trend = chart.trends['1m']['ema15']
    dates = chart.trends['1m']['dates']

    match = match and this_candle[OPEN_INDEX] < wide_trend[dates[i - 1]]
    match = match and this_candle[HIGH_INDEX] > wide_trend[dates[i - 1]]

    return match

async def amber(symbol, last_candle):
    type = '1m'
    chart = charts[symbol]
    now = time.time()
    print('{:<9} {}'.format(symbol, str(datetime.datetime.fromtimestamp(chart.data[type][-1, TIMESTAMP_INDEX]))))
    if not history_condition(chart):
        return
    print(stringify_standard_candle(chart.data[type][-4]))
    print(stringify_standard_candle(chart.data[type][-3]))
    print(stringify_standard_candle(chart.data[type][-2]))
    print(stringify_standard_candle(chart.data[type][-1]))
    this_candle_match = this_candle_condition(last_candle, chart)
    if this_candle_match:
        print(stringify_standard_candle(last_candle, bcolors.OKGREEN))
        # await start_quickie(symbol, 800000, [1.002, 1.003, 1.004, 1.005, 1.01, 1.02, 1.05, 1.1])
        # await start_quickie(symbol, 500000, [1.002, 1.003, 1.005, 1.01, 1.1])
        # await start_quickie(symbol, 700000, [1.003, 1.004, 1.005, 1.006, 1.01, 1.02, 1.03])
        await start_quickie(symbol, 600000, [1.003, 1.004, 1.005])
    else:
        print(stringify_standard_candle(last_candle, bcolors.OKBLUE))

async def lurk():
    while True:
        await update_charts('1m', amber)
        # update_charts('30m')
        # update_charts('1D')
        decay_sell_orders()
        enforce_sell()

import asyncio

loop = asyncio.get_event_loop()
for symbol in candidates:
    loop.create_task(lurk())
loop.run_forever()

update_charts('1m', test)
