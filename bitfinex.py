#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from common import log

from botson import notify_admin
from botson import send_photo_to_admin


# In[ ]:


cfg = None
symbol = None


# In[ ]:


import json

file = open('./keys.json',mode='r')
all_of_it = file.read()
file.close()
obj = json.loads(all_of_it)
api_key = obj['bitfinex'][0]
api_secret = obj['bitfinex'][1]

# const WebSocket = require('ws')

# const wss = new WebSocket('wss://api.bitfinex.com/ws/2')
# wss.onmessage = (msg) => console.log(msg.data)
# wss.onopen = () => {
#   // API keys setup here (See "Authenticated Channels")
# 

def ff(x):
    if x is None:
        return 'None  '
    else:
        return '{:.3f}'.format(x)

import datetime

def ft(unix_timetamp_in_ms):
    KST = datetime.timezone(datetime.timedelta(hours=9))
    return str(datetime.datetime.fromtimestamp(unix_timetamp_in_ms / 1000, tz=KST))

import time


# In[ ]:


#PYTHON 3.4
import requests
import json
import base64
import hashlib
import time
import hmac

import json

def get(api):
    base = 'https://api.bitfinex.com'
    bitfinexKey = obj['bitfinex'][0]
    bitfinexSecret = str.encode(obj['bitfinex'][1])

    payloadObject = {
            'request':api,
            'nonce':str(time.time() * 100000), #convert to string
            'options':{}
    }

    payload_json = json.dumps(payloadObject)
    print("payload_json: ", payload_json)

    payload = base64.b64encode(bytes(payload_json, "utf-8"))
    print("payload: ", payload)

    m = hmac.new(bitfinexSecret, payload, hashlib.sha384)
    m = m.hexdigest()

    #headers
    headers = {
        'X-BFX-APIKEY' : bitfinexKey,
        'X-BFX-PAYLOAD' : base64.b64encode(bytes(payload_json, "utf-8")),
        'X-BFX-SIGNATURE' : m
    }

#     r = requests.get(bitfinexorderURL, data={}, headers=headers).json()
#     print("Response is: ", r)

    r = requests.get(base + api, data={}, headers=headers)
#     print('Response Code: ' + str(r.status_code))
#     print('Response Header: ' + str(r.headers))
#     print('Response Content: '+ str(r.content))
    return r

def post(api, data):
    base = 'https://api.bitfinex.com'
    bitfinexKey = obj['bitfinex'][0]
    bitfinexSecret = str.encode(obj['bitfinex'][1])

    payloadObject = {
            'request':api,
            'nonce':str(time.time() * 100000) #convert to string
    }
    for key in data:
        payloadObject[key] = data[key]
    log(payloadObject)
    
    payload_json = json.dumps(payloadObject)
    print("payload_json: ", payload_json)

    payload = base64.b64encode(bytes(payload_json, "utf-8"))
    print("payload: ", payload)

    m = hmac.new(bitfinexSecret, payload, hashlib.sha384)
    m = m.hexdigest()

    #headers
    headers = {
        'X-BFX-APIKEY' : bitfinexKey,
        'X-BFX-PAYLOAD' : base64.b64encode(bytes(payload_json, "utf-8")),
        'X-BFX-SIGNATURE' : m
    }

#     r = requests.get(bitfinexorderURL, data={}, headers=headers).json()
#     print("Response is: ", r)

    r = requests.post(base + api, json=payloadObject, headers=headers)
#     print('Response Code: ' + str(r.status_code))
#     print('Response Header: ' + str(r.headers))
#     print('Response Content: '+ str(r.content))
    return r

def post2(api, data):
    base = 'https://api.bitfinex.com'
    bitfinexKey = obj['bitfinex'][0]
    bitfinexSecret = str.encode(obj['bitfinex'][1])

    bodyObject = {}
    for key in data:
        bodyObject[key] = data[key]
#     log(bodyObject)
    
    nonce = str(time.time() * 1000)
    
    body = json.dumps(bodyObject)
