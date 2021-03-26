from upbit_helpers_2 import *

traders = {}

# async def shit(symbol):
#     for i in range(10):
#         print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ {} {}'.format(symbol, i))
#         await asyncio.sleep(1)

async def engage(service, symbol, type, last_candle, loop):
    chart = charts[symbol]
    now = time.time()
    print('{:<9} {}'.format(symbol, str(datetime.datetime.fromtimestamp(chart.data[type][-1, TIMESTAMP_INDEX]))))
    # if symbol not in traders or traders[symbol].done():
    #     print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    #     traders[symbol] = loop.create_task(shit(symbol))
    #     # await asyncio.sleep(0)
    if not service.history_condition(chart, chart.data[type].shape[0]):
        return
    print(stringify_standard_candle(chart.data[type][-4]))
    print(stringify_standard_candle(chart.data[type][-3]))
    print(stringify_standard_candle(chart.data[type][-2]))
    print(stringify_standard_candle(chart.data[type][-1]))
    this_candle_match = service.this_candle_condition(last_candle, chart, chart.data[type].shape[0])
    if this_candle_match:
        print(stringify_standard_candle(last_candle, bcolors.OKGREEN))
        await start_quickie(symbol, service.amount, service.targets)
        # if symbol not in traders or traders[symbol].done():
        #     # traders[symbol] = loop.create_task(start_quickie(symbol, 60 * 10000, [1.003, 1.004, 1.005, 1.01, 1.05, 1.1]))
        #     # traders[symbol] = loop.create_task(start_quickie(symbol, 100 * 10000, [1.01, 1.02, 1.03, 1.04, 1.05]))
        #     traders[symbol] = loop.create_task(start_quickie(symbol, service.amount, service.targets))
        #     await asyncio.sleep(0)
    else:
        print(stringify_standard_candle(last_candle, bcolors.OKBLUE))

def get_bullishness(chart):
    dates = chart.trends['1m']['dates']
    trends = chart.trends['1m']

    result = 1

    result = result * trends['sma5.diff.diff'][dates[-1]]
    result = result * trends['sma5.diff.diff'][dates[-1]]
    result = result * trends['sma5.diff.diff'][dates[-1]]
    result = result * trends['sma5.diff.diff'][dates[-1]]
    result = result * trends['sma5.diff.diff'][dates[-1]]

    result = result * trends['sma10.diff.diff'][dates[-1]]
    result = result * trends['sma10.diff.diff'][dates[-1]]
    result = result * trends['sma10.diff.diff'][dates[-1]]
    result = result * trends['sma10.diff.diff'][dates[-1]]

    result = result * trends['sma20.diff.diff'][dates[-1]]
    result = result * trends['sma20.diff.diff'][dates[-1]]
    result = result * trends['sma20.diff.diff'][dates[-1]]

    result = result * trends['sma60.diff.diff'][dates[-1]]
    result = result * trends['sma60.diff.diff'][dates[-1]]

    result = result * trends['sma120.diff.diff'][dates[-1]]

    result = result ** trends['sma5v.diff.diff'][dates[-1]]
    result = result ** trends['sma10v.diff.diff'][dates[-1]]
    result = result ** trends['sma20v.diff.diff'][dates[-1]]
    result = result ** trends['sma60v.diff.diff'][dates[-1]]
    result = result ** trends['sma120v.diff.diff'][dates[-1]]

    return result

def get_bullishness_2(chart):
    dates = chart.trends['30m']['dates']
    trends = chart.trends['30m']

    print(trends['sma5.diff'][dates[-1]])
    print(trends['sma10.diff'][dates[-1]])
    print(trends['sma20.diff'][dates[-1]])
    print(trends['sma60.diff'][dates[-1]])
    print(trends['sma120.diff'][dates[-1]])

    print(trends['sma5.diff.diff'][dates[-1]])
    print(trends['sma10.diff.diff'][dates[-1]])
    print(trends['sma20.diff.diff'][dates[-1]])
    print(trends['sma60.diff.diff'][dates[-1]])
    print(trends['sma120.diff.diff'][dates[-1]])

    result = 1

    result = result * trends['sma5.diff.diff'][dates[-1]]

    result = result * trends['sma10.diff.diff'][dates[-1]]

    result = result * trends['sma20.diff.diff'][dates[-1]]

    result = result * trends['sma60.diff.diff'][dates[-1]]

    result = result * trends['sma120.diff.diff'][dates[-1]]

    # result = result ** trends['sma5v.diff.diff'][dates[-1]]
    # result = result ** trends['sma10v.diff.diff'][dates[-1]]
    # result = result ** trends['sma20v.diff.diff'][dates[-1]]
    # result = result ** trends['sma60v.diff.diff'][dates[-1]]
    # result = result ** trends['sma120v.diff.diff'][dates[-1]]

    return result

