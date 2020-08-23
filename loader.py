#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# get_ipython().system('pip install websockets mpl_finance aiohttp pytz')


# In[ ]:


#############################################################################################
#
#  이 부분은 Bitfinex에서 데이터 받아오는 코드인데, API 키가 있어야 함
#
#############################################################################################


# In[ ]:


# from common import log
# from data_manager import DataManager
# from analyzer_legacy import round_down_to_nice_number
# from bitfinex import get
# from bitfinex import run


# # bitfinex_symbol = 'tIOTBTC'
# # bitfinex_symbol = 'tBTCUSD'
# bitfinex_symbol = 'tLTCUSD'
# dm = DataManager([bitfinex_symbol], ['5m', '30m', '1h', '3h', '1D'])
# # dm = DataManager(['tEDOBTC'], ['5m', '30m', '3h', '1D'])
# # dm = DataManager(['BTC', 'ETH', 'ETC', 'XRP', 'DSH', 'LTC', 'XMR'], ['1m', '5m', '15m', '30m', '1h', '3h', '12h', '1D'])
# await run(None, dm, None)


# # log(candles, candles_index)
# analysis_wide = None
# segment = dm.get_segment(bitfinex_symbol, '1h')
# for i in range(segment.shape[0]):
#     segment[i][0] = segment[i][0] / 1000
# log(segment.shape)


# # r = get('/v1/margin_infos')

# # margin_limits = json.loads(r.content)[0]['margin_limits']
# # for ml in margin_limits:
# #     log(ml, round_down_to_nice_number(float(ml['tradable_balance']), 2))


# In[ ]:


#############################################################################################
#
#  여기부터 실행!!! (다른 거래소에서 데이터 받아오기)
#
#############################################################################################


# In[ ]:


import requests

import time
import datetime
import json

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_finance import candlestick2_ohlc

from common import log

def ft(unix_timetamp_in_ms):
    dt = datetime.datetime.utcfromtimestamp(unix_timetamp_in_ms / 1000)
    return str(dt)

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24


# In[ ]:


# # candle_minutes = 3 * 60
# candle_minutes = 5

# period = candle_minutes * MINUTE


# In[ ]:


# # polo_symbol = 'XBTCZUSD'
# # polo_pair = 'USDT_BTC'
# # kraken_symbol = 'XBTUSD'
# # kraken_symbol2 = 'XXBTZUSD'

# polo_symbol = 'XLTCZUSD'
# polo_pair = 'USDT_LTC'
# kraken_symbol = 'LTCUSD'
# kraken_symbol2 = 'XLTCZUSD'

# # dt = datetime.datetime.strptime('2012-02-09', '%Y-%m-%d')
# # dt = datetime.datetime(year=2017, month=8, day=1)
# # ts = time.mktime(dt.timetuple())
# # te = ts + (1000 * DAY)
# # period = 1 * DAY

# segment = np.empty([0, 6])

# dt = datetime.datetime(year=2017, month=7, day=1)
# ts = time.mktime(dt.timetuple())
# tt = time.mktime(datetime.datetime.strptime('2019-09-26', '%Y-%m-%d').timetuple())

# prev = None


# In[ ]:


import pytz
import calendar

