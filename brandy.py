from upbit_helpers import *

# def history_condition(chart, i):
#     trends = chart.trends['30m']
#     dates = trends['dates']

#     match = True
    
#     match = match and abs(trends['sma5.diff'][dates[i - 1]] - 1) < 0.0005

#     if not match:
#         return False

#     result = 1

#     result = result * trends['sma5.diff.diff'][dates[i - 1]]
#     result = result * trends['sma10.diff.diff'][dates[i - 1]]
#     # result = result * trends['sma20.diff.diff'][dates[i - 1]]
#     # result = result * trends['sma60.diff.diff'][dates[i - 1]]
#     # result = result * trends['sma120.diff.diff'][dates[i - 1]]

#     # result = result * trends['sma5.diff'][dates[i - 1]] ** trends['sma5v.diff'][dates[i - 1]]
#     # result = result * trends['sma10.diff'][dates[i - 1]] ** trends['sma10v.diff'][dates[i - 1]]
#     # result = result * trends['sma20.diff'][dates[i - 1]] ** trends['sma20v.diff'][dates[i - 1]]
#     # result = result * trends['sma60.diff'][dates[i - 1]] ** trends['sma60v.diff'][dates[i - 1]]
#     # result = result * trends['sma120.diff'][dates[i - 1]] ** trends['sma120v.diff'][dates[i - 1]]

#     # result = result * trends['sma5.diff.diff'][dates[i - 1]] ** trends['sma5v.diff.diff'][dates[i - 1]]
#     # result = result * trends['sma10.diff.diff'][dates[i - 1]] ** trends['sma10v.diff.diff'][dates[i - 1]]
#     # result = result * trends['sma20.diff.diff'][dates[i - 1]] ** trends['sma20v.diff.diff'][dates[i - 1]]
#     # result = result * trends['sma60.diff.diff'][dates[i - 1]] ** trends['sma60v.diff.diff'][dates[i - 1]]
#     # result = result * trends['sma120.diff.diff'][dates[i - 1]] ** trends['sma120v.diff.diff'][dates[i - 1]]

#     print('*********************', result)

#     return result > 1

def history_condition(chart, i):
    trends = chart.trends['30m']
    dates = trends['dates']

    match = True

    # match = match and trends['sma5.diff.diff'][dates[i - 1]] > 1
    # match = match and trends['sma10.diff.diff'][dates[i - 1]] > 1
    # match = match and trends['sma20.diff.diff'][dates[i - 1]] > 1
    # match = match and trends['sma60.diff.diff'][dates[i - 1]] > 1
    # match = match and trends['sma120.diff.diff'][dates[i - 1]] > 1

    # match = match and trends['sma5.diff'][dates[i - 1]] > 1
    # match = match and trends['sma10.diff'][dates[i - 1]] > 1
    # match = match and trends['sma20.diff'][dates[i - 1]] > 1
    # # match = match and trends['sma60.diff'][dates[i - 1]] > 1
    # # match = match and trends['sma120.diff'][dates[i - 1]] > 1

    trends = chart.trends['30m']
    dates = trends['dates']

    match = match and trends['sma5.diff.diff'][dates[i - 1]] >= 1
    # match = match and trends['sma10.diff.diff'][dates[i - 1]] >= 1
    match = match and trends['sma20.diff.diff'][dates[i - 1]] >= 1
    # match = match and trends['sma60.diff.diff'][dates[i - 1]] >= 1
    # match = match and trends['sma120.diff.diff'][dates[i - 1]] >= 1

    # match = match and trends['sma5.diff'][dates[i - 1]] < 1.01

    match = match and abs(trends['sma5.diff'][dates[i - 1]] - 1) < 0.001

    match = match and trends['sma5'][dates[i - 1]] < trends['sma5'][dates[i - 3]]
    match = match and trends['sma5'][dates[i - 1]] < trends['sma5'][dates[i - 4]]
    match = match and trends['sma5'][dates[i - 1]] < trends['sma5'][dates[i - 5]]
    match = match and trends['sma5'][dates[i - 1]] < trends['sma5'][dates[i - 6]]
    match = match and trends['sma5'][dates[i - 1]] < trends['sma5'][dates[i - 7]]
    match = match and trends['sma5'][dates[i - 1]] < trends['sma5'][dates[i - 8]]
    match = match and trends['sma5'][dates[i - 1]] < trends['sma5'][dates[i - 9]]
    match = match and trends['sma5'][dates[i - 1]] < trends['sma5'][dates[i - 10]]
    match = match and trends['sma5'][dates[i - 1]] < trends['sma5'][dates[i - 11]]

    match = match and trends['sma20'][dates[i - 1]] < trends['sma20'][dates[i - 3]]
    match = match and trends['sma20'][dates[i - 1]] < trends['sma20'][dates[i - 4]]
    match = match and trends['sma20'][dates[i - 1]] < trends['sma20'][dates[i - 5]]
    match = match and trends['sma20'][dates[i - 1]] < trends['sma20'][dates[i - 6]]
    match = match and trends['sma20'][dates[i - 1]] < trends['sma20'][dates[i - 7]]
    match = match and trends['sma20'][dates[i - 1]] < trends['sma20'][dates[i - 8]]
    match = match and trends['sma20'][dates[i - 1]] < trends['sma20'][dates[i - 9]]
    match = match and trends['sma20'][dates[i - 1]] < trends['sma20'][dates[i - 10]]
    match = match and trends['sma20'][dates[i - 1]] < trends['sma20'][dates[i - 11]]

    # match = match and trends['sma5'][dates[i - 1]] < trends['sma20'][dates[i - 1]]

    return match

def this_candle_condition(this_candle, chart, i):
    return True
    match = True

    dates = chart.trends['1m']['dates']
    price_1m = chart.trends['1m']['sma5']

    match = match and this_candle[OPEN_INDEX] < price_1m[dates[i - 1]]
    match = match and this_candle[HIGH_INDEX] > price_1m[dates[i - 1]]

    return match
