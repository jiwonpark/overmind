
#%%
import numpy as np

# get_ipython().run_line_magic('matplotlib', 'inline')

import websockets
import json

from common import log

from botson import notify_admin

class Bitfinex:

    def __init__(self):

        file = open('/Users/jiwon/keys/keys.json',mode='r')
        all_of_it = file.read()
        file.close()
        obj = json.loads(all_of_it)
        self.api_key = obj['bitfinex'][0]
        self.api_secret = obj['bitfinex'][1]
        self.bf_orderbook = None
        self.bf_orderbook_history = np.empty((0, 3))
        self.bf_ticker_history = np.empty((0, 2))
        self.snapshot = None

    def feed_bf_orderbook(self, symbol, ts, data):

        snapshot = {}
        # print(symbol, ts, data)
        if isinstance(data[0], list):
            for it in data:
                price = it[0]
                count = it[1]
                amount = it[2]
                assert price not in self.bf_orderbook
                self.bf_orderbook[price] = amount
                # print('obi:', it)
        else:
            price = data[0]
            count = data[1]
            amount = data[2]
            if count > 0:
                if price in self.bf_orderbook:
                    self.bf_orderbook[price] += amount
                else:
                    self.bf_orderbook[price] = amount
            else:
                assert count == 0
                assert price in self.bf_orderbook
                del self.bf_orderbook[price]
            # print('obi:', data)
        lowest_ask = None
        for price in sorted(self.bf_orderbook):
            if self.bf_orderbook[price] > 0:
                highest_bid = price
                assert lowest_ask is None
            elif lowest_ask is None and self.bf_orderbook[price] < 0:
                lowest_ask = price
        assert highest_bid is not None
        assert lowest_ask is not None
        assert highest_bid < lowest_ask
        self.bf_orderbook_history = np.append(self.bf_orderbook_history, [[ts, highest_bid, lowest_ask]], axis=0)
        snapshot['ts'] = ts
        snapshot['bp'] = highest_bid
        snapshot['ap'] = lowest_ask
        self.snapshot = snapshot

    async def producer_bf(self):

        while True:
            bf_ticker_reverse_index = {}
            bf_book_reverse_index = {}
            self.bf_orderbook = {}
            try:
                print('Restarting bf...')
                
                nonce = str(int(time.time() * 10000000))
                auth_string = 'AUTH' + nonce
                auth_sig = hmac.new(self.api_secret.encode(), auth_string.encode(), hashlib.sha384).hexdigest()
                
                payload = {'event': 'auth', 'apiKey': self.api_key, 'authSig': auth_sig, 'authPayload': auth_string, 'authNonce': nonce }
                payload = json.dumps(payload)
                
                ws_bf = await websockets.connect('wss://api.bitfinex.com/ws/2')
                
                await ws_bf.send(json.dumps({ 'event': 'subscribe', 'channel': 'ticker', 'symbol': 'tLTCUSD' }))
                await ws_bf.send(json.dumps({ 'event': 'subscribe', 'channel': 'book', 'symbol': 'tLTCUSD' }))
                
                while 1:
                    data = json.loads(await ws_bf.recv())
                    # print(data)
                    if isinstance(data, list):
                        if data[1] == 'hb':
                            pass
                        elif data[0] in bf_ticker_reverse_index:
                            symbol = bf_ticker_reverse_index[data[0]]
                            self.bf_ticker_history = np.append(self.bf_ticker_history, [[time.time(), data[1][6]]], axis=0)
                            print(symbol, data[1][0], data[1][2], data[1][6])
                            # self.snapshot['last'] = data[1][6]
                            # print('bf:', self.snapshot)
                        elif data[0] in bf_book_reverse_index:
                            # print(data)
                            self.feed_bf_orderbook(bf_book_reverse_index[data[0]], time.time(), data[1])
                    elif data['event'] == 'subscribed':
                        if data['channel'] == 'ticker':
                            bf_ticker_reverse_index[data['chanId']] = data['symbol']
                            print('bf_ticker_reverse_index:', bf_ticker_reverse_index)
                        elif data['channel'] == 'book':
                            bf_book_reverse_index[data['chanId']] = data['symbol']
                            print('bf_book_reverse_index:', bf_book_reverse_index)
            except Exception as e:
                print(e)
            time.sleep(30)

import requests
import pytz
import datetime

def ft(unix_timetamp_in_ms):
    KST = datetime.timezone(datetime.timedelta(hours=9))
    return str(datetime.datetime.fromtimestamp(unix_timetamp_in_ms / 1000, tz=KST))


import traceback
import sys

from upbit import post_limit_order
from upbit import wait_order_fulfillment
from upbit import get_free_balances2
from upbit import start_quickie

