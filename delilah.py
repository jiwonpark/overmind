import numpy as np

def trough(chart):
    dates = chart.trends['30m']['dates']
    trends = chart.trends['30m']

    result = True

    result = np.logical_and(result, abs(trends['sma5.diff'] - 1) < 0.005)
    result = np.logical_and(result, abs(trends['sma10.diff'] - 1) < 0.005)
    # result = np.logical_and(result, abs(trends['sma20.diff'] - 1) < 0.005)

    return result

def safe_to_buy(chart):
    dates = chart.trends['30m']['dates']
    trends = chart.trends['30m']

    result = [1] * len(dates)

    # result = result * trends['sma5v.diff.diff']
    # result = result * trends['sma10v.diff.diff']
    # result = result * trends['sma20v.diff.diff']
    # result = result * trends['sma60v.diff.diff']
    # result = result * trends['sma120v.diff.diff']
    # result = result > 1.01

    # result_price_acc = [1] * len(dates)

    # result_price_acc = result_price_acc * trends['sma5.diff.diff']
    # result_price_acc = result_price_acc * trends['sma10.diff.diff']
    # result_price_acc = result_price_acc * trends['sma20.diff.diff']

    # result_price_acc = result_price_acc > 1.01

    # result = np.logical_and(result, result_price_acc)

    result = np.logical_and(result, trends['sma5v.diff.diff'] > 1.01)
    result = np.logical_and(result, trends['sma10v.diff.diff'] > 1.01)
    result = np.logical_and(result, trends['sma20v.diff.diff'] > 1.01)

    result = np.logical_and(result, trends['sma5.diff.diff'] > 1)
    result = np.logical_and(result, trends['sma10.diff.diff'] > 1)
    result = np.logical_and(result, trends['sma20.diff.diff'] > 1)

    result = np.logical_and(result, trough(chart))

    # result = np.logical_and(result, trends['sma5.diff.diff'] > 1)
    # result = np.logical_and(result, trends['sma10.diff.diff'] > 1)
    # result = np.logical_and(result, trends['sma20.diff.diff'] > 1)

    # result = np.logical_and(result, trends['sma5.diff'] < 1.01)


    # result = np.logical_and(result, trends['sma5.diff'] > 1)
    # result = np.logical_and(result, trends['sma10.diff'] > 1)
    # result = np.logical_and(result, trends['sma20.diff'] > 1)
    # result = np.logical_and(result, trends['sma60.diff'] > 1)
    # result = np.logical_and(result, trends['sma120.diff'] > 1)

    # result = result ** trends['sma5v.diff.diff'][dates[-1]]
    # result = result ** trends['sma10v.diff.diff'][dates[-1]]
    # result = result ** trends['sma20v.diff.diff'][dates[-1]]
    # result = result ** trends['sma60v.diff.diff'][dates[-1]]
    # result = result ** trends['sma120v.diff.diff'][dates[-1]]

    return result

# def safe_to_buy(chart):

def get_narrow_trend_coefficient(charts, symbol):
    chart = charts[symbol]
    trends = chart.trends['30m']
    dates = trends['dates']

    result = 1

    result = result * trends['sma5.diff'][dates[-1]] ** trends['sma5v.diff'][dates[-1]]
    result = result * trends['sma10.diff'][dates[-1]] ** trends['sma10v.diff'][dates[-1]]
    result = result * trends['sma20.diff'][dates[-1]] ** trends['sma20v.diff'][dates[-1]]
    result = result * trends['sma60.diff'][dates[-1]] ** trends['sma60v.diff'][dates[-1]]
    result = result * trends['sma120.diff'][dates[-1]] ** trends['sma120v.diff'][dates[-1]]

    result = result * trends['sma5.diff.diff'][dates[-1]] ** trends['sma5v.diff.diff'][dates[-1]]
    result = result * trends['sma10.diff.diff'][dates[-1]] ** trends['sma10v.diff.diff'][dates[-1]]
    result = result * trends['sma20.diff.diff'][dates[-1]] ** trends['sma20v.diff.diff'][dates[-1]]
    result = result * trends['sma60.diff.diff'][dates[-1]] ** trends['sma60v.diff.diff'][dates[-1]]
    result = result * trends['sma120.diff.diff'][dates[-1]] ** trends['sma120v.diff.diff'][dates[-1]]

    return result

def get_wide_trend_coefficient(charts, symbol):
    chart = charts[symbol]
    trends = chart.trends['1m']
    dates = trends['dates']

    result = 1

    result = result * trends['sma5.diff'][dates[-1]] ** trends['sma5v.diff'][dates[-1]]
    result = result * trends['sma10.diff'][dates[-1]] ** trends['sma10v.diff'][dates[-1]]
    result = result * trends['sma20.diff'][dates[-1]] ** trends['sma20v.diff'][dates[-1]]
    result = result * trends['sma60.diff'][dates[-1]] ** trends['sma60v.diff'][dates[-1]]
    result = result * trends['sma120.diff'][dates[-1]] ** trends['sma120v.diff'][dates[-1]]

    result = result * trends['sma5.diff.diff'][dates[-1]] ** trends['sma5v.diff.diff'][dates[-1]]
    result = result * trends['sma10.diff.diff'][dates[-1]] ** trends['sma10v.diff.diff'][dates[-1]]
    result = result * trends['sma20.diff.diff'][dates[-1]] ** trends['sma20v.diff.diff'][dates[-1]]
    result = result * trends['sma60.diff.diff'][dates[-1]] ** trends['sma60v.diff.diff'][dates[-1]]
    result = result * trends['sma120.diff.diff'][dates[-1]] ** trends['sma120v.diff.diff'][dates[-1]]

    return result
