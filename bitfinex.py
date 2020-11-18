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

file = open('/Users/jiwon/keys/keys.json',mode='r')
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


# In[ ]:


import time

mos = {}
mos_last_update_time = 0

def update_mos():
    global mos_last_update_time
    now = time.time() 
    if now - mos_last_update_time < 60:
        return True
    mos_last_update_time = now
    res = get('/v1/symbols_details')
    data = json.loads(res.content)
    if 'error' in data:
        log(res.content) # { "error": "ERR_RATE_LIMIT"}'
        return False
    for item in data:
#         log(item)
#         log(item['pair'], item['minimum_order_size'])
        mos['t' + item['pair'].upper()] = float(item['minimum_order_size'])
#     log(mos[symbol])
    return True


# In[ ]:


tb = {}

def update_tradable_balance():
    res = post2('/v2/auth/r/info/margin/sym_all', {})
#     log(res.content)
    data = json.loads(res.content)
    for item in data:
#         log(item[1], item[2])
        tb[item[1]] = min(float(item[2][2]), float(item[2][3]))


# In[ ]:

stop_and_limit_price_pairs = {}

positions = {}
orders = None
# positions['tUSDETH'] = {'amount': 1, 'price': 130}
# positions['tUSDETH']['amount'] = 0
# log(positions)

def query_orders(symbol, direction, type = None, gid = None):
    from bitfinex import orders
    assert orders is not None
    result = []
    # for order_id in orders[symbol]:
    #     order = orders[symbol][order_id]
    for order_id, order in orders[symbol].items():
        if type is not None and order['type'] != type:
            continue
        if gid is not None and (order['gid'] is None or order['gid'] % 1000 != gid):
            continue
        if direction > 0 and order['amount'] > 0 or direction < 0 and order['amount'] < 0:
            log(order)
            result.append(order)
    return result

def get_total_order_amount(orders):
    amount = 0
    for order in orders:
        amount += order['amount']
    return amount

pending_order_request = {}

def pending_order_request_exists(symbol):
    if symbol in pending_order_request:
        log('pending_order_request:', pending_order_request)
        assert pending_order_request[symbol] >= 0
        if pending_order_request[symbol] > 0:
            log('pending_order_request', pending_order_request)
            return True
    return False

# async def place_trailing_stop_order(websocket, symbol, amount, price_trailing):
#     log('flowcheck', symbol, amount, price_trailing)
#     assert amount != 0
#     if symbol in pending_order_request:
#         pending_order_request[symbol] += 1
#     else:
#         pending_order_request[symbol] = 1
#     await websocket.send(json.dumps([
#           0,
#           "on",
#           0,
#           {
#             "gid": 3,
#             "cid": 1234522267,
#             "type": "TRAILING STOP",
#             "symbol": symbol,
#             "amount": str(amount),
#             "price_trailing": str(price_trailing)
#           }
#         ]
#     ))

async def place_stop_order(websocket, symbol, amount, price, reduce_only, group_id):
    log('flowcheck', symbol, amount, price, group_id)
    assert amount != 0
    if symbol in pending_order_request:
        pending_order_request[symbol] += 1
    else:
        pending_order_request[symbol] = 1
    await websocket.send(json.dumps([
          0,
          "on",
          0,
          {
            "gid": group_id if group_id is not None else 0,
            "cid": 1234522267,
            "type": "STOP",
            "symbol": symbol,
            "amount": str(amount),
            "price": str(price),
            "flags": 1024 if reduce_only else 0
          }
        ]
    ))

async def place_limit_order(websocket, symbol, amount, price, reduce_only, group_id):
    log('flowcheck', symbol, amount, price, group_id)
    assert amount != 0
    if symbol in pending_order_request:
        pending_order_request[symbol] += 1
    else:
        pending_order_request[symbol] = 1
    await websocket.send(json.dumps([
          0,
          "on",
          0,
          {
            "gid": group_id if group_id is not None else 0,
            "cid": 1234522267,
            "type": "LIMIT",
            "symbol": symbol,
            "amount": str(amount),
            "price": str(price),
            "flags": 1024 if reduce_only else 0
          }
        ]
    ))
    log('pending_order_request:', pending_order_request)

