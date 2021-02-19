#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np


# In[ ]:


from common import log


# In[ ]:

from datetime import datetime
from dateutil import tz

import time

def dt_format(dt):
    return datetime.utcfromtimestamp(dt).replace(tzinfo=tz.gettz('UTC')).astimezone(tz.gettz('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')

def to_segment(series, start_index = 0):
    tic = time.perf_counter()
    assert(start_index >= 0)
    width = len(series) - start_index
    segment = np.empty((width, 6))
    for i in range(0, width):
        j = start_index + i
        segment[i] = np.array(series[j])
        # log(i, j, dt_format(series[j][0] / 1000))
    # log(segment)
    toc = time.perf_counter()
    log('{:.3f} ms'.format((toc - tic) * 1000))
    return segment

def guarantee_integrity(series, interval, appended_only):
    i = len(series) - 1 if appended_only else 1
    while i < len(series):
#         log(len(series), i, series[i][0] - series[i - 1][0], interval, series[i])
        stagnant = int((series[i][0] - series[i - 1][0]) / interval) - 1
        if stagnant == 0:
            i += 1
            continue
        for j in range(stagnant):
            last = series[i - 1][2]
            series.insert(i + j, [series[i - 1][0] + interval * (j + 1), last, last, last, last, 0])
#             log('inserted', series[i + j])
        i += 1
    log(len(series))

def check_integrity(series, interval):
    for i in range(1, len(series)):
#         log(series[i - 1], series[i], series[i][0] - series[i - 1][0], interval)
        assert series[i][0] - series[i - 1][0] == interval


# In[ ]:


def get_milliseconds(interval_name):
    unit = interval_name[-1:]
    amount = int(interval_name[0:-1])
#     log(unit, amount)
    if unit == 'm':
        return amount * 1000 * 60
    elif unit == 'h':
        return amount * 1000 * 60 * 60
    elif unit == 'D':
        return amount * 1000 * 60 * 60 * 24

# for interval_name in ['1m', '5m', '15m', '30m', '1h', '3h', '12h', '1D']:
# #     get_milliseconds(interval_name)
#     log(interval_name, get_milliseconds(interval_name))


# In[ ]:


import json

class DataManager:

    def __init__(self, symbols_of_interest, candles_of_interest):
        self.candles_index = {}
        self.tickers_index = {}
        self.candles_reverse_index = {}
        self.tickers_reverse_index = {}
        self.candles = {}
        self.tickers = {}
        self.symbols_of_interest = symbols_of_interest
        self.candles_of_interest = candles_of_interest
        self.analyzers = []
        self.analyses = {}

    def reset(self):
        self.candles_index = {}
        self.tickers_index = {}
        self.candles_reverse_index = {}
        self.tickers_reverse_index = {}
        self.candles = {}
        self.tickers = {}
        self.analyzers = []
        self.analyses = {}

    def add_analyzer(self, analyzer, tag):
        self.analyzers.append([analyzer, tag])

    def subscribe(self):
        pass

    async def subscribe(self, websocket):
        for symbol in self.symbols_of_interest:
            for candle in self.candles_of_interest:
                await websocket.send(json.dumps({ 'event': 'subscribe', 'channel': 'candles', 'key': 'trade:' + candle + ':' + symbol }))

    def on_subscribed(self, data):
        log('Subscribed to candle', data['key'], 'on channel', data['chanId'])
        symbol = data['key'].split(':')[2]
        if symbol not in self.candles.keys():
            self.candles[symbol] = {}
        self.candles_index[data['key']] = data['chanId']
        self.candles_reverse_index[data['chanId']] = data['key']

    async def on_candles(self, data, append_only):
        if data[0] not in self.candles_reverse_index:
            return [False]
        chanId = data[0]
        candle_type = self.candles_reverse_index[chanId].split(':')[1]
        interval = get_milliseconds(candle_type)
        symbol = self.candles_reverse_index[chanId].split(':')[2]
        if len(data[1]) == 0:
            log(symbol + ' not cool')
            log(symbol + ' not cool')
            log(symbol + ' not cool')
            log(symbol + ' not cool')
            log(symbol + ' not cool')
            log(symbol + ' not cool')
            log(symbol + ' not cool')
            log(symbol + ' not cool')
            log(symbol + ' not cool')
            return [False]
        if isinstance(data[1][0], list):
            data[1].reverse()
            self.candles[symbol][candle_type] = data[1]
            log('Candles', self.candles_reverse_index[chanId], 'initialized with', len(data[1]), 'candles.')
            guarantee_integrity(self.candles[symbol][candle_type], interval, False)
            check_integrity(self.candles[symbol][candle_type], interval)
            self.update_analyses(symbol, candle_type, 0)
            return [True, symbol, candle_type]
        elif data[1][0] == self.candles[symbol][candle_type][-2][0]:
            log('Redundant candle for {} {}'.format(self.candles_reverse_index[chanId], dt_format(self.candles[symbol][candle_type][-2][0] / 1000)))
            assert self.candles[symbol][candle_type][-2][5] == data[1][5]
            return [False]
        elif data[1][0] == self.candles[symbol][candle_type][-1][0]:
            log('Updating last candle for {} {}'.format(self.candles_reverse_index[chanId], dt_format(self.candles[symbol][candle_type][-1][0] / 1000)))
            log(self.candles[symbol][candle_type][-1])
            log(data[1])
            self.candles[symbol][candle_type][-1] = data[1]
            self.update_analyses(symbol, candle_type, len(self.candles[symbol][candle_type]) - 1)
            return [True, symbol, candle_type]
        else:
            log('Appending new candle for {} {}'.format(self.candles_reverse_index[chanId], dt_format(self.candles[symbol][candle_type][-1][0] / 1000)))
            log(dt_format(self.candles[symbol][candle_type][-2][0] / 1000))
            log(dt_format(self.candles[symbol][candle_type][-1][0] / 1000))
            log(dt_format(data[1][0] / 1000))
            log((data[1][0] - self.candles[symbol][candle_type][-1][0]) / (60 * 1000))
            log((self.candles[symbol][candle_type][-1][0] - self.candles[symbol][candle_type][-2][0]) / (60 * 1000))
            log(interval)
            # assert data[1][0] - self.candles[symbol][candle_type][-1][0] == interval
            # assert data[1][0] - self.candles[symbol][candle_type][-1][0] == self.candles[symbol][candle_type][-1][0] - self.candles[symbol][candle_type][-2][0]
            self.candles[symbol][candle_type].append(data[1])
            guarantee_integrity(self.candles[symbol][candle_type], interval, True)
            check_integrity(self.candles[symbol][candle_type], interval)
            self.update_analyses(symbol, candle_type, len(self.candles[symbol][candle_type]) - 2)
            return [True, symbol, candle_type]

    def update_analyses(self, symbol, candle_type, update_start_index):
        log(symbol, candle_type, update_start_index)
        for analyzer in self.analyzers:
            f = analyzer[0]
            tag = analyzer[1]
            if symbol not in self.analyses.keys():
                self.analyses[symbol] = {}
            if candle_type not in self.analyses[symbol].keys():
                self.analyses[symbol][candle_type] = {}
            if tag not in self.analyses[symbol][candle_type].keys() or update_start_index == 0:
                self.analyses[symbol][candle_type][tag] = []
            tic = time.perf_counter()
            log('before: {: >3}'.format(len(self.analyses[symbol][candle_type][tag])))
            assert(update_start_index >= 0)
            f(self.candles[symbol][candle_type], self.analyses[symbol][candle_type][tag], update_start_index)
            log(' after: {: >3} '.format(len(self.analyses[symbol][candle_type][tag])))
            toc = time.perf_counter()
            log('{:.3f} ms'.format((toc - tic) * 1000))

    def get_segment(self, symbol, candle):
        candle_type = 'trade:' + candle + ':' + symbol
        if candle_type not in self.candles_index:
            return None
        if candle not in self.candles[symbol].keys():
            return None
        return to_segment(self.candles[symbol][candle])


# In[ ]:


def on_candles2(candles, additional_candles, interval):
#     print(candles, len(additional_candles))
    guarantee_integrity(additional_candles, interval, False)
    n = len(candles)
#     print(candles, len(additional_candles))
    j = 0
    if n > 0:
#         print(candles[n - 1])
        if candles[n-1][0] >= additional_candles[0][0]:
            align = None
            for i in range(n):
                if candles[i][0] == additional_candles[0][0]:
                    align = i
            assert align is not None
            for i in range(align, n - 1):
                j = i - align
                assert candles[i] == additional_candles[j]
            j = n - 1 - align
            assert candles[n - 1][0] == additional_candles[j][0]
            candles[n - 1][1] = additional_candles[j][1]
            candles[n - 1][2] = additional_candles[j][2]
            candles[n - 1][3] = additional_candles[j][3]
            candles[n - 1][4] = additional_candles[j][4]
            candles[n - 1][5] = additional_candles[j][5]
            j += 1
    while j < len(additional_candles):
        candles.append(additional_candles[j])
        j += 1
#     print(n, len(additional_candles[j:]), len(candles))
    check_integrity(candles, interval)
    return candles


# In[ ]:




