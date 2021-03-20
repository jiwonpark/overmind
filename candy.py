
from upbit_helpers import *

def history_condition(chart, i):
    match = True

    dates = chart.trends['30m']['dates']

    price_30m = []
    price_30m.append(chart.trends['30m']['sma5'])
    price_30m.append(chart.trends['30m']['sma10'])
    price_30m.append(chart.trends['30m']['sma20'])
    price_30m.append(chart.trends['30m']['sma60'])
    price_30m.append(chart.trends['30m']['sma120'])

    diff_30m = []
    diff_30m.append(chart.trends['30m']['sma5.diff'])
    diff_30m.append(chart.trends['30m']['sma10.diff'])
    diff_30m.append(chart.trends['30m']['sma20.diff'])
    diff_30m.append(chart.trends['30m']['sma60.diff'])
    diff_30m.append(chart.trends['30m']['sma120.diff'])

    diff_diff_30m = []
    diff_diff_30m.append(chart.trends['30m']['sma5.diff.diff'])
    diff_diff_30m.append(chart.trends['30m']['sma10.diff.diff'])
    diff_diff_30m.append(chart.trends['30m']['sma20.diff.diff'])
    diff_diff_30m.append(chart.trends['30m']['sma60.diff.diff'])
    diff_diff_30m.append(chart.trends['30m']['sma120.diff.diff'])

    price = chart.data['30m'][i-1,CLOSE_INDEX]

    match = True

    match = match and (diff_diff_30m[0][dates[i-1]] > 0 or diff_30m[0][dates[i-1]] > 0)
    match = match and (diff_diff_30m[1][dates[i-1]] > 0 or diff_30m[1][dates[i-1]] > 0)
    match = match and (diff_diff_30m[2][dates[i-1]] > 0 or diff_30m[2][dates[i-1]] > 0)
    match = match and (diff_diff_30m[3][dates[i-1]] > 0 or diff_30m[3][dates[i-1]] > 0)
    match = match and (diff_diff_30m[4][dates[i-1]] > 0 or diff_30m[4][dates[i-1]] > 0)
    if not match:
        return False

    # match = match and diff_30m[0][dates[i-1]] > 0
    # match = match and diff_30m[1][dates[i-1]] > 0
    # match = match and diff_30m[2][dates[i-1]] > 0
    # match = match and diff_30m[3][dates[i-1]] > 0
    # match = match and diff_30m[4][dates[i-1]] > 0
    # if not match:
    #     return False

    # maximas = chart.trends['30m']['sma5.maximas']
    # match = match and (i - max(maximas[maximas < i]) > 50 if len(maximas[maximas < i]) > 0 else False)

    # maximas = chart.trends['30m']['sma10.maximas']
    # match = match and (i - max(maximas[maximas < i]) > 50 if len(maximas[maximas < i]) > 0 else False)

    # maximas = chart.trends['30m']['sma20.maximas']
    # match = match and (i - max(maximas[maximas < i]) > 50 if len(maximas[maximas < i]) > 0 else False)

    # maximas = chart.trends['30m']['sma60.maximas']
    # match = match and (i - max(maximas[maximas < i]) > 50 if len(maximas[maximas < i]) > 0 else False)

    # maximas = chart.trends['30m']['sma120.maximas']
    # match = match and (i - max(maximas[maximas < i]) > 50 if len(maximas[maximas < i]) > 0 else False)

    minimas = chart.trends['30m']['sma5.minimas']
    match = match and (i - max(minimas[minimas < i]) < 2  if len(minimas[minimas < i]) > 0 else False)

    # minimas = chart.trends['30m']['sma10.minimas']
    # match = match and (i - max(minimas[minimas < i]) < 2 if len(minimas[minimas < i]) > 0 else False)

    # minimas = chart.trends['30m']['sma20.minimas']
    # match = match and (i - max(minimas[minimas < i]) < 2 if len(minimas[minimas < i]) > 0 else False)

    # minimas = chart.trends['30m']['sma60.minimas']
    # match = match and (i - max(minimas[minimas < i]) < 2 if len(minimas[minimas < i]) > 0 else False)

    # minimas = chart.trends['30m']['sma120.minimas']
    # match = match and (i - max(minimas[minimas < i]) < 2 if len(minimas[minimas < i]) > 0 else False)


    if not match:
        return False

    # if diff_30m[0][dates[i-1]] > 0.0005: # 단기 이동평균선의 직전봉에서의 미분이 너무 크다는 건 이미 가격이 올라버렸다는 것일 수 있으니 거르자
    #     return False

    # if price > price_30m[4][dates[i-1]]:
    #     return False

    # for trend in diff_30m:
    #     print('diff {:f}'.format(trend[dates[i-1]]))
    #     if trend[dates[i-1]] < 0:
    #         return False

    return True

    # for j in range(2):
    #     diff_trend = diff_30m[j]
    #     if diff_trend[dates[i-1-1]] <= 0 and diff_trend[dates[i-1]] > 0: # 기울기가 음에서 양으로 전환됨, 즉 가격의 극소점
    #         for k in range(3, len(price_30m)):
    #             wider_price_trend = price_30m[k]
    #             if price < wider_price_trend[dates[i-1]]: # 현재 가격보다 더 높이 있는 장기 이동평균선이 하나라도 있음 고고
    #                 return True
    #         #     if price > wider_price_trend[dates[i-1]]: # 현재 가격보다 아래 있는 장기 이동평균선이 하나라도 있음 아웃
    #         #         return False
    #         # return True

    # return False

def this_candle_condition(this_candle, chart, i):
    match = True

    # dates = chart.trends['30m']['dates']
    # price_30m = chart.trends['30m']['sma20']

    # match = match and this_candle[OPEN_INDEX] < price_30m[dates[i - 1]]
    # match = match and this_candle[HIGH_INDEX] > price_30m[dates[i - 1]]

    return match

################################################################################################################################################