async def buy(charts):
    a = []
    for symbol in charts:
        bullishness_wide = get_bullishness_2(charts[symbol])
        print(symbol, bullishness_wide)
        if math.isnan(bullishness_wide):
            continue
        if math.isinf(bullishness_wide):
            continue
        if bullishness_wide < 1:
            continue
        bullishness = get_bullishness(charts[symbol])
        if math.isnan(bullishness):
            continue
        if math.isinf(bullishness):
            continue
        a.append([symbol, bullishness])
    a.sort(key=lambda x: x[1], reverse=True)
    print(a)
    for i in range(min(len(a), 3)):
        await start_quickie(a[i][0], 10000, [1.3])

import asyncio

loop = asyncio.get_event_loop()

import brandy
import candy

# brandy.amount = 30 * 10000
# brandy.targets = [1.002, 1.003, 1.003]

brandy.amount = 100000
# brandy.targets = [1.005] # 목표 매도가가 설정된 반감기대로 decay에 의해 낮춰짐을 감안하여 매수가 대비 1.005배 가격에서의 청산(0.5% 익절)을 노려본다.
brandy.targets = [1.05]

# candy.amount = 100 * 10000
# candy.targets = [1.05, 1.3]

import delilah

import elektra

elektra.amount = 1000000
elektra.targets = [1.3]

candidates = []
load_candidates(candidates)
# load_candidates(candidates, True)
# candidates = ['KRW-STEEM', 'KRW-SPND']

charts = {}

async def lurk():
    while True:

        # 모든 코인에 대해 잔고를 남기지 않고 평균매수단가 기준 100000원 어치 단위로 매도 주문을 일괄로 깔아놓는다.
        # 단, 가격 하락 시 처리가 곤란한 짜투리 잔고를 허용하지 않기 위해, 마지막 덩어리가 8000원 어치 미만인 경우 이전 덩어리에 합쳐서 주문을 해놓는다.
        # Decay가 꾸준히 진행되면서 현재가와 매도 목표가의 간극을 기하급수적으로 줄여주는 것을 감안하여,
        # 충분히 긴 시간을 가지고 혹시 모를 단기간의 큰 상승을 노려볼 수 있도록 비현실적으로 높은 매도가(이 경우 매수가의 100배~1000배 가격 사이)에 균등하게 주문들을 깔아준다.
        # 혹시 모를 버그로 인해 매수 주문이 안들어간 경우가 있을 것에 대비하여 30분에 한번 수행해준다.
        enforce_sell(30, 100000, 8000, 100, 1000)

        # await update_charts(candidates, charts, '1D')
        await update_charts(candidates, charts, '30m')
        # await update_charts(candidates, charts, '1m')
        await update_charts(candidates, charts, '1m', engage, elektra, loop)

        # 모든 매도 주문 각각에 대해 매도 주문가와 마지막 시가의 차이를 좁혀준다.
        # 이 경우 30분(반감기)에 한번 꼴로 매도 주문가와 시가의 차이를 반으로 좁혀서 점진적으로 시가에 수렴시켜 체결 가능성을 높힌다.
        # 시가가 매수가보다 하락 시 매도가가 decay되면서 시가를 쫓아가다 손절이 이루어진다.
        # 반감기를 사용자가 설정하긴 하지만, 반감기는 그 설정에 고정된 것이 아니라 탄력적이어서,
        # 추세를 종합적으로 고려하여 하락장 추세이면 그것에 맞게 사용자가 설정한 반감기를 것보다 줄여서 보다 신속한 매도(익절/손절)을 유도하고,
        # 반대로 상승이 예상되면 그에 맞게 반감기를 늘려서 대응한다.
        # 상승장 추세인지 하락장 추세인지는, 전략에 get_narrow_trend_coefficient 및 get_wide_trend_coefficient 함수로 정의돼있는 것을 사용한다.
        decay_sell_orders(charts, 5, delilah)

        # await buy()
    # market_sell_available_amount(symbol)
    # cancel_cheapest_sell_order(symbol)

loop.create_task(lurk())
# loop.create_task(update_charts('1m', test, brandy))
# loop.create_task(update_charts('30m', test, candy))
loop.run_forever()

# cancel_all_sell_orders()
# market_sell_available_amount('KRW-MLK')
# cancel_cheapest_sell_order('KRW-MLK')

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