async def prorder(websocket, symbol, amount, limit_stop_price, limit_price, timeout, group_id):
    log('flowcheck', symbol, amount, limit_stop_price, limit_price, timeout, group_id)
    assert amount != 0
    if symbol in pending_order_request:
        pending_order_request[symbol] += 2
    else:
        pending_order_request[symbol] = 2
    await websocket.send(json.dumps([
          0,
          "on",
          0,
          {
            "gid": group_id if group_id is not None else 0,
            "cid": 1234522267,
            "type": "STOP LIMIT",
            "symbol": symbol,
            "amount": str(-amount),
            "price": str(limit_stop_price),
            "price_aux_limit": str(limit_price)
          }
        ]
    ))
    await websocket.send(json.dumps([
          0,
          "on",
          0,
          {
            "gid": group_id if group_id is not None else 0,
            "cid": 1234522267,
            "type": "LIMIT",
            "symbol": symbol,
            "amount": str(amount),
            "price": str(limit_stop_price)
          }
        ]
    ))
    log('pending_order_request:', pending_order_request)

async def place_oco_order(websocket, symbol, amount, limit_price, stop_price, reduce_only, group_id):
    log('flowcheck', symbol, amount, limit_price, stop_price, group_id)
    assert amount != 0
    await place_stop_order(websocket, symbol, amount, stop_price, reduce_only, group_id)
    await place_limit_order(websocket, symbol, amount, limit_price, reduce_only, group_id)

async def place_oco_order_v1(websocket, symbol, amount, limit_price, stop_price, group_id):
    log('flowcheck', symbol, amount, limit_price, stop_price, group_id)
    assert amount != 0
    if symbol in pending_order_request:
        pending_order_request[symbol] += 2
    else:
        pending_order_request[symbol] = 2
    await websocket.send(json.dumps([
          0,
          "on",
          0,
          {
            "gid": group_id if group_id is not None else 0,
            "cid": 1234522267,
            "type": "LIMIT",
            "symbol": symbol,
            "amount": str(amount),
            "price": str(limit_price),
            "price_oco_stop": str(stop_price),
            "flags": 16384
          }
        ]
    ))

async def update_order_price(websocket, order, price):
    log('flowcheck', order, price)
#     symbol = order['symbol']
#     if symbol in pending_order_request:
#         pending_order_request[symbol] += 1
#     else:
#         pending_order_request[symbol] = 1
    await websocket.send(json.dumps([
          0,
          "ou",
          0,
          {
            "id": order['id'],
            "price": str(price)
          }
        ]
    ))

async def update_order_amount(websocket, order_id, new_amount):
    log('flowcheck', order_id, new_amount)
    await websocket.send(json.dumps([
          0,
          "ou",
          0,
          {
            "id": order_id,
            "amount": str(new_amount)
          }
        ]
    ))

    
async def cancel_order(websocket, order_id):
#     if symbol in pending_order_request:
#         pending_order_request[symbol] += 1
#     else
#         pending_order_request[symbol] = 1
    log('flowcheck', order_id)
    await websocket.send(json.dumps([
          0,
          "oc",
          0,
          {
            "id": order_id,
          }
        ]
    ))

async def on_position_update(websocket, data):
    global positions
    position = data[2]
    symbol = position[0]
    if position[2] == 0:
        if symbol in positions:
            del positions[symbol]
            log('Deleted position for', symbol)
    else:
        if symbol in positions and positions[symbol]['amount'] * position[2] < 0: # Abnormal state: opposite direction amount
            del positions[symbol]
        if symbol not in positions:
            positions[symbol] = {}
            positions[symbol]['time'] = time.time()
        positions[symbol]['amount'] = position[2]
        positions[symbol]['price'] = position[3]
        positions[symbol]['pl'] = position[6]
        positions[symbol]['plp'] = position[7]
        positions[symbol]['check'] = True
        if 'peak_amount' not in positions[symbol] or positions[symbol]['peak_amount'] > 0 and positions[symbol]['peak_amount'] < position[2] or positions[symbol]['peak_amount'] < 0 and positions[symbol]['peak_amount'] > position[2]:
            positions[symbol]['peak_amount'] = position[2]
            log('Updated position peak amount ', positions[symbol])
