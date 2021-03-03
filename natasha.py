from upbit_helpers import *

import time

r = requests.get('https://api.upbit.com/v1/market/all')
pairs = json.loads(r.content.decode('utf-8'))
candidates = []
day_candles_histories = {}
for it in pairs:
    symbol = it['market']
    base_currency = symbol[:symbol.find('-')] # KRW-XRP 이런 이름에서 '-'를 찾아 그 앞부분을 취한다.
    if base_currency != 'KRW': # KRW 기반이 아닌 건 스킵
        continue
    print('{} {} {}'.format(symbol, it['korean_name'], it['english_name']))
    candidates.append(symbol)
    # candles = get_day_candle(symbol)
    # history = get_standard_minute_candles_history_upbit(candles)
    # for i in range(history.shape[0]):
    #     print(stringify_standard_candle(history[i]))
    # print(np.average(history[:,VOLUME_INDEX]))
    # time.sleep(0.05)

def is_between(x, min, max):
    return min < x and x < max

def history_condition_1(minute_history, i):
    match = True

    dt = datetime.datetime.fromtimestamp(minute_history[i, TIMESTAMP_INDEX])
    seconds_since_midnight = (dt - dt.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    # match = match and seconds_since_midnight == 9 * 60 * 60
    # # match = match and seconds_since_midnight % (60 * 60) == 0

    # match = match and is_between(minute_history[i - 3, PRICE_CHANGE_RATIO_INDEX] * 100, -1, 1)
    # match = match and is_between(minute_history[i - 2, PRICE_CHANGE_RATIO_INDEX] * 100, -1, 1)
    # match = match and is_between(minute_history[i - 1, PRICE_CHANGE_RATIO_INDEX] * 100, 2, 5)

    # match = match and minute_history[i - 3, VOLUME_RATIO_INDEX] > 1
    match = match and minute_history[i - 2, VOLUME_RATIO_INDEX] < 1
    match = match and minute_history[i - 1, VOLUME_RATIO_INDEX] > 2

    match = match and minute_history[i - 3, VOLUME_KRW_INDEX] < 5000 * 10000
    match = match and minute_history[i - 2, VOLUME_KRW_INDEX] < 5000 * 10000
    match = match and minute_history[i - 1, VOLUME_KRW_INDEX] < 5000 * 10000

    return match

MINUTES = 1

def history_condition(minute_history, series, i = 0):
    match = True

    wide_trend = series.ema15
    narrow_trend = series.ema5

    if wide_trend[series.dates[i-1]] / wide_trend[series.dates[i-1-20]] < 1.000:
        return False
    if narrow_trend[series.dates[i-1]] / narrow_trend[series.dates[i-1-5]] < 1.000:
        return False

    past_n = 10
    previous_diff = None
    for j in range(past_n):
        diff = wide_trend[series.dates[i-1-j]] - narrow_trend[series.dates[i-1-j]]
        if diff < 0:
            return False
        # if not (previous_diff is None or previous_diff > diff):
        #     return False
        previous_diff = diff

    return match

def this_candle_condition(this_candle, series, i = 0):
    match = True

    match = match and this_candle[OPEN_INDEX] < series.ema15[series.dates[i - 1]]
    match = match and this_candle[HIGH_INDEX] > series.ema15[series.dates[i - 1]]

    return match


from analyze_correlation import Series

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

max_snapshots = 7

def test(symbol):
    print(symbol)
    candles = get_minute_candle(symbol, MINUTES)
    # for it in candles:
    #     print(json.dumps(it))
    history = get_standard_minute_candles_history_upbit(candles)

    past_size = 60
    future_size = 20

    snapshots_count = 0

    series = Series(history[:,:6])
    for i in range(past_size, history.shape[0] - future_size):
        if not history_condition(history[:i], series, i):
            continue
        if not this_candle_condition(history[i], series, i):
            continue
        if snapshots_count == 0:
            fig = plt.figure(figsize=(20 * max_snapshots, 7))
            gs_all = gridspec.GridSpec(1, max_snapshots, figure=fig)
        if snapshots_count < max_snapshots:
            ax = fig.add_subplot(gs_all[0, snapshots_count])
            series.draw(ax, i)
            snapshots_count += 1
        print(symbol)
        print(stringify_standard_candle(history[i - 4]))
        print(stringify_standard_candle(history[i - 3]))
        print(stringify_standard_candle(history[i - 2]))
        print(stringify_standard_candle(history[i - 1]))
        print(stringify_standard_candle(history[i], bcolors.OKGREEN if history[i, PRICE_HIGH_RATIO_INDEX] * 100 > 3 else bcolors.FAIL))
        print(stringify_standard_candle(history[i + 1]))
        print(stringify_standard_candle(history[i + 2]))
        print(stringify_standard_candle(history[i + 3]))

    if snapshots_count > 0:
        print('Rendering...')
        fig.savefig("output/upbit-{}-1m.png".format(symbol), bbox_inches='tight', dpi=100)
        plt.close(fig)
        print('done')

last_request_time = time.time()
MIN_INTERVAL_SECONDS = 0.1

async def lurk(symbol):
    global last_request_time
    while True:
        now = time.time()
        if now - last_request_time < MIN_INTERVAL_SECONDS:
            time.sleep(MIN_INTERVAL_SECONDS - (now - last_request_time))
        last_request_time = time.time()
        candles = get_minute_candle(symbol, MINUTES)
        history = get_standard_minute_candles_history_upbit(candles)
        series = Series(history[:,:6])
        history_match = history_condition(history, series, history.shape[0])
        now = time.time()
        print('{:<9} {}'.format(symbol, str(datetime.datetime.fromtimestamp(history[-1, TIMESTAMP_INDEX]))))
        if history[-1, TIMESTAMP_INDEX] < now and not history_match:
            await asyncio.sleep(30)
            continue
        print(stringify_standard_candle(history[-4]))
        print(stringify_standard_candle(history[-3]))
        print(stringify_standard_candle(history[-2]))
        print(stringify_standard_candle(history[-1]))
        dt = candles[0]['candle_date_time_kst']
        timestamp = int(datetime.datetime(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]), int(dt[11:13]), int(dt[14:16]), int(dt[17:19])).timestamp())
        this_candle = [timestamp, candles[0]['opening_price'], None, candles[0]['high_price'], candles[0]['low_price'], candles[0]['candle_acc_trade_volume'], candles[0]['candle_acc_trade_price'], None, None, None]
        this_candle_match = this_candle_condition(this_candle, series)
        if this_candle_match:
            print(stringify_standard_candle(this_candle, bcolors.OKGREEN))
            # await start_quickie(symbol, 800000, [1.002, 1.003, 1.004, 1.005, 1.01, 1.02, 1.05, 1.1])
            # await start_quickie(symbol, 500000, [1.002, 1.003, 1.005, 1.01, 1.1])
            await start_quickie(symbol, 600000, [1.002, 1.002, 1.005, 1.005, 1.01, 1.1])
        else:
            print(stringify_standard_candle(this_candle, bcolors.OKBLUE))
        print(candles[0])
        await asyncio.sleep(1)

print(len(candidates))

# for symbol in candidates:
#     test(symbol)
#     time.sleep(MIN_INTERVAL_SECONDS)
# exit()

loop = asyncio.get_event_loop()
for symbol in candidates:
    loop.create_task(lurk(symbol))
loop.run_forever()
