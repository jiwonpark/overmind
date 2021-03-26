
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
    price_30m.append(chart.trends['30m']['sma5r20'])
    price_30m.append(chart.trends['30m']['sma10r20'])

    diff_30m = []
    diff_30m.append(chart.trends['30m']['sma5.diff'])
    diff_30m.append(chart.trends['30m']['sma10.diff'])
    diff_30m.append(chart.trends['30m']['sma20.diff'])
    diff_30m.append(chart.trends['30m']['sma60.diff'])
    diff_30m.append(chart.trends['30m']['sma120.diff'])
    diff_30m.append(chart.trends['30m']['sma5r20.diff'])
    diff_30m.append(chart.trends['30m']['sma10r20.diff'])

    diff_diff_30m = []
    diff_diff_30m.append(chart.trends['30m']['sma5.diff.diff'])
    diff_diff_30m.append(chart.trends['30m']['sma10.diff.diff'])
    diff_diff_30m.append(chart.trends['30m']['sma20.diff.diff'])
    diff_diff_30m.append(chart.trends['30m']['sma60.diff.diff'])
    diff_diff_30m.append(chart.trends['30m']['sma120.diff.diff'])
    diff_diff_30m.append(chart.trends['30m']['sma5r20.diff.diff'])
    diff_diff_30m.append(chart.trends['30m']['sma10r20.diff.diff'])

    price = chart.data['30m'][i-1,CLOSE_INDEX]

    match = True

    # relative_pp = chart.trends['30m']['sma5'][dates[i-2]] / chart.trends['30m']['sma20'][dates[i-2]]
    # relative_p  = chart.trends['30m']['sma5'][dates[i-1]] / chart.trends['30m']['sma20'][dates[i-1]]

    # if relative_p > relative_pp and 0.99 < relative_p and relative_p < 1.0:
    #     return True
    # else:
    #     return False

    # THRESHOLD = 0.005
    # divergence = price_30m[6][dates[i-1]] / price_30m[2][dates[i-1]]
    # # match = match and -THRESHOLD < divergence and divergence < THRESHOLD
    # match = match and -THRESHOLD < divergence and divergence < 0

    # THRESHOLD = 0.0003
    # THRESHOLD = 0.001
    # match = match and -THRESHOLD < diff_30m[0][dates[i-1]] and diff_30m[0][dates[i-1]] < THRESHOLD
    # match = match and -THRESHOLD < diff_30m[1][dates[i-1]] and diff_30m[1][dates[i-1]] < THRESHOLD
    # match = match and -THRESHOLD < diff_30m[2][dates[i-1]] and diff_30m[2][dates[i-1]] < THRESHOLD
    # match = match and -THRESHOLD < diff_30m[3][dates[i-1]] and diff_30m[3][dates[i-1]] < THRESHOLD
    # match = match and -THRESHOLD < diff_30m[4][dates[i-1]] and diff_30m[4][dates[i-1]] < THRESHOLD

    # match = match and price_30m[5][dates[i-1]] < 0
    match = match and price_30m[6][dates[i-1]] < 0

    # match = match and (diff_diff_30m[0][dates[i-1]] > 0)
    match = match and (diff_diff_30m[1][dates[i-1]] > 0)
    # match = match and (diff_diff_30m[2][dates[i-1]] > 0)
    # match = match and (diff_diff_30m[3][dates[i-1]] > 0)
    # match = match and (diff_diff_30m[4][dates[i-1]] > 0)
    if not match:
        return False

    # match = match and diff_30m[0][dates[i-1]] > 0
    # match = match and diff_30m[1][dates[i-1]] > 0
    # match = match and diff_30m[2][dates[i-1]] > 0
    match = match and diff_30m[3][dates[i-1]] > 0
    # match = match and diff_30m[4][dates[i-1]] > 0
    # if not match:
    #     return False
    
    # match = match and price_30m_rel[dates[i-1]] < 0

    if not match:
        return False

# def get_maximas(dates, diff, diffdiff):
#     a = []
#     for i in range(len(diff)):
#         # print(diff[dates[i]], diffdiff[dates[i]])
#         # print(str(mdates.num2date(dates[i])))
#         if -THRESHOLD < diff[dates[i]] and diff[dates[i]] < THRESHOLD and diffdiff[dates[i]] < -THRESHOLD2:
#             a.append(i)
#     return a

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

    dates = chart.trends['30m']['dates']
    match = match and this_candle[OPEN_INDEX] < chart.trends['30m']['sma20'][dates[i - 1]]
    match = match and this_candle[HIGH_INDEX] > chart.trends['30m']['sma20'][dates[i - 1]]

    # data = chart.data['30m']
    # match = match and data[i,VOLUME_RATIO_INDEX] > 3

    return match

################################################################################################################################################