#     await websocket.send(json.dumps({ 'event': 'subscribe', 'channel': 'ticker', 'symbol': symbol }))
#     log('flowcheck', positions)
#     await normalize_liquidations(websocket, symbol)
#     await cancel_all_for_volatility_breakthrough_orders(symbol)

async def on_positions(websocket, data):
    log(data[2])
    global positions
#     if positions is None:
#         positions = {}
    for symbol, position in positions.items():
        position['check'] = False
        log('Previous data:', symbol, position)
    for position in data[2]:
        symbol = position[0]
        if symbol in positions and positions[symbol]['amount'] == position[2] and positions[symbol]['price'] == position[3]:
            positions[symbol]['check'] = True
        else:
            positions[symbol] = {'amount': position[2], 'price': position[3], 'pl': position[6], 'plp': position[7], 'time': time.time(), 'check': True, 'peak_amount': position[2]}
#         await websocket.send(json.dumps({'event': 'subscribe', 'channel': 'ticker', 'symbol': position[0]}))
#         await normalize_liquidations(websocket, symbol)
#         await cancel_all_for_volatility_breakthrough_orders(symbol)
    positions = { symbol:position for symbol, position in positions.items() if position['check'] is True }    
    for symbol, position in positions.items():
        log('Checked data:', symbol, position)

async def on_orders(websocket, data):
#     for order in data[2]:
#         await cancel_order(websocket, order[0])
    global orders
    if orders is not None:
        return
    orders = {}
    for order in data[2]:
        order_id = order[0]
        group_id = order[1]
        symbol = order[3]
        amount = order[6]
        order_type = order[8]
        price = order[16]
        log(order_id, symbol, amount, price, order_type)
        if symbol not in orders:
            orders[symbol] = {}
        orders[symbol][order_id] = {'id': order_id, 'gid': group_id, 'symbol': symbol, 'amount': amount, 'price': price, 'type': order_type}
#     if positions is not None:
#     for symbol in positions:
#         await normalize_liquidations(websocket, symbol)
#         await cancel_all_for_volatility_breakthrough_orders(symbol)

async def process_stop_and_limit_price_pairs(symbol):
    global stop_and_limit_price_pairs
    assert symbol not in pending_order_request or pending_order_request[symbol] == 0
    reduction_amount = get_total_order_amount(query_orders(symbol, -positions[symbol]['amount'], 'STOP', 999))
    expansion_amount = get_total_order_amount(query_orders(symbol, positions[symbol]['amount'], 'LIMIT', 999))
    log(reduction_amount, expansion_amount)
    if abs(reduction_amount) > abs(expansion_amount):
        log('REDUCTION EXCEEDS EXPANSION!')
        stop_and_limit_price_pairs[symbol] = []
    else:
        if len(stop_and_limit_price_pairs[symbol]) > 0:
            order_info = stop_and_limit_price_pairs[symbol].pop(0)
            await place_stop_order(ws, symbol, -order_info[0], order_info[1], False, order_info[3])
            await place_limit_order(ws, symbol, order_info[0], order_info[2], False, order_info[3])
            log(stop_and_limit_price_pairs)

async def on_new_order(websocket, data):
#     log(data)
    order = data[2]
    order_id = order[0]
    group_id = order[1]
    symbol = order[3]
    amount = order[6]
    order_type = order[8]
    price = order[16]
    log('flowcheck', order_id, symbol, amount, price, order_type)
    if symbol not in orders:
        orders[symbol] = {}
    orders[symbol][order_id] = {'id': order_id, 'gid': group_id, 'symbol': symbol, 'amount': amount, 'price': price, 'type': order_type}
    if order[28] == 'API>BFX':
        pending_order_request[symbol] -= 1
        log('pending_order_request:', pending_order_request)
        if pending_order_request[symbol] == 0:
            notify_admin('New order(s) for {} complete!'.format(symbol))
            await process_stop_and_limit_price_pairs(symbol)