def retrieve_polo(polo_pair, candle_minutes, start, end):
    period = candle_minutes * MINUTE
    
    ts = calendar.timegm(datetime.datetime.strptime(start, '%Y-%m-%d').timetuple())
    tt = calendar.timegm(datetime.datetime.strptime(end, '%Y-%m-%d').timetuple())
    
    print(ts % (24*60*60) / 60 / 60)

    prev = None
    segment = np.empty([0, 6])

    while ts < tt:
        print(ft(ts * 1000))
        te = ts + (30 * DAY)

        r = requests.get('https://poloniex.com/public?command=returnChartData&currencyPair=' + polo_pair + '&start=' + str(ts) + '&end=' + str(te) + '&period=' + str(period))
    #     log(r.content)
        candles = json.loads(r.content.decode('utf-8'))
        log(len(candles))
        log(len(candles) / 60 / 24 * 5)
        log(ft(candles[0]['date'] * 1000), 'candles[0][\'date\']')

        last_candle_not_finished = None
        for i in range(len(candles)):
            time.sleep(0)
            if prev is not None:
                interval = candles[i]['date'] - prev
    #             log(interval)
                if interval > period:
                    missing_count = int(interval / period) - 1
                    last = segment[-1][2]
                    timestamp = segment[-1][0]
                    for j in range(missing_count):
                        timestamp += period
                        segment = np.append(segment, [[timestamp, last, last, last, last, 0]], axis=0)
                    prev = timestamp
                    last_candle_not_finished = False
                elif interval < period:
                    last_candle_not_finished = True
                else:
                    last_candle_not_finished = False

            if last_candle_not_finished:
                segment[-1] = [segment[-1][0], segment[-1][1], candles[i]['close'], max(segment[-1][3], candles[i]['high']), min(segment[-1][4], candles[i]['low']), segment[-1][5] + candles[i]['volume']]
            else:
                segment = np.append(segment, [[candles[i]['date'], candles[i]['open'], candles[i]['close'], candles[i]['high'], candles[i]['low'], candles[i]['volume']]], axis=0)
                prev = segment[-1][0]

        log(ft(segment[-1,0] * 1000), 'segment[-1,0]')
        ts = te

    log(segment.shape)
#     log(segment)

    np.savetxt('poloniex.{}.{}.csv'.format(polo_pair, period), segment, delimiter=",")
    a = np.genfromtxt('poloniex.{}.{}.csv'.format(polo_pair, period), delimiter=",")

    print(segment.shape)
    print(a.shape)
    
    return segment


# In[ ]:


def retrieve_kraken(candle_minutes):
    kraken_symbol = 'LTCUSD'
    kraken_symbol2 = 'XLTCZUSD'

    period = candle_minutes * MINUTE

    dt = datetime.datetime(year=2017, month=7, day=1)
    ts = time.mktime(dt.timetuple())
#     tt = time.mktime(datetime.datetime.strptime('2019-09-26', '%Y-%m-%d').timetuple())

    r = requests.get('https://api.kraken.com/0/public/OHLC?pair=' + kraken_symbol + '&interval=' + str(candle_minutes) + '&since=' + str(ts))
    log(r.content)
    candles = json.loads(r.content.decode('utf-8'))['result'][kraken_symbol2]
    log(len(candles))
    log(len(candles) / 60 / 24 * candle_minutes)
    # log(candles[0]['open'])

    prev = None
    segment = np.empty([0, 6])

    for i in range(len(candles)):
        if prev is not None:
            interval = candles[i][0] - prev
            log(interval)
            if interval > period:
                missing_count = int(interval / period) - 1
                last = segment[-1][2]
                timestamp = segment[-1][0]
                for j in range(missing_count):
                    timestamp += period
                    segment = np.append(segment, [[timestamp, last, last, last, last, 0]], axis=0)
                prev = timestamp
                print(segment.shape[0])

    #         log(candles[i]['open'], candles[i]['high'], candles[i]['low'], candles[i]['close'])
    #         segment = np.append(segment, [[candles[i]['date'], candles[i]['open'], candles[i]['high'], candles[i]['low'], candles[i]['close']]], axis=0)
    #         segment = np.append(segment, [[candles[i]['date'], candles[i]['open'], candles[i]['close'], candles[i]['high'], candles[i]['low']]], axis=0)
        segment = np.append(segment, [[int(candles[i][0]), float(candles[i][1]), float(candles[i][4]), float(candles[i][2]), float(candles[i][3]), float(candles[i][6])]], axis=0)
    #         log(candles[i])
        prev = segment[-1][0]

    log(segment.shape)
    # log(segment)
    
    return segment

