from upbit_helpers_2 import *

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

def mask_h(plt, x1, x2, min_y, max_y, color, alpha):
    return plt.Rectangle((x1, min_y), x2 - x1, max_y - min_y, linewidth=0, alpha=alpha, edgecolor=color, facecolor=color)

from mplfinance.original_flavor import plot_day_summary_ohlc
from mplfinance.original_flavor import candlestick2_ohlc

import colorsys

def highlight_candle(ax, plt, i, dates, span_minutes, min_y, max_y, color):
    ax.add_patch(mask_h(plt, dates[i] - (span_minutes/(24*60)/2), dates[i] + (span_minutes/(24*60)/2), min_y, max_y, color, 1.0))

def draw(data, trends, price, ax, highlights):
    tic = time.perf_counter()

    span_minutes = (data[1,0] - data[0,0]) / 60
    print(span_minutes)

    n = data.shape[0] 

    i = int(n / 2)

    open = data[i,1]
    close = data[i,2]
    center = (open + close) / 2
    # min_y = center / 1.05
    # max_y = center * 1.05
    min_y = min(data[:,LOW_INDEX])
    max_y = max(data[:,HIGH_INDEX])

    plt.xticks([trends['dates'][i]], rotation=0)
    plt.xticks([trends['dates'][n - 1]], rotation=0)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    ax.set_ylim(bottom = min_y, top = max_y)

    for j in range(len(highlights)):
        k = highlights[j]
        highlight_candle(ax, plt, k, trends['dates'], span_minutes, min_y, max_y, 'cyan')

    # for j in range(len(highlights)):
    #     if highlights[trends['dates'][j]]:
    #        highlight_candle(ax, plt, j, trends['dates'], span_minutes, min_y, max_y, 'cyan')

    highlight_candle(ax, plt, n - 1, trends['dates'], span_minutes, min_y, max_y, 'yellow')

    THRESHOLD2 = 0.1

    # for j in range(len(trends['sma5.diff.diff'])):
    #     dd = trends['sma5.diff.diff'][trends['dates'][j]]
    #     if dd > 0:
    #         highlight_candle(ax, plt, j, trends['dates'], span_minutes, min_y, max_y, 'greenyellow')
    #     else:
    #         highlight_candle(ax, plt, j, trends['dates'], span_minutes, min_y, max_y, 'lightcoral')

    plot_day_summary_ohlc(ax, trends['ohlc'])

    # ax.plot(trends['hsma40'], color = 'blue', linewidth = 2, label='High, 40-Day SMA')
    # ax.plot(trends['lsma40'], color = 'blue', linewidth = 2, label='Low, 40-Day SMA')
    # ax.plot(trends['ema15'], color = 'red', linestyle='--', linewidth = 2, label='Close, 15-Day EMA')
    # ax.plot(trends['ema5'], color = 'green', linestyle='--', linewidth = 2, label='Close, 5-Day EMA')

    ax.plot(trends['sma5'], color = 'magenta', linewidth = 1, label='5')
    ax.plot(trends['sma10'], color = 'navy', linewidth = 1, label='10')
    ax.plot(trends['sma20'], color = 'orange', linewidth = 1, label='20')
    ax.plot(trends['sma60'], color = 'red', linewidth = 1, label='60')
    ax.plot(trends['sma120'], color = 'grey', linewidth = 1, label='120')

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

def color(candle):
    return bcolors.OKGREEN if candle[PRICE_CHANGE_RATIO_INDEX] * 100 > 0 else bcolors.FAIL

from delilah import safe_to_buy

def test(charts, service, symbol, type):
    chart = charts[symbol]

    past_size = 10
    future_size = 3

    n = chart.data[type].shape[0]

    minimas = []
    maximas = []
    buys = []
    sells = []
    purge_restropect = []

    fig = plt.figure(figsize=(20, 7))
    ax = fig.add_subplot(1, 1, 1)
    # buys = safe_to_buy(chart)
    # print(buys)

    for i in range(past_size, n - future_size):
        this_candle = chart.data[type][i]
        if this_candle[CLOSE_INDEX] / this_candle[OPEN_INDEX] > 1.03:
            print(chart.trends[type]['sma5.diff'][chart.trends[type]['dates'][i]], chart.trends[type]['sma5.diff.diff'][chart.trends[type]['dates'][i]])
        # if this_candle[CLOSE_INDEX] / this_candle[OPEN_INDEX] < 1.1:
        #     continue
        if not service.history_condition(chart, i):
            continue
        if not service.this_candle_condition(this_candle, chart, i):
            continue
        buys.append(i)
        print(symbol)
        print(stringify_standard_candle(chart.data[type][i - 4]))
        print(stringify_standard_candle(chart.data[type][i - 3]))
        print(stringify_standard_candle(chart.data[type][i - 2]))
        print(stringify_standard_candle(chart.data[type][i - 1]))
        print(stringify_standard_candle(chart.data[type][i    ], color(chart.data[type][i])))
        print(stringify_standard_candle(chart.data[type][i + 1], color(chart.data[type][i + 1])))
        print(stringify_standard_candle(chart.data[type][i + 2], color(chart.data[type][i + 2])))
        print(stringify_standard_candle(chart.data[type][i + 3], color(chart.data[type][i + 3])))

    # draw(chart.data[type], chart.trends[type], 0, ax, chart.trends[type]['sma5.minimas'])
    draw(chart.data[type], chart.trends[type], 0, ax, buys)

    if len(buys) == 0:
        plt.close(fig)
        return

    print('Rendering...')
    try:
        os.mkdir('output')
    except OSError:
        pass
    fig.savefig("output/upbit-{}-{}.png".format(symbol, type), bbox_inches='tight', dpi=100)
    plt.close(fig)
    print('done')

import asyncio

loop = asyncio.get_event_loop()

import brandy
import candy
import elektra

candidates = []
load_candidates(candidates)
# load_candidates(candidates, True)

# candidates = ['KRW-ATOM', 'KRW-ADX', 'KRW-DMT', 'KRW-LINK', 'KRW-STEEM', 'KRW-SPND', 'KRW-ENJ', 'KRW-SRN', 'KRW-BTG', 'KRW-DOGE']
# candidates = ['KRW-SRN', 'KRW-MTL']

charts = {}

loop.run_until_complete(update_charts(candidates, charts, '30m'))
loop.run_until_complete(update_charts(candidates, charts, '1m'))

# with open('charts.30m.json', 'w') as outfile:
#     json.dump(charts, outfile)

for symbol in charts:
    test(charts, elektra, symbol, '1m')