async def on_update_order(websocket, data):
    log('flowcheck', data)
    order = data[2]
    order_id = order[0]
#     group_id = order[1]
    symbol = order[3]
    amount = order[6]
    order_type = order[8]
    price = order[16]
    orders[symbol][order_id]['amount'] = amount
    orders[symbol][order_id]['price']= price
#     pending_order_request[symbol] -= 1
    notify_admin('Order update for {} success!'.format(symbol))

async def on_close_order(websocket, data):
    log('flowcheck', data)
    order = data[2]
    order_id = order[0]
    group_id = order[1]
    symbol = order[3]
    original_amount = order[7]
    order_type = order[8]
    price = order[17]
    if symbol in orders and order_id in orders[symbol]:
        del orders[symbol][order_id]
#     if order[13] != 'CANCELED':
#         position_amount = positions[symbol]['amount']
#         price = positions[symbol]['price']
#         if position_amount != 0:
#             await place_trailing_stop_order(websocket, symbol, -position_amount, price * 0.01)
    if order[13] == 'CANCELED':
        if order[28] == 'API>BFX':
            assert symbol in pending_order_request
            pending_order_request[symbol] -= 1
            log('Order canceled - pending_order_request:', pending_order_request[symbol])
    else:
#         if order_type != 'TRAILING STOP':
        if group_id != 999 and group_id != 9999:
            await create_liquidation(websocket, symbol, price, original_amount)
        notify_admin('Order fulfilled: {} {} {} {}'.format(group_id, symbol, original_amount, price))

async def on_ticker(websocket, data):
    log(data)
    log(data[1][6])


# In[ ]:


import requests
import math

async def cancel_orders(ws, group_id, symbol, long, short):
    if orders is None or symbol not in orders:
        return
#     log('orders({}): {}'.format(len(orders), orders))
    i = 0
    for order_id in orders[symbol]:
        order = orders[symbol][order_id]
        log('order:', order)
        if order['gid'] == group_id:
            log(i)
            if (long and order['amount'] > 0) or (short and order['amount'] < 0):
                i += 1
                r = post('/v1/order/cancel', {'order_id': order_id})
                log(r)
                if symbol in pending_order_request:
                    pending_order_request[symbol] += 1
                else:
                    pending_order_request[symbol] = 1

