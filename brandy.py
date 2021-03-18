
from upbit_helpers import *

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
