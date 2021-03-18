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

import colorsys

def highlight_candle(ax, plt, i, dates, span_minutes, min_y, max_y, color):
    ax.add_patch(mask_h(plt, dates[i] - (span_minutes/(24*60)/2), dates[i] + (span_minutes/(24*60)/2), min_y, max_y, color, 1.0))

def draw(data, trends, price, ax, begin, end, i):
    tic = time.perf_counter()

    span_minutes = (data[1,0] - data[0,0]) / 60
    print(span_minutes)

    open = data[i,1]
    close = data[i,2]
    center = (open + close) / 2
    min_y = center / 1.1
    max_y = center * 1.1
    # min_y = min(self.segment[begin:i,4])
    # max_y = max(self.segment[begin:i,3])

    plt.xticks([trends['dates'][i]], rotation=0)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    ax.set_ylim(bottom = min_y, top = max_y)

    # for j in range(trends['sma5.maximas'].shape[1]):
    #     if j >= begin and j < end:
    #         highlight_candle(ax, plt, trends['sma5.maximas'][0,j], trends['dates'], span_minutes, min_y, max_y, 'red')

    for j in range(trends['sma5.minimas'].shape[1]):
        k = trends['sma5.minimas'][0,j]
        if k >= begin and k < end:
            highlight_candle(ax, plt, k, trends['dates'], span_minutes, min_y, max_y, 'cyan')

    highlight_candle(ax, plt, i, trends['dates'], span_minutes, min_y, max_y, 'yellow')

    plot_day_summary_ohlc(ax, trends['ohlc'][begin:end])

    # ax.plot(trends['hsma40'][trends['dates'][begin]:trends['dates'][end]], color = 'blue', linewidth = 2, label='High, 40-Day SMA')
    # ax.plot(trends['lsma40'][trends['dates'][begin]:trends['dates'][end]], color = 'blue', linewidth = 2, label='Low, 40-Day SMA')
    # ax.plot(trends['ema15'][trends['dates'][begin]:trends['dates'][end]], color = 'red', linestyle='--', linewidth = 2, label='Close, 15-Day EMA')
    # ax.plot(trends['ema5'][trends['dates'][begin]:trends['dates'][end]], color = 'green', linestyle='--', linewidth = 2, label='Close, 5-Day EMA')

    ax.plot(trends['sma5'][trends['dates'][begin]:trends['dates'][end]], color = 'magenta', linewidth = 1, label='5')
    ax.plot(trends['sma10'][trends['dates'][begin]:trends['dates'][end]], color = 'navy', linewidth = 1, label='10')
    ax.plot(trends['sma20'][trends['dates'][begin]:trends['dates'][end]], color = 'orange', linewidth = 1, label='20')
    ax.plot(trends['sma60'][trends['dates'][begin]:trends['dates'][end]], color = 'red', linewidth = 1, label='60')
    ax.plot(trends['sma120'][trends['dates'][begin]:trends['dates'][end]], color = 'grey', linewidth = 1, label='120')

    # for index, value in trends['sma20.diff.diff'].items():
    #     if math.isnan(value):
    #         value = 0
    #     print(index, value)
    #     # saturation = math.log(abs(value) * 100) * 0.3 if value != 0 else 0
    #     saturation = value * 1000
    #     saturation = abs(saturation) if abs(saturation) < 1.0 else 1.0
    #     saturation = math.sqrt(math.sqrt(saturation))
    #     saturation = saturation * 0.3
    #     if value > 0:
    #         color = colorsys.hsv_to_rgb(0.3, saturation, 1.0)
    #     else:
    #         color = colorsys.hsv_to_rgb(1.0, saturation, 1.0)
    #     ax.add_patch(mask_h(plt, index - (span_minutes/(24*60)/2), index + (span_minutes/(24*60)/2), min_y, max_y, color, 1.0))

    plt.axhline(price, color='red')

    toc = time.perf_counter()
    print('{:.3f} ms'.format((toc - tic) * 1000))

from scipy.signal import argrelextrema

def get_maximas(trend):
    # print(trend.fillna(0).to_numpy())
    return np.asarray(argrelextrema(trend.fillna(0).to_numpy(), np.greater_equal, order = 10))

def get_minimas(trend):
    # print(trend.fillna(0).to_numpy())
    return np.asarray(argrelextrema(trend.fillna(0).to_numpy(), np.less_equal, order = 10))

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

        trends['sma5'] = trends['dataframe']['close'].rolling(5).mean()
        trends['sma10'] = trends['dataframe']['close'].rolling(10).mean()
        trends['sma20'] = trends['dataframe']['close'].rolling(20).mean()
        trends['sma60'] = trends['dataframe']['close'].rolling(60).mean()
        trends['sma120'] = trends['dataframe']['close'].rolling(120).mean()

        trends['sma5.diff'] = trends['sma5'].diff() / trends['sma5']
        trends['sma10.diff'] = trends['sma10'].diff() / trends['sma10']
        trends['sma20.diff'] = trends['sma20'].diff() / trends['sma20']
        trends['sma60.diff'] = trends['sma60'].diff() / trends['sma60']
        trends['sma120.diff'] = trends['sma120'].diff() / trends['sma120']

        trends['sma5.diff.diff'] = trends['sma5.diff'].diff()
        trends['sma10.diff.diff'] = trends['sma10.diff'].diff()
        trends['sma20.diff.diff'] = trends['sma20.diff'].diff()
        trends['sma60.diff.diff'] = trends['sma60.diff'].diff()
        trends['sma120.diff.diff'] = trends['sma120.diff'].diff()

        trends['sma5.maximas'] = get_maximas(trends['sma5'])
        trends['sma10.maximas'] = get_maximas(trends['sma10'])
        trends['sma20.maximas'] = get_maximas(trends['sma20'])
        trends['sma60.maximas'] = get_maximas(trends['sma60'])
        trends['sma120.maximas'] = get_maximas(trends['sma120'])

        trends['sma5.minimas'] = get_minimas(trends['sma5'])
        trends['sma10.minimas'] = get_minimas(trends['sma10'])
        trends['sma20.minimas'] = get_minimas(trends['sma20'])
        trends['sma60.minimas'] = get_minimas(trends['sma60'])
        trends['sma120.minimas'] = get_minimas(trends['sma120'])

        # trends['sma120.diff'] = trends['sma120'].diff() / trends['sma120']

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
    
    def draw(self, type, ax, price, begin, end, i):
        draw(self.data[type], self.trends[type], price, ax, begin, end, i)

charts = {}

async def update_charts(type, do_your_thing = None, loop = None):
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
            # if do_your_thing is not None:
            #     await do_your_thing(symbol, last_candle, loop)
        else:
            stale_list += symbol + ' '
        if do_your_thing is not None:
            await do_your_thing(symbol, last_candle, loop)
        # print(symbol)
        await asyncio.sleep(0)
    remaining_stale_count = stale_count - updated_count
    now = time.time()
    print('{:>3} {} {:>3}/{:>3} {}'.format(type, datetime.datetime.utcfromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S'), updated_count, stale_count,
        stale_list if remaining_stale_count <= 20 else '({})'.format(remaining_stale_count)))

max_snapshots = 10

async def test(symbol, _, __):
    chart = charts[symbol]

    past_size = 100
    future_size = 20

    snapshots_count = 0

    type = '1m'
    for i in range(past_size, chart.data[type].shape[0] - future_size):
        last_candle = chart.data['1m'][i]
        if not history_condition(chart, i):
            continue
        if not this_candle_condition(last_candle, chart, i):
            continue
        if snapshots_count == 0:
            fig = plt.figure(figsize=(20 * max_snapshots, 7))
            gs_all = gridspec.GridSpec(1, max_snapshots, figure=fig)
        if snapshots_count < max_snapshots:
            ax = fig.add_subplot(gs_all[0, snapshots_count])
            chart.draw(type, ax, last_candle[OPEN_INDEX], i - past_size, i + future_size, i)
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
        try:
            os.mkdir('output')
        except OSError:
            pass
        fig.savefig("output/upbit-{}-{}.png".format(symbol, type), bbox_inches='tight', dpi=100)
        plt.close(fig)
        print('done')

decay_interval_minutes = 5
decay_ratio = 0.9

def enforce_sell():
    data = get_free_balances()
    for symbol in data:
        amount = data[symbol]['amount']
        price = data[symbol]['price']
        if amount * price < 10000:
            continue
        data2 = post_limit_order(symbol, -amount, round_up_to_unit(price * 1.1, get_upbit_krw_price_unit))
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
            new_price = round_up_to_unit(last + (price - last) * decay_ratio, get_upbit_krw_price_unit)
            if new_price == price:
                new_price = price - get_upbit_krw_price_unit(price)
            data = post_limit_order(symbol, -amount, new_price)
            if 'error' in data:
                print(data)