async def place_stop_limit_orders(ws, group_id, symbol, amount, ppps):
    assert amount != 0
    if symbol in pending_order_request:
        pending_order_request[symbol] += len(ppps)
    else:
        pending_order_request[symbol] = len(ppps)
    for it in ppps:
        log(it)
        await ws.send(json.dumps([
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
    log(pending_order_request)
    notify_admin('Requested {} stop limit orders'.format(len(ppps)))

# In[ ]:


from data_manager import DataManager

# In[ ]:


import asyncio
import pathlib
import ssl
import websockets

import time
import hmac, hashlib

from time import sleep

# global positions
# global orders

# global ws

async def run(configuration, data_manager, actor):
    log('gogo')
    notify_admin('bitfinex loop is up and running!')
    # send_photo_to_admin()

    global cfg
    global symbol

    if configuration is not None:
        cfg = configuration
    
    if data_manager is None:
        dm = DataManager(cfg.symbols_of_interest, cfg.candles_of_interest)
    else:
        dm = data_manager
    
    append_only = actor is None

    update_mos()
    
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
        global ws
        ws = websocket
        await websocket.send(payload)
#         await websocket.send(json.dumps({ 'event': 'subscribe', 'channel': 'bu' }))
        await dm.subscribe(websocket)

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

#         await place_stop_order(websocket, "tETHUSD", -0.2, 130, False, None)


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
                    await on_new_order(websocket, data)
                elif data[1] == 'os' and not append_only:
                    await on_orders(websocket, data)
                elif data[1] == 'ou' and not append_only:
                    await on_update_order(websocket, data)
                elif data[1] == 'oc' and not append_only:
#                     log('oc', data[2][3], data[2][7], data[2][16], data[2][8], data[2][13])
#                     log(data)
                    await on_close_order(websocket, data)
                elif data[1] == 'te' and not append_only:
                    log('te', data[2][1], data[2][4], data[2][5], data[2][6])
                elif data[1] == 'tu' and not append_only:
                    log('tu', data[2][1], data[2][4], data[2][5], data[2][6])
                elif data[1] == 'ps' and not append_only:
                    await on_positions(websocket, data)
                elif data[1] == 'pn' and not append_only:
                    await on_position_update(websocket, data)
                elif data[1] == 'pu' and not append_only:
                    await on_position_update(websocket, data)
                elif data[1] == 'pc' and not append_only:
                    await on_position_update(websocket, data)
                elif data[1] == 'hb':
                    None
                elif data[0] > 0:
                    result = await dm.on_candles(data, append_only)
                    if result[0]:
                        if not append_only:
                            assert actor is not None
                            if update_mos():
                                await actor(websocket, dm, result[1], result[2])
                elif data[1] == 'n':
                    # 06/13/2019 06:14:41 PM run: [0, 'n', [1560417281153, 'on-req', None, None, [None, 0, 1234522267, 'tLTCUSD', None, None, -0.6081493395007104, None, 'STOP', None, None, None, None, None, None, None, 130.99514563106794, None, 0, 0, None, None, None, 0, None, None, None, None, None, None, None, None], None, 'ERROR', 'Invalid order: not enough tradable balance for -0.6081493395007104 LTCUSD at 130.99514563106794']]
                    log(data)
                    if data[2][1] == 'on-req' and data[2][6] == 'ERROR':
                        failed_order_symbol = data[2][4][3]
                        assert failed_order_symbol in pending_order_request
                        pending_order_request[failed_order_symbol] -= 1
                        log('Handle order fail:', pending_order_request[failed_order_symbol])
                        notify_admin('Order failed!')
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
                            dm.on_subscribed(data)
                        elif data['channel'] == 'ticker':
                            log('Subscribed to ticker:', data['symbol'], data['chanId'])
                        else:
                            log(data)
                    else:
                        log(data)
                else:
                    log(data)
            sleep(0.001)

def reset_bf_state():
    global ws
    global positions
    global orders
    global pending_order_request
    ws = None
    for symbol, position in positions.items():
        position['check'] = False
    orders = None
    pending_order_request = {}

# def main(cfg, actor):
#     while True:
#         log('Vulture gogo')
#         reset_bf_state()
#         try:
#             loop = asyncio.get_event_loop()
#             loop.run_until_complete(run(cfg, None, actor))
#             loop.close()
#         except Exception as e:
#             log(e)
#         sleep(30)

async def main(cfg, data_manager, actor):
    while True:
        log('Vulture gogo')
        reset_bf_state()
        try:
            await run(cfg, data_manager, actor)
        # except Exception as e:
        except websockets.exceptions.ConnectionClosedError as e:
            log(repr(e))
            notify_admin(repr(e))
        sleep(30)

def get_positions():
    return positions

def get_orders():
    return orders


# In[ ]:

import sys

async def tester1(ws, dm, symbol, candle_type):
    log('hey')
    update_tradable_balance()
#     segment = dm.get_segment(symbol, candle_type)
#     price = segment[-1, 2]
    await cancel_orders(ws, 111, symbol, False, True)
#     price = 57
#     await place_stop_limit_orders(ws, 888, symbol, tb[symbol] / price, price, 1.01, 1.02, 1.005, 10)
#     sys.exit()

async def tester2(ws, dm, symbol, candle_type):
    log('hey')
    update_tradable_balance()
    # if not pending_order_request_exists(symbol):
    #     await aim_for_volatility_breakthrough(symbol, 54, 58, 0, 0, 0, 0)

class Config():
    pass
config = Config()
config.symbols_of_interest = ['tLTCUSD']
# config.candles_of_interest = ['1m', '15m', '1h']
config.candles_of_interest = ['5m']
config.trade_margin_ratio = 1

# await run(config, None, tester2)

from common import running_in_notebook

if not running_in_notebook():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(config, None, tester2))
    loop.close()

# In[ ]:
