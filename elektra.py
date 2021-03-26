from upbit_helpers import *

# def history_condition(chart, i):
#     trends = chart.trends['30m']
#     dates = trends['dates']

#     match = True

#     # match = match and trends['sma20.diff.diff'][dates[i]] > 1

#     # match = match and trends['sma5.diff.diff'][dates[i - 1]] > 1
#     # match = match and trends['sma10.diff.diff'][dates[i - 1]] > 1
#     match = match and trends['sma20.diff.diff'][dates[i - 1]] > 1
#     # match = match and trends['sma60.diff.diff'][dates[i - 1]] > 1
#     # match = match and trends['sma120.diff.diff'][dates[i - 1]] > 1

#     # match = match and trends['sma5.diff'][dates[i - 1]] > 1
#     # match = match and trends['sma10.diff'][dates[i - 1]] > 1
#     match = match and trends['sma20.diff'][dates[i - 1]] > 1
#     match = match and trends['sma60.diff'][dates[i - 1]] > 1
#     # match = match and trends['sma120.diff'][dates[i - 1]] > 1

#     match = match and trends['sma20'][dates[i - 1]] > trends['sma20'][dates[i - 2]]
#     match = match and trends['sma20'][dates[i - 1]] > trends['sma20'][dates[i - 3]]

#     # match = match and trends['sma20'][dates[i]] > trends['sma20'][dates[i - 1]]
#     # match = match and trends['sma20'][dates[i]] > trends['sma20'][dates[i - 2]]

#     return match

# def this_candle_condition(this_candle, chart, i):
#     match = True

#     dates = chart.trends['30m']['dates']
#     trends = chart.trends['30m']

#     match = match and this_candle[LOW_INDEX] <= trends['sma20'][dates[i - 1]]

#     return match

def history_condition_1(chart, i):
    trends = chart.trends['1m']
    dates = trends['dates']

    if trends['sma5.diff.diff'][dates[i-1]] < 1:
        return False

    # rise = 0
    # for j in range(10):
    #     if trends['sma60'][dates[i - 1]] >= trends['sma60'][dates[i - 1 - j]]:
    #         rise += 1
    #     else:
    #         rise -= 1
    # if rise < 0:
    #     return False

    # if not abs(trends['sma5.diff'][dates[i - 1]] - 1) < 0.001:
    #     return False

    result = 1

    result = result * trends['sma5v.diff.diff'][dates[i-1]]

    # result = result * trends['sma5.diff.diff'][dates[i-1]] ** trends['sma5v.diff.diff'][dates[i-1]]
    # result = result * trends['sma10.diff.diff'][dates[i-1]] ** trends['sma10v.diff.diff'][dates[i-1]]
    # result = result * trends['sma20.diff.diff'][dates[i-1]] ** trends['sma20v.diff.diff'][dates[i-1]]
    # result = result * trends['sma60.diff.diff'][dates[i-1]] ** trends['sma60v.diff.diff'][dates[i-1]]
    # result = result * trends['sma120.diff.diff'][dates[i-1]] ** trends['sma120v.diff.diff'][dates[i-1]]

    # result = result * trends['sma5v.diff'][dates[i-1]]

    # result = result * trends['sma5.diff.diff'][dates[i-1]] ** (trends['sma5v.diff.diff'][dates[i-1]] ** 100)
    # result = result * trends['sma10.diff.diff'][dates[i-1]] ** (trends['sma10v.diff.diff'][dates[i-1]] ** 100)
    # result = result * trends['sma20.diff.diff'][dates[i-1]] ** (trends['sma20v.diff.diff'][dates[i-1]] ** 100)
    # result = result * trends['sma60.diff.diff'][dates[i-1]] ** (trends['sma60v.diff.diff'][dates[i-1]] ** 100)
    # result = result * trends['sma120.diff.diff'][dates[i-1]] ** (trends['sma120v.diff.diff'][dates[i-1]] ** 100)

    print(result)

    return result > 2

def history_condition(chart, i):
    trends = chart.trends['1m']
    dates = trends['dates']
    # print(trends['sma5.diff.diff'][dates[i-1]])
    if trends['sma5.diff'][dates[i-1]] < 1: return False
    if trends['sma20.diff'][dates[i-1]] < 1: return False
    return True

def price_breakout(this_candle, data, i):
    if data[i,CLOSE_INDEX] - data[i,OPEN_INDEX] == 0:
        return this_candle[HIGH_INDEX] - this_candle[OPEN_INDEX] > 0
    return (this_candle[HIGH_INDEX] - this_candle[OPEN_INDEX]) / (data[i,CLOSE_INDEX] - data[i,OPEN_INDEX]) > 2

def this_candle_condition_1(this_candle, chart, i):
    # return True
    match = True

    data = chart.data['1m']
    trends = chart.trends['1m']
    dates = chart.trends['1m']['dates']

    # print(this_candle[VOLUME_INDEX], data[i - 1][VOLUME_INDEX])
    assert this_candle[VOLUME_INDEX] / data[i - 1][VOLUME_INDEX] == data[i][VOLUME_RATIO_INDEX]

    if not price_breakout(this_candle, data, i - 1): return False
    if not price_breakout(this_candle, data, i - 2): return False
    if not price_breakout(this_candle, data, i - 3): return False
    volume_ratio = (this_candle[VOLUME_INDEX]) / (data[i-1,VOLUME_INDEX])
    print(volume_ratio)
    return volume_ratio > 1.5

    # match = match and this_candle[LOW_INDEX] <= trends['sma5'][dates[i - 1]]

    return match

def cross_price_trend(this_candle, trend):
    return this_candle[OPEN_INDEX] < trend and trend < this_candle[HIGH_INDEX]

def this_candle_condition(this_candle, chart, i):
    trends = chart.trends['1m']
    dates = chart.trends['1m']['dates']

    if not cross_price_trend(this_candle, trends['sma5'][dates[i - 1]]): return False
    if not cross_price_trend(this_candle, trends['sma10'][dates[i - 1]]): return False
    if not cross_price_trend(this_candle, trends['sma20'][dates[i - 1]]): return False

    return True