#     print("body: ", body)
    
    signature = '/api' + api + nonce + body
    
    sig = hmac.new(bitfinexSecret, signature.encode('utf-8'), hashlib.sha384)
    sig = sig.hexdigest()

    #headers
    headers = {
        'bfx-nonce' : nonce,
        'bfx-apikey' : bitfinexKey,
        'bfx-signature' : sig
    }

#     r = requests.get(bitfinexorderURL, data={}, headers=headers).json()
#     print("Response is: ", r)

    r = requests.post(base + api, json=bodyObject, headers=headers)
#     print('Response Code: ' + str(r.status_code))
#     print('Response Header: ' + str(r.headers))
#     print('Response Content: '+ str(r.content))
    return r

from data_manager import DataManager

import ssl
import websockets
import yaml

import hmac, hashlib

from time import sleep

import math

partial_reposition_amount_ratio = 0.5
partial_reposition_price_ratio = 1.01

from helper import get_skim_amount

class Bitfinex:
    mos = {}
    mos_last_update_time = 0
    tb = {}
    stop_and_limit_price_pairs = {}
    positions = None
    orders = None
    pending_order_request = {}
    dm = None

    def __init__(self):
        pass

    def update_mos(self):
        now = time.time() 
        if now - self.mos_last_update_time < 60:
            return True
        self.mos_last_update_time = now
        res = get('/v1/symbols_details')
        data = json.loads(res.content)
        if 'error' in data:
            log(res.content) # { "error": "ERR_RATE_LIMIT"}'
            return False
        for item in data:
            # log(item)
            # log(item['pair'], item['minimum_order_size'])
            self.mos['t' + item['pair'].upper()] = float(item['minimum_order_size'])
        # log(self.mos[symbol])
        return True

    def update_tradable_balance(self):
        res = post2('/v2/auth/r/info/margin/sym_all', {})
        log(res.content) # ["error",10100,"apikey: invalid"]
        data = json.loads(res.content)
        if data[0] == "error":
            notify_admin(res.content)
            return
        for item in data:
            # log(item)
            self.tb[item[1]] = min(float(item[2][2]), float(item[2][3]))

    def query_orders(self, symbol, direction, type = None, gid = None):
        assert self.orders is not None
        if symbol not in self.orders:
            return []
        result = []
        # for order_id in self.orders[symbol]:
        #     order = self.orders[symbol][order_id]
        for order_id, order in self.orders[symbol].items():
            # log(order)
            if type is not None and order['type'] != type:
                continue
            if gid is not None:
                if gid == 0 and order['gid'] is not None or gid != 0 and (order['gid'] is None or order['gid'] % 1000 != gid):
                    continue
            if direction > 0 and order['amount'] > 0 or direction < 0 and order['amount'] < 0:
                # log(order)
                result.append(order)
        return result

    def get_total_order_amount(self):
        amount = 0
        for order in self.orders:
            amount += order['amount']
        return amount

    def pending_order_request_exists(self, symbol):
        if symbol in self.pending_order_request:
            log('pending_order_request:', self.pending_order_request)
            assert self.pending_order_request[symbol] >= 0
            if self.pending_order_request[symbol] > 0:
                log('pending_order_request', self.pending_order_request)
                return True
        return False

    # async def place_trailing_stop_order(self, symbol, amount, price_trailing):
    #     log('flowcheck', symbol, amount, price_trailing)
    #     assert amount != 0
    #     if symbol in self.pending_order_request:
    #         self.pending_order_request[symbol] += 1
    #     else:
    #         self.pending_order_request[symbol] = 1
    #     await self.ws.send(json.dumps([
    #         0,
    #         "on",
    #         0,
    #         {
    #             "gid": 3,
    #             "cid": 1234522267,
    #             "type": "TRAILING STOP",
    #             "symbol": symbol,
    #             "amount": str(amount),
    #             "price_trailing": str(price_trailing)
    #         }
    #         ]
    #     ))

    async def place_stop_order(self, symbol, amount, price, reduce_only, group_id):
        log('flowcheck', symbol, amount, price, group_id)
        assert amount != 0
        if symbol in self.pending_order_request:
            self.pending_order_request[symbol] += 1
        else:
            self.pending_order_request[symbol] = 1
        order = {
            "cid": 1234522267,
            "type": "STOP",
            "symbol": symbol,
            "amount": str(amount),
            "price": str(price),
            "flags": 1024 if reduce_only else 0
        }
        if group_id is not None:
            order["gid"] = group_id
        await self.ws.send(json.dumps([
            0,
            "on",
            0,
            order,
        ]))

    async def place_limit_order(self, symbol, amount, price, reduce_only, group_id):
        log('flowcheck', symbol, amount, price, group_id)
        assert amount != 0
        if symbol in self.pending_order_request:
            self.pending_order_request[symbol] += 1
        else:
            self.pending_order_request[symbol] = 1
        order = {
            "cid": 1234522267,
            "type": "LIMIT",
            "symbol": symbol,
            "amount": str(amount),
            "price": str(price),
            "flags": 1024 if reduce_only else 0
        }
        if group_id is not None:
            order["gid"] = group_id
        await self.ws.send(json.dumps([
            0,
            "on",
            0,
            order
        ]))
        log('pending_order_request:', self.pending_order_request)

    async def prorder(self, symbol, amount, limit_stop_price, limit_price, timeout, group_id):
        log('flowcheck', symbol, amount, limit_stop_price, limit_price, timeout, group_id)
        assert amount != 0
        if symbol in self.pending_order_request:
            self.pending_order_request[symbol] += 2
        else:
            self.pending_order_request[symbol] = 2

        order = {
            "cid": 1234522267,
            "type": "STOP LIMIT",
            "symbol": symbol,
            "amount": str(-amount),
            "price": str(limit_stop_price),
            "price_aux_limit": str(limit_price)
        }
        if group_id is not None:
            order["gid"] = group_id
        await self.ws.send(json.dumps([
            0,
            "on",
            0,
            order
        ]))

        order = {
            "cid": 1234522267,
            "type": "LIMIT",
            "symbol": symbol,
            "amount": str(amount),
            "price": str(limit_stop_price)
        }
        if group_id is not None:
            order["gid"] = group_id
        await self.ws.send(json.dumps([
            0,
            "on",
            0,
            order
        ]))
        log('pending_order_request:', self.pending_order_request)

    async def place_oco_order(self, symbol, amount, limit_price, stop_price, reduce_only, group_id):
        log('flowcheck', symbol, amount, limit_price, stop_price, group_id)
        assert amount != 0
        await self.place_stop_order(symbol, amount, stop_price, reduce_only, group_id)
        await self.place_limit_order(symbol, amount, limit_price, reduce_only, group_id)

    async def place_oco_order_v1(self, symbol, amount, limit_price, stop_price, group_id):
        log('flowcheck', symbol, amount, limit_price, stop_price, group_id)
        assert amount != 0
        if symbol in self.pending_order_request:
            self.pending_order_request[symbol] += 2
        else:
            self.pending_order_request[symbol] = 2
        order = {
            "cid": 1234522267,
            "type": "LIMIT",
            "symbol": symbol,
            "amount": str(amount),
            "price": str(limit_price),
            "price_oco_stop": str(stop_price),
            "flags": 16384
        }
        if group_id is not None:
            order["gid"] = group_id
        await self.ws.send(json.dumps([
            0,
            "on",
            0,
            order
        ]))

    async def update_order_price(self, order, price):
        log('flowcheck', order, price)
        # symbol = order['symbol']
        # if symbol in self.pending_order_request:
        #     self.pending_order_request[symbol] += 1
        # else:
        #     self.pending_order_request[symbol] = 1
        await self.ws.send(json.dumps([
            0,
            "ou",
            0,
            {
                "id": order['id'],
                "price": str(price)
            }
        ]))

    async def update_order_amount(self, order_id, new_amount):
        log('flowcheck', order_id, new_amount)
        await self.ws.send(json.dumps([
            0,
            "ou",
            0,
            {
                "id": order_id,
                "amount": str(new_amount)
            }
        ]))
    
    async def cancel_order(self, order_id):
        # if symbol in self.pending_order_request:
        #     self.pending_order_request[symbol] += 1
        # else
        #     self.pending_order_request[symbol] = 1
        log('flowcheck', order_id)
        await self.ws.send(json.dumps([
            0,
            "oc",
            0,
            {
                "id": order_id,
            }
        ]))

    async def on_position_update(self, data):
        position = data[2]
        symbol = position[0]
        # notify_admin(json.dumps(position))
        if position[2] == 0:
            if symbol in self.positions:
                del self.positions[symbol]
                log('Deleted position for', symbol)
        elif position[7] is not None:
            if symbol in self.positions and self.positions[symbol]['amount'] * position[2] < 0: # Abnormal state: opposite direction amount
                del self.positions[symbol]
            if symbol not in self.positions:
                self.positions[symbol] = {}
            self.positions[symbol]['time'] = time.time()
            self.positions[symbol]['amount'] = position[2]
            self.positions[symbol]['price'] = position[3]
            self.positions[symbol]['pl'] = position[6]
            self.positions[symbol]['plp'] = position[7]
            self.positions[symbol]['dirty'] = False
            if 'peak_amount' not in self.positions[symbol] or self.positions[symbol]['peak_amount'] > 0 and self.positions[symbol]['peak_amount'] < position[2] or self.positions[symbol]['peak_amount'] < 0 and self.positions[symbol]['peak_amount'] > position[2]:
                self.positions[symbol]['peak_amount'] = position[2]
                log('Updated position peak amount ', self.positions[symbol])
        # await websocket.send(json.dumps({ 'event': 'subscribe', 'channel': 'ticker', 'symbol': symbol }))
        # log('flowcheck', self.positions)
        # await normalize_liquidations(websocket, symbol)
        # await cancel_all_for_volatility_breakthrough_orders(symbol)

    async def on_positions(self, data):
        if self.positions is None:
            self.positions = {}
        log(data[2])
        # notify_admin(json.dumps(data[2]))
        # if self.positions is None:
        #     self.positions = {}
        for symbol, position in self.positions.items():
            position['dirty'] = True
            log('Previous data:', symbol, position)
        for position in data[2]:
            symbol = position[0]
            if position[2] == 0:
                if symbol in self.positions:
                    del self.positions[symbol]
                    log('Deleted position for', symbol)
            self.positions[symbol] = {'amount': position[2], 'price': position[3], 'pl': position[6], 'plp': position[7], 'time': time.time(), 'dirty': False, 'peak_amount': position[2]}
            notify_admin(json.dumps(self.positions[symbol]))
            # await websocket.send(json.dumps({'event': 'subscribe', 'channel': 'ticker', 'symbol': position[0]}))
            # await normalize_liquidations(websocket, symbol)
            # await cancel_all_for_volatility_breakthrough_orders(symbol)
        self.positions = { symbol:position for symbol, position in self.positions.items() if not position['dirty'] }    
        for symbol, position in self.positions.items():
            log('Checked data:', symbol, position)
            notify_admin('{} {} {}'.format(symbol, position['amount'], position['price']))

    async def on_orders(self, data):
        # for order in data[2]:
        #     await self.cancel_order(order[0])
        if self.orders is not None:
            return
        self.orders = {}
        for order in data[2]:
            order_id = order[0]
            group_id = order[1]
            symbol = order[3]
            amount = order[6]
            order_type = order[8]
            price = order[16]
            log(order_id, symbol, amount, price, order_type)
            if symbol not in self.orders:
                self.orders[symbol] = {}
            self.orders[symbol][order_id] = {'id': order_id, 'gid': group_id, 'symbol': symbol, 'amount': amount, 'price': price, 'type': order_type}
        # if self.positions is not None:
        # for symbol in self.positions:
        #     await normalize_liquidations(websocket, symbol)
        #     await cancel_all_for_volatility_breakthrough_orders(symbol)

    async def process_stop_and_limit_price_pairs(self, symbol):
        assert symbol not in self.pending_order_request or self.pending_order_request[symbol] == 0
        reduction_amount = self.get_total_order_amount(query_orders(symbol, -self.positions[symbol]['amount'], 'STOP', 999))
        expansion_amount = self.get_total_order_amount(query_orders(symbol, self.positions[symbol]['amount'], 'LIMIT', 999))
        log(reduction_amount, expansion_amount)
        if abs(reduction_amount) > abs(expansion_amount):
            log('REDUCTION EXCEEDS EXPANSION!')
            self.stop_and_limit_price_pairs[symbol] = []
        else:
            if len(self.stop_and_limit_price_pairs[symbol]) > 0:
                order_info = self.stop_and_limit_price_pairs[symbol].pop(0)
                await self.place_stop_order(symbol, -order_info[0], order_info[1], False, order_info[3])
                await self.place_limit_order(symbol, order_info[0], order_info[2], False, order_info[3])
                log(self.stop_and_limit_price_pairs)

    async def on_new_order(self, data):
        # log(data)
        order = data[2]
        order_id = order[0]
        group_id = order[1]
        symbol = order[3]
        amount = order[6]
        order_type = order[8]
        price = order[16]
        log('flowcheck', order_id, symbol, amount, price, order_type)
        if symbol not in self.orders:
            self.orders[symbol] = {}
        self.orders[symbol][order_id] = {'id': order_id, 'gid': group_id, 'symbol': symbol, 'amount': amount, 'price': price, 'type': order_type}
        if order[28] == 'API>BFX':
            self.pending_order_request[symbol] -= 1
            log('pending_order_request:', self.pending_order_request)
            if self.pending_order_request[symbol] == 0:
                notify_admin('New order(s) for {} complete!'.format(symbol))
                # await self.process_stop_and_limit_price_pairs(symbol)

    async def on_update_order(self, data):
        log('flowcheck', data)
        order = data[2]
        order_id = order[0]
        # group_id = order[1]
        symbol = order[3]
        amount = order[6]
        order_type = order[8]
        price = order[16]
        self.orders[symbol][order_id]['amount'] = amount
        self.orders[symbol][order_id]['price']= price
        # self.pending_order_request[symbol] -= 1
        notify_admin('Order update for {} success!'.format(symbol))

    async def on_close_order(self, data):
        log('flowcheck', data)
        order = data[2]
        order_id = order[0]
        group_id = order[1]
        symbol = order[3]
        original_amount = order[7]
        order_type = order[8]
        price = order[17]
        if symbol in self.orders and order_id in self.orders[symbol]:
            del self.orders[symbol][order_id]
        # if order[13] != 'CANCELED':
        #     position_amount = self.positions[symbol]['amount']
        #     price = self.positions[symbol]['price']
        #     if position_amount != 0:
        #         await place_trailing_stop_order(websocket, symbol, -position_amount, price * 0.01)
        if order[13] == 'CANCELED':
            if order[28] == 'API>BFX':
                # assert symbol in self.pending_order_request
                # self.pending_order_request[symbol] -= 1
                # log('Order canceled - pending_order_request:', self.pending_order_request[symbol])
                pass
        else:
            # if order_type != 'TRAILING STOP':
            # if group_id != 999 and group_id != 9999:
            #     await self.create_liquidation(symbol, price, original_amount)
            notify_admin('Order fulfilled: {} {} {} {}'.format(group_id, symbol, original_amount, price))
            if symbol in self.positions:
                self.positions[symbol]['dirty'] = True
        # # TODO: position directionality
        # if original_amount > 0:
        #     await self.place_limit_order(symbol, -original_amount * partial_reposition_amount_ratio, price * partial_reposition_price_ratio, False, None)
        # else:
        #     await self.place_limit_order(symbol, -original_amount, price / partial_reposition_price_ratio, False, None)

    async def on_ticker(self, data):
        log(data)
        log(data[1][6])

    async def cancel_orders(self, group_id, symbol, long, short):
        if self.orders is None or symbol not in self.orders:
            return
    #     log('orders({}): {}'.format(len(self.orders), self.orders))
        i = 0
        for order_id in self.orders[symbol]:
            order = self.orders[symbol][order_id]
            log('order:', order)
            if group_id is not None:
                if group_id != 0 and order['gid'] % 1000 != group_id if group_id == 0 else order['gid'] is not None:
                    continue
            log(i)
            if (long and order['amount'] > 0) or (short and order['amount'] < 0):
                i += 1
                r = post('/v1/order/cancel', {'order_id': order_id})
                log(r)
                if symbol in self.pending_order_request:
                    self.pending_order_request[symbol] += 1
                else:
                    self.pending_order_request[symbol] = 1

    async def place_stop_limit_orders(self, group_id, symbol, amount, ppps):
        assert amount != 0
        if symbol in self.pending_order_request:
            self.pending_order_request[symbol] += len(ppps)
        else:
            self.pending_order_request[symbol] = len(ppps)
        for it in ppps:
            log(it)
            await self.ws.send(json.dumps([
                0,
                "on",
                0,
                {
                    "gid": group_id if group_id is not None else 0,
                    "cid": 1234522267,
                    "type": "STOP LIMIT",
                    "symbol": symbol,
                    "amount": str(amount),
                    "price": str(it[0]),
                    "price_aux_limit": str(it[1])
                }
                ]
            ))
        log(self.pending_order_request)
        notify_admin('Requested {} stop limit orders'.format(len(ppps)))

    async def run(self, configuration, data_manager, actor):
        log('gogo')
        notify_admin('bitfinex loop is up and running!')
        # send_photo_to_admin()

        global cfg
        global symbol

        if configuration is not None:
            cfg = configuration
        
        if data_manager is None:
            self.dm = DataManager(cfg.symbols_of_interest, cfg.candles_of_interest)
        else:
            self.dm = data_manager
        
        append_only = actor is None

        self.update_mos()
        
        nonce = str(int(time.time() * 10000000))
        auth_string = 'AUTH' + nonce
        auth_sig = hmac.new(api_secret.encode(), auth_string.encode(),
                            hashlib.sha384).hexdigest()

        payload = {'event': 'auth', 'apiKey': api_key, 'authSig': auth_sig,
                'authPayload': auth_string, 'authNonce': nonce }
        payload = json.dumps(payload)

    #     Print JSON
    #     log(json.dumps(payload, ensure_ascii=False, indent="\t") )

    #     async with websockets.connect('wss://api.bitfinex.com/ws/2', ssl=ssl_context) as websocket:
        async with websockets.connect('wss://api.bitfinex.com/ws/2') as websocket:
            self.ws = websocket
            await websocket.send(payload)
    #         await websocket.send(json.dumps({ 'event': 'subscribe', 'channel': 'bu' }))
            await self.dm.subscribe(websocket)

    #         await websocket.send(json.dumps([
    #                 0,
    #                 "oc",
    #                 0,
    #                 {
    #                     "id": 20707578488
    #                 }
    #             ]
    #         ))

    #         await websocket.send(json.dumps([
    #                 0, 
    #                 'ou', 
    #                 0, 
    #                 { 
    #                     "id": 20707705570, 
    #                     "price": '151.'
    #                 }
    #             ]
    #         ))

    #         await place_trailing_stop_order(websocket, "tETHUSD", 0.2, 3)

    #         await self.place_stop_order(websocket, "tETHUSD", -0.2, 130, False, None)


            while 1:
                data = json.loads(await websocket.recv())
    #             log(data)
                if isinstance(data, list):
                    if data[1] == 'fos':
                        None
                    elif data[1] == 'fcs':
                        None
                    elif data[1] == 'fls':
                        None
                    elif data[1] == 'fls':
                        None
                    elif data[1] == 'ws':
                        None
                    elif data[1] == 'on' and not append_only:
    #                     log('on', data[2][3], data[2][7], data[2][16], data[2][8])
                        await self.on_new_order(data)
                    elif data[1] == 'os' and not append_only:
                        await self.on_orders(data)
                    elif data[1] == 'ou' and not append_only:
                        await self.on_update_order(data)
                    elif data[1] == 'oc' and not append_only:
    #                     log('oc', data[2][3], data[2][7], data[2][16], data[2][8], data[2][13])
    #                     log(data)
                        await self.on_close_order(data)
                    elif data[1] == 'te' and not append_only:
                        log('te', data[2][1], data[2][4], data[2][5], data[2][6])
                    elif data[1] == 'tu' and not append_only:
                        log('tu', data[2][1], data[2][4], data[2][5], data[2][6])
                    elif data[1] == 'ps' and not append_only:
                        await self.on_positions(data)
                    elif data[1] == 'pn' and not append_only:
                        await self.on_position_update(data)
                    elif data[1] == 'pu' and not append_only:
                        await self.on_position_update(data)
                    elif data[1] == 'pc' and not append_only:
                        await self.on_position_update(data)
                    elif data[1] == 'hb':
                        None
                    elif data[0] > 0:
                        result = await self.dm.on_candles(data, append_only)
                        if result[0]:
                            symbol = result[1]
                            if self.positions is not None:
                                if self.orders is not None:
                                    # if symbol not in self.positions or not self.positions[symbol]['dirty']:
                                    if True:
                                        if not append_only:
                                            assert actor is not None
                                            if self.update_mos():
                                                await actor(self, self.dm, result[1], result[2])
                                    else:
                                        notify_admin('{} position data dirty!'.format(symbol))
                                else:
                                    notify_admin('Orders not yet received!')
                            else:
                                notify_admin('Positions not yet received!')
                        else:
                            log(result)
                    elif data[1] == 'n':
                        # 06/13/2019 06:14:41 PM run: [0, 'n', [1560417281153, 'on-req', None, None, [None, 0, 1234522267, 'tLTCUSD', None, None, -0.6081493395007104, None, 'STOP', None, None, None, None, None, None, None, 130.99514563106794, None, 0, 0, None, None, None, 0, None, None, None, None, None, None, None, None], None, 'ERROR', 'Invalid order: not enough tradable balance for -0.6081493395007104 LTCUSD at 130.99514563106794']]
                        log(data)
                        if data[2][1] == 'on-req' and data[2][6] == 'ERROR':
                            failed_order_symbol = data[2][4][3]
                            assert failed_order_symbol in self.pending_order_request
                            self.pending_order_request[failed_order_symbol] -= 1
                            log('Handle order fail:', self.pending_order_request[failed_order_symbol])
                            notify_admin(json.dumps(data))
                    else:
                        log(data)
                else:
                    if 'caps' in data:
                        None
                    elif 'event' in data:
                        if data['event'] == 'info':
                            None
                        elif data['event'] == 'subscribed':
                            if data['channel'] == 'candles':
                                self.dm.on_subscribed(data)
                            elif data['channel'] == 'ticker':
                                log('Subscribed to ticker:', data['symbol'], data['chanId'])
                            else:
                                log(data)
                        else:
                            log(data)
                    else:
                        log(data)
                sleep(0.001)

    def reset_bf_state(self):
        self.ws = None
        if self.positions is not None:
            for symbol, position in self.positions.items():
                position['dirty'] = True
        self.orders = None
        self.pending_order_request = {}

    def get_order_average(self, symbol, position, type, same_direction, group_id):
        amount = 0
        product_sum = 0
        if symbol not in self.orders:
            return 0, 0
        orders = self.orders[symbol]
        for order_id, order in orders.items():
            # log('{} {}'.format(order_id, yaml.dump(order)))
            if order['type'] == type and (order['amount'] * position['amount'] > 0 if same_direction else order['amount'] * position['amount'] < 0) and (group_id is None or order['gid'] == group_id):
                amount += order['amount']
                product_sum += order['price'] * order['amount']
        if amount != 0:
            log('{} {} {}: {:.8f} {:.2f}'.format(symbol, type, 'dilution' if same_direction else 'liquidation', amount, product_sum / amount))
            return amount, product_sum / amount
        else:
            return 0, 0

    # async def lay_out_smart_sell_orders(self, symbol, amount, max_price, min_price):
    #     unit_amount = self.mos[symbol]
    #     # unit_amount = 50 / max_price
    #     # count = math.floor(amount / self.mos[symbol])
    #     # notify_admin('{:.5f} {:.5f} {} {:.7f}'.format(amount, unit_amount, count, amount % (count * unit_amount)))
    #     count = 100
    #     decrement_amount = amount / count
    #     notify_admin('{:.7f} {:.7f} {} {:.7f}'.format(amount, unit_amount, count, decrement_amount))
    #     price_step = (max_price - min_price + 1) / count
    #     for i in range(count):
    #         stop_price = max_price - i * price_step
    #         await self.place_stop_order(symbol, -(unit_amount + decrement_amount), stop_price, False, 111)
    #         await self.place_limit_order(symbol, unit_amount, stop_price / 1.005, False, 111)

    async def lay_out_smart_sell_orders(self, symbol, amount, max_price, min_price, d, max_deflation_ratio, max_count):
        assert self.positions is not None
        assert symbol in self.positions
        assert self.positions[symbol]['amount'] > 0
        a0 = self.positions[symbol]['amount']
        a1 = self.mos[symbol]
        pr = max_price - min_price
        epr = max_price - max_price / d
        count = ((a0 * max_deflation_ratio) * pr / epr - amount) / a1
        count = math.floor(min(max_count, count))
        if count < 1:
            return
        a2 = amount / count
        exposed_amount = (a1 + a2) * (epr / pr * count)
        assert exposed_amount <= a0 * max_deflation_ratio
        p1 = max_price
        notify_admin('{} {} {} {} {} {} {} {}'.format(a0, a1, a2, max_price, min_price, pr, epr, count))
        for i in range(count):
            p2 = p1 / d
            await self.place_stop_order(symbol, -(a1 + a2), p1, False, 111)
            await self.place_limit_order(symbol, a1, p2, False, 111)
            # log(a1 + a2, a1, p1, p2)
            p1 -= pr / count

    async def lay_out_smart_buy_orders(self, symbol, min_price, max_price, d, max_inflation_ratio, k):
        assert self.positions is not None
        assert symbol in self.positions
        assert self.positions[symbol]['amount'] > 0
        a0 = self.positions[symbol]['amount']
        a1 = self.mos[symbol]
        p0 = self.positions[symbol]['price']
        p1 = min_price
        if p1 <= p0:
            return
        while p1 < max_price:
            p2 = p1 * d
            # print(p0, p1, p2)
            a2 = get_skim_amount(p0, p1, p2, a0, a1) * k ** math.log10((p2 - p0) / p0 * 100)
            await self.place_stop_order(symbol, a1 + a2, p1, False, 222)
            await self.place_limit_order(symbol, -a1, p2, False, 222)
            # log(a1 + a2, a1, p1, p2)
            p1 = p1 * ((d - 1) / ((a0 * max_inflation_ratio) / (a1 + a2)) + 1)

import asyncio

async def main(cfg, data_manager, actor):
    bitfinex = Bitfinex()
    while True:
        log('Vulture gogo')
        bitfinex.reset_bf_state()
        try:
            await bitfinex.run(cfg, data_manager, actor)
        # except IndexError as e:
        #     log(repr(e))
        #     notify_admin(repr(e))
        except websockets.exceptions.ConnectionClosedError as e:
            log(repr(e))
            notify_admin(repr(e))
        except websockets.exceptions.ConnectionClosedOK as e:
            log(repr(e))
            notify_admin(repr(e))
        # except Exception as e:
        #     log(repr(e))
        #     notify_admin(repr(e))
        # except websockets.exceptions.IncompleteReadError as e:
        #     log(repr(e))
        #     notify_admin(repr(e))
        # except websockets.exceptions.ConnectionResetError as e:
        #     log(repr(e))
        #     notify_admin(repr(e))
        # except websockets.exceptions.CancelledError as e:
        #     log(repr(e))
        #     notify_admin(repr(e))
        sleep(30)
