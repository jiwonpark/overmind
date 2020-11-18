
#%%
import numpy as np

# get_ipython().run_line_magic('matplotlib', 'inline')

import websockets
import json

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

class Upbit:

    def __init__(self):
        self.ub_orderbook_history = np.empty((0, 3))
        self.ub_ticker_history = np.empty((0, 2))
        self.snapshot = None

    async def producer_ub(self):
        while True:
            ws_ub = await websockets.connect('wss://api.upbit.com/websocket/v1')
            await ws_ub.send(json.dumps([ { "ticket" : "test" } ,{"format":"SIMPLE"}, {"type":"orderbook", "codes" : ["KRW-LTC"]}, { "type" : "ticker", "codes" : ["KRW-LTC"] } ]))
            try:
                while 1:
                    data = json.loads(await ws_ub.recv())
                    # print(data)
                    if data['ty'] == 'ticker' and data['cd'] == 'KRW-LTC':
                        self.ub_ticker_history = np.append(self.ub_ticker_history, [[time.time(), data['tp']]], axis=0)
                        # print('ub', data['tp'])
                        # {'ty': 'ticker', 'cd': 'KRW-LTC', 'op': 107300.0, 'hp': 107650.0, 'lp': 100000.0, 'tp': 101000.0, 'pcp': 107200.0, 'atp': 1570438236.214195, 'c': 'FALL', 'cp': 6200.0, 'scp': -6200.0, 'cr': 0.0578358209, 'scr': -0.0578358209, 'ab': 'ASK', 'tv': 17.24103294, 'atv': 15105.92397352, 'tdt': '20190809', 'ttm': '171327', 'ttms': 1565370807000, 'aav': 7523.65477131, 'abv': 7582.26920221, 'h52wp': 173000.0, 'h52wdt': '2019-06-12', 'l52wp': 25040.0, 'l52wdt': '2018-12-07', 'ts': None, 'ms': 'ACTIVE', 'msfi': None, 'its': False, 'dd': None, 'mw': 'NONE', 'tms': 1565370807605, 'atp24h': 1926291918.7091465, 'atv24h': 18411.92718214, 'st': 'SNAPSHOT'}
                    elif data['ty'] == 'orderbook' and data['cd'] == 'KRW-LTC':
                        snapshot = {}
                        snapshot['ts'] = data['tms'] / 1000
                        snapshot['ts_'] = time.time()
                        snapshot['bp'] = data['obu'][0]['bp']
                        snapshot['ap'] = data['obu'][0]['ap']
                        # print('ub:', snapshot)
                        self.ub_orderbook_history = np.append(self.ub_orderbook_history, [[snapshot['ts'], snapshot['bp'], snapshot['ap']]], axis=0)
                        self.snapshot = snapshot
            except Exception as e:
                print(e)
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

arbiter = Arbiter()
loop = asyncio.get_event_loop()
loop.create_task(arbiter.start())

#%%
from common import running_in_notebook

if not running_in_notebook():
    # await arbiter.plot(5)
    loop.run_until_complete(arbiter.plot(5))
    loop.close()

#%%