class Upbit:

    def __init__(self):
        self.ub_orderbook_history = {}
        self.ub_ticker_history = {}
        self.symbols = []
        self.snapshot = None
        self.min_trade_amount = {
            'KRW': 500,
            'BTC': 0.0005,
            'USDT': 0.0005
        }
        self.free_balances = None
        self.free_balances_timestamp = None

        r = requests.get('https://api.upbit.com/v1/market/all')
        pairs = json.loads(r.content.decode('utf-8'))
        # print(pairs)

        for it in pairs:
            self.symbols.append(it['market'])
            symbol = it['market'].split('-')
            x = symbol[1]
            y = symbol[0]
            if x not in self.ub_orderbook_history:
                self.ub_orderbook_history[x] = {}
            if x not in self.ub_ticker_history:
                self.ub_ticker_history[x] = {}
            if y not in self.ub_orderbook_history[x]:
                self.ub_orderbook_history[x][y] = np.empty((0, 3))
            if y not in self.ub_ticker_history[x]:
                self.ub_ticker_history[x][y] = np.empty((0, 2))
    
    async def check_transitive_arbitrage(self, snapshot, min_make_ratio, max_time_diff_seconds, x, y, z, z_amount):
        # print(x, y1, y2)
        if y in self.ub_orderbook_history and z in self.ub_orderbook_history[y] and self.ub_orderbook_history[y][z].shape[0] > 0 and z in self.ub_orderbook_history[x] and self.ub_orderbook_history[x][z].shape[0] > 0:
            y_z = self.ub_orderbook_history[y][z][-1]
            x_z = self.ub_orderbook_history[x][z][-1]
            a = (y_z[1] * snapshot['bp']) / x_z[2]
            b = x_z[1] / (snapshot['ap'] * y_z[2])
            c = snapshot['ap'] / snapshot['bp']
            t1 = snapshot['ts'] - y_z[0]
            t2 = snapshot['ts'] - x_z[0]
            if t1 < max_time_diff_seconds and t2 < max_time_diff_seconds:
                if a > min_make_ratio:
                    # await start_quickie('KRW-BTC', 10000, 1.002)
                    print('{}\t{}\t{}\t{}\t{:.4f}\t{:.4f}\t{:.4f}\t{:.2f}\t{:.2f}'.format(ft(snapshot['ts'] * 1000), x, y, z, a, b, c, t1, t2))
                    x_amount = z_amount / x_z[2]
                    y_amount = x_amount * snapshot['bp']
                    if self.free_balances is not None and self.free_balances[z]['amount'] > z_amount * 1.01 and self.free_balances[y]['amount'] > y_amount * 1.01:
                    # if True:
                        order = post_limit_order(z + '-' + x, x_amount, x_z[2])
                        log(order)
                        log(post_limit_order(z + '-' + y, -y_amount, y_z[1]))
                        order = await wait_order_fulfillment(order['uuid'])
                        log('{} {}'.format(x_amount, order['executed_volume']))
                        log(post_limit_order(y + '-' + x, -float(order['executed_volume']), snapshot['bp']))
                        self.free_balances = None
                elif b > min_make_ratio:
                    print('{}\t{}\t{}\t{}\t{:.4f}\t{:.4f}\t{:.4f}\t{:.2f}\t{:.2f}'.format(ft(snapshot['ts'] * 1000), x, y, z, a, b, c, t1, t2))
                    y_amount = z_amount / y_z[2]
                    x_amount = y_amount / snapshot['ap']
                    if self.free_balances is not None and self.free_balances[z]['amount'] > z_amount * 1.01 and self.free_balances[y]['amount'] > y_amount * 1.01:
                    # if False:
                        order = post_limit_order(y + '-' + x, x_amount, snapshot['ap'])
                        log(order)
                        log(post_limit_order(z + '-' + y, y_amount, y_z[2]))
                        order = await wait_order_fulfillment(order['uuid'])
                        log('{} {}'.format(x_amount, order['executed_volume']))
                        log(post_limit_order(z + '-' + x, -float(order['executed_volume']), x_z[1]))
                        self.free_balances = None
            now = time.time()
            if self.free_balances is None or now - self.free_balances_timestamp > 10:
                self.free_balances = get_free_balances2()
                self.free_balances_timestamp = now
        # elif y1 == 'USDT' and y2 in self.ub_orderbook_history[x] and self.ub_orderbook_history[x][y2].shape[0] > 0:
        #     fx = 1111
        #     y1_y2 = [0, fx, fx]
        #     x_y2 = self.ub_orderbook_history[x]['KRW'][-1]
        #     a = (snapshot['bp'] * y1_y2[1]) / x_y2[2]
        #     b = x_y2[1] / (snapshot['ap'] * y1_y2[2])
        #     c = snapshot['ap'] / snapshot['bp']
        #     if a > min_make_ratio or b > min_make_ratio:
        #         print('{}\t{}\t{}\t{:.4f}\t{:.4f}\t{:.4f}'.format(x, y1, y2, a, b, c))

    async def producer_ub(self):
        print(self.symbols)
        while True:
            ws_ub = await websockets.connect('wss://api.upbit.com/websocket/v1')
            await ws_ub.send(json.dumps([ { "ticket" : "test" } ,{"format":"SIMPLE"}, {"type":"orderbook", "codes" : self.symbols}, { "type" : "ticker", "codes" : self.symbols } ]))
            try:
                while 1:
                    data = json.loads(await ws_ub.recv())
                    # print(data)
                    symbol = data['cd'].split('-')
                    x = symbol[1]
                    y = symbol[0]
                    if data['ty'] == 'ticker':
                        now = time.time()
                        self.ub_ticker_history[x][y] = np.append(self.ub_ticker_history[x][y], [[now, data['tp']]], axis=0)
                        # print('ub', data['tp'])
                        # {'ty': 'ticker', 'cd': 'KRW-LTC', 'op': 107300.0, 'hp': 107650.0, 'lp': 100000.0, 'tp': 101000.0, 'pcp': 107200.0, 'atp': 1570438236.214195, 'c': 'FALL', 'cp': 6200.0, 'scp': -6200.0, 'cr': 0.0578358209, 'scr': -0.0578358209, 'ab': 'ASK', 'tv': 17.24103294, 'atv': 15105.92397352, 'tdt': '20190809', 'ttm': '171327', 'ttms': 1565370807000, 'aav': 7523.65477131, 'abv': 7582.26920221, 'h52wp': 173000.0, 'h52wdt': '2019-06-12', 'l52wp': 25040.0, 'l52wdt': '2018-12-07', 'ts': None, 'ms': 'ACTIVE', 'msfi': None, 'its': False, 'dd': None, 'mw': 'NONE', 'tms': 1565370807605, 'atp24h': 1926291918.7091465, 'atv24h': 18411.92718214, 'st': 'SNAPSHOT'}
                    elif data['ty'] == 'orderbook':
                        snapshot = {}
                        snapshot['ts'] = data['tms'] / 1000
                        snapshot['ts_'] = time.time()
                        snapshot['bp'] = data['obu'][0]['bp']
                        snapshot['ap'] = data['obu'][0]['ap']
                        # print('ub:', symbol, snapshot)
                        self.ub_orderbook_history[x][y] = np.append(self.ub_orderbook_history[x][y], [[snapshot['ts'], snapshot['bp'], snapshot['ap']]], axis=0)
                        self.snapshot = snapshot
                        if snapshot['bp'] > 0:
                            await self.check_transitive_arbitrage(snapshot, 1.0035, 0.3, x, y, 'KRW', 20000)
            except websockets.exceptions.ConnectionClosedError as e:
                log(repr(e))
                notify_admin(repr(e))
            # except Exception as e:
            #     traceback.print_exc()
            #     sys.exit()
            time.sleep(30)