################################################################################################################################################

# def history_condition(chart, i = 0):
#     dates = chart.trends['1m']['dates']
#     narrow_trend = chart.trends['1m']['sma5']
#     wide_trend = chart.trends['1m']['sma10']
#     wider_trend = chart.trends['1m']['sma60']
#     widest_trend = chart.trends['1m']['sma120']

#     if narrow_trend[dates[i-1]] / narrow_trend[dates[i-1-5]] < 1.000:
#         return False
#     if wide_trend[dates[i-1]] / wide_trend[dates[i-1-20]] < 1.000:
#         return False
#     if wider_trend[dates[i-1]] / wider_trend[dates[i-1-20]] < 1.000:
#         return False
#     if widest_trend[dates[i-1]] / widest_trend[dates[i-1-20]] < 1.000:
#         return False

#     past_n = 10
#     # previous_diff = None
#     for j in range(1, past_n):
#         diff = wide_trend[dates[i-1-j]] - narrow_trend[dates[i-1-j]] # 계속 wide가 컸었음..
#         if diff < 0:
#             return False
#         # if not (previous_diff is None or previous_diff > diff):
#         #     return False
#         # previous_diff = diff

#     if narrow_trend[dates[i-1]] >= wide_trend[dates[i-1]]: # 방금 전 역전!
#         return True

#     return False

# def this_candle_condition(this_candle, chart, i = 0):
#     match = True

#     # dates = chart.trends['1m']['dates']
#     # wide_trend = chart.trends['1m']['ema15']

#     # match = match and this_candle[OPEN_INDEX] < wide_trend[dates[i - 1]]
#     # match = match and this_candle[HIGH_INDEX] > wide_trend[dates[i - 1]]

#     return match

################################################################################################################################################

# def history_condition(chart, i = 0):
#     match = True

#     dates = chart.trends['1m']['dates']


#     price_1m = []
#     # price_1m.append(chart.trends['1m']['sma5'])
#     # price_1m.append(chart.trends['1m']['sma10'])
#     # price_1m.append(chart.trends['1m']['sma20'])
#     price_1m.append(chart.trends['1m']['sma60'])
#     price_1m.append(chart.trends['1m']['sma120'])

#     diff_1m = []
#     diff_1m.append(chart.trends['1m']['sma5.diff'])
#     diff_1m.append(chart.trends['1m']['sma10.diff'])
#     diff_1m.append(chart.trends['1m']['sma20.diff'])
#     diff_1m.append(chart.trends['1m']['sma60.diff'])
#     diff_1m.append(chart.trends['1m']['sma120.diff'])

#     diff_diff_1m = []
#     diff_diff_1m.append(chart.trends['1m']['sma5.diff.diff'])
#     diff_diff_1m.append(chart.trends['1m']['sma10.diff.diff'])
#     diff_diff_1m.append(chart.trends['1m']['sma20.diff.diff'])
#     diff_diff_1m.append(chart.trends['1m']['sma60.diff.diff'])
#     diff_diff_1m.append(chart.trends['1m']['sma120.diff.diff'])

#     # 직전봉에서의 이동평균가를 그보다 10개봉 전 것과 비교했을 때 더 작으면, 즉 추세적으로 하락중이면 거른다. (이건 장기추세만 봄)
#     for trend in price_1m:
#         if trend[dates[i-1]] < trend[dates[i-1-10]]:
#             return False

#     # 직전 봉에서의 가격의 이동평균 미분(순간 속도)가 하나라도 음수, 즉 이동평균 중 하나라도 내리막이면 거른다.
#     for trend in diff_1m:
#         if trend[dates[i-1]] < 0:
#             return False

#     # 직전 봉에서의 가격의 이동평균 미분의 미문(순간 가속도)가 하나라도 음수, 즉 이동평균 중 하나라도 감소세가 강해지고 있거나, 증가세가 둔화되고 있으면 거른다.
#     # 그런데 바로 위에서 내리막(감소세)인 것은 걸렀으므로, 여기서 걸러지는 것은 증가하고는 있지만, 증가세가 둔화되면서 위로 볼록해지기 시작하는 것들이다.
#     for trend in diff_diff_1m:
#         if trend[dates[i-1]] < 0:
#             return False

#     # past_n = 10
#     # previous_diff = None
#     # for j in range(past_n):
#     #     diff = wide_trend[dates[i-1-j]] - narrow_trend[dates[i-1-j]]
#     #     if diff < 0:
#     #         return False
#     #     # if not (previous_diff is None or previous_diff > diff):
#     #     #     return False
#     #     previous_diff = diff

#     return match

# def this_candle_condition(this_candle, chart, i = 0):
#     match = True

#     dates = chart.trends['1m']['dates']
#     price_1m = chart.trends['1m']['sma20']

#     match = match and this_candle[OPEN_INDEX] < price_1m[dates[i - 1]]
#     match = match and this_candle[HIGH_INDEX] > price_1m[dates[i - 1]]

#     return match

################################################################################################################################################

def history_condition(chart, i = 0):
    match = True

    dates = chart.trends['1m']['dates']

    price_1m = []
    price_1m.append(chart.trends['1m']['sma5'])
    price_1m.append(chart.trends['1m']['sma10'])
    price_1m.append(chart.trends['1m']['sma20'])
    price_1m.append(chart.trends['1m']['sma60'])
    price_1m.append(chart.trends['1m']['sma120'])

    diff_1m = []
    diff_1m.append(chart.trends['1m']['sma5.diff'])
    diff_1m.append(chart.trends['1m']['sma10.diff'])
    diff_1m.append(chart.trends['1m']['sma20.diff'])
    diff_1m.append(chart.trends['1m']['sma60.diff'])
    diff_1m.append(chart.trends['1m']['sma120.diff'])

    diff_diff_1m = []
    diff_diff_1m.append(chart.trends['1m']['sma5.diff.diff'])
    diff_diff_1m.append(chart.trends['1m']['sma10.diff.diff'])
    diff_diff_1m.append(chart.trends['1m']['sma20.diff.diff'])
    diff_diff_1m.append(chart.trends['1m']['sma60.diff.diff'])
    diff_diff_1m.append(chart.trends['1m']['sma120.diff.diff'])

    price = chart.data['1m'][i-1,CLOSE_INDEX]

    match = True

    match = match and diff_diff_1m[0][dates[i-1]] > 0.002
    match = match and diff_diff_1m[1][dates[i-1]] > 0.0005
    match = match and diff_diff_1m[2][dates[i-1]] > 0
    match = match and diff_diff_1m[3][dates[i-1]] > 0
    match = match and diff_diff_1m[4][dates[i-1]] > 0
    if not match:
        return False

    # match = match and diff_1m[0][dates[i-1]] > 0
    # match = match and diff_1m[1][dates[i-1]] > 0
    # match = match and diff_1m[2][dates[i-1]] > 0
    # match = match and diff_1m[3][dates[i-1]] > 0
    # match = match and diff_1m[4][dates[i-1]] > 0
    # if not match:
    #     return False

    # maximas = chart.trends['1m']['sma5.maximas']
    # match = match and (i - max(maximas[maximas < i]) > 50 if len(maximas[maximas < i]) > 0 else False)

    # maximas = chart.trends['1m']['sma10.maximas']
    # match = match and (i - max(maximas[maximas < i]) > 50 if len(maximas[maximas < i]) > 0 else False)

    # maximas = chart.trends['1m']['sma20.maximas']
    # match = match and (i - max(maximas[maximas < i]) > 50 if len(maximas[maximas < i]) > 0 else False)

    # maximas = chart.trends['1m']['sma60.maximas']
    # match = match and (i - max(maximas[maximas < i]) > 50 if len(maximas[maximas < i]) > 0 else False)

    # maximas = chart.trends['1m']['sma120.maximas']
    # match = match and (i - max(maximas[maximas < i]) > 50 if len(maximas[maximas < i]) > 0 else False)

    minimas = chart.trends['1m']['sma5.minimas']
    match = match and (i - max(minimas[minimas < i]) < 2  if len(minimas[minimas < i]) > 0 else False)

    # minimas = chart.trends['1m']['sma10.minimas']
    # match = match and (i - max(minimas[minimas < i]) < 2 if len(minimas[minimas < i]) > 0 else False)

    # minimas = chart.trends['1m']['sma20.minimas']
    # match = match and (i - max(minimas[minimas < i]) < 2 if len(minimas[minimas < i]) > 0 else False)

    # minimas = chart.trends['1m']['sma60.minimas']
    # match = match and (i - max(minimas[minimas < i]) < 2 if len(minimas[minimas < i]) > 0 else False)

    # minimas = chart.trends['1m']['sma120.minimas']
    # match = match and (i - max(minimas[minimas < i]) < 2 if len(minimas[minimas < i]) > 0 else False)


    if not match:
        return False

    if diff_1m[0][dates[i-1]] > 0.0005: # 단기 이동평균선의 직전봉에서의 미분이 너무 크다는 건 이미 가격이 올라버렸다는 것일 수 있으니 거르자
        return False

    if price > price_1m[4][dates[i-1]]:
        return False

    # for trend in diff_1m:
    #     print('diff {:f}'.format(trend[dates[i-1]]))
    #     if trend[dates[i-1]] < 0:
    #         return False

    return True

    # for j in range(2):
    #     diff_trend = diff_1m[j]
    #     if diff_trend[dates[i-1-1]] <= 0 and diff_trend[dates[i-1]] > 0: # 기울기가 음에서 양으로 전환됨, 즉 가격의 극소점
    #         for k in range(3, len(price_1m)):
    #             wider_price_trend = price_1m[k]
    #             if price < wider_price_trend[dates[i-1]]: # 현재 가격보다 더 높이 있는 장기 이동평균선이 하나라도 있음 고고
    #                 return True
    #         #     if price > wider_price_trend[dates[i-1]]: # 현재 가격보다 아래 있는 장기 이동평균선이 하나라도 있음 아웃
    #         #         return False
    #         # return True

    return False

def this_candle_condition(this_candle, chart, i = 0):
    match = True

    # dates = chart.trends['1m']['dates']
    # price_1m = chart.trends['1m']['sma20']

    # match = match and this_candle[OPEN_INDEX] < price_1m[dates[i - 1]]
    # match = match and this_candle[HIGH_INDEX] > price_1m[dates[i - 1]]

    return match

################################################################################################################################################

traders = {}

# async def shit(symbol):
#     for i in range(10):
#         print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ {} {}'.format(symbol, i))
#         await asyncio.sleep(1)

async def amber(symbol, last_candle, loop):
    type = '1m'
    chart = charts[symbol]
    now = time.time()
    print('{:<9} {}'.format(symbol, str(datetime.datetime.fromtimestamp(chart.data[type][-1, TIMESTAMP_INDEX]))))
    # if symbol not in traders or traders[symbol].done():
    #     print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    #     traders[symbol] = loop.create_task(shit(symbol))
    #     # await asyncio.sleep(0)
    if not history_condition(chart):
        return
    print(stringify_standard_candle(chart.data[type][-4]))
    print(stringify_standard_candle(chart.data[type][-3]))
    print(stringify_standard_candle(chart.data[type][-2]))
    print(stringify_standard_candle(chart.data[type][-1]))
    this_candle_match = this_candle_condition(last_candle, chart)
    if this_candle_match:
        print(stringify_standard_candle(last_candle, bcolors.OKGREEN))
        if symbol not in traders or traders[symbol].done():
            # traders[symbol] = loop.create_task(start_quickie(symbol, 60 * 10000, [1.003, 1.004, 1.005, 1.01, 1.05, 1.1]))
            traders[symbol] = loop.create_task(start_quickie(symbol, 100 * 10000, [1.01, 1.02, 1.03, 1.04, 1.05]))
            await asyncio.sleep(0)
    else:
        print(stringify_standard_candle(last_candle, bcolors.OKBLUE))

import asyncio

loop = asyncio.get_event_loop()

async def lurk():
    while True:
        await update_charts('1m', amber, loop)
        # await update_charts('30m')
        # await update_charts('1D')
        decay_sell_orders()
        enforce_sell()

# loop.create_task(lurk())
loop.create_task(update_charts('1m', test))
loop.run_forever()

# import random

# async def sap(id):
#     for i in range(5):
#         print('[{}]:{}'.format(id, i))
#         await asyncio.sleep(random.randint(0, 2))

# tasks = []
# loop = asyncio.get_event_loop()
# for i in range(5):
#     tasks.append(loop.create_task(sap(i)))
# loop.run_until_complete()

# # all_done = False

# # while not all_done:
# #     for i in range(len(tasks)):
# #         if tasks[i] is not None and tasks[i].done():
# #             tasks[i] = None
# #     all_done = True
# #     for i in range(10):
# #         if tasks[i] is not None:
# #             all_done = False
# #             break
    