import time
import hmac, hashlib

import matplotlib.pyplot as plt

import asyncio

class Arbiter:

    def __init__(self):
        self.bitfinex = Bitfinex()
        self.upbit = Upbit()

    async def start(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.bitfinex.producer_bf())
        loop.create_task(self.upbit.producer_ub())

    async def plot(self, interval):

        buy = None
        sell = None
        last_snapshot_ts = 0

        while True:

            await asyncio.sleep(1)

            bf = self.bitfinex.snapshot
            ub = self.upbit.snapshot
            bf_orderbook_history = self.bitfinex.bf_orderbook_history
            ub_orderbook_history = self.upbit.ub_orderbook_history
            bf_ticker_history = self.bitfinex.bf_ticker_history
            ub_ticker_history = self.upbit.ub_ticker_history

            if bf is not None and ub is not None:
                if buy != ub['ap'] / bf['bp'] or sell != ub['bp'] / bf['ap']:
                    buy = ub['ap'] / bf['bp']
                    sell = ub['bp'] / bf['ap']
                    ub_age = (time.time() - ub['ts_']) * 1000
                    if ub_age < 1000:
                        # for price in sorted(self.bf_orderbook):
                        #     print(price, ':', self.bf_orderbook[price])
                        print(int(round(buy)), int(round(sell)), bf['bp'], bf['ap'], ((bf['ap'] - bf['bp']) / bf['bp'] * 100), int((ub['ts_'] - ub['ts']) * 1000), int(ub_age))
                        # print('==================================')

            # ts = time.time()
            # if ts - last_snapshot_ts > interval:
            #     last_snapshot_ts = ts
            #     print('here')
            #     plt.plot(bf_orderbook_history[:,0], bf_orderbook_history[:,1], color='green')
            #     plt.plot(bf_orderbook_history[:,0], bf_orderbook_history[:,2], color='red')
            #     plt.plot(ub_orderbook_history[:,0], ub_orderbook_history[:,1] / 1185, color='blue')
            #     plt.plot(ub_orderbook_history[:,0], ub_orderbook_history[:,2] / 1185, color='orange')
            #     plt.plot(bf_ticker_history[:,0], bf_ticker_history[:,1], color='black')
            #     plt.plot(ub_ticker_history[:,0], ub_ticker_history[:,1] / 1185, color='black')
            #     plt.show()


#%%
from common import running_in_notebook

if not running_in_notebook():
    arbiter = Arbiter()
    loop = asyncio.get_event_loop()
    loop.create_task(arbiter.start())
    loop.run_until_complete(arbiter.plot(5))
    loop.close()
    # await arbiter.plot(5)

#%%
