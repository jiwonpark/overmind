#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from common import log


# In[ ]:


import json

file = open('/Users/jiwon/keys/keys.json',mode='r')
all_of_it = file.read()
file.close()
obj = json.loads(all_of_it)
access_key = obj['upbit'][0]
secret_key = obj['upbit'][1]


# In[ ]:


from common import running_in_notebook
if running_in_notebook():
    get_ipython().run_line_magic('run', './botson.ipynb')
else:
    from botson import notify_admin


# In[ ]:


import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode

import requests

# access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
# secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
# server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']

server_url = 'https://api.upbit.com'

def upbit_get(api, query, query_string):
    global access_key
    global secret_key

    if query_string is None:
        payload = {
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
        }
    else:
        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()
        payload = {
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }
    
    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    if query_string is None:
        res = requests.get(server_url + api, headers=headers)
    else:
        res = requests.get(server_url + api, params=query, headers=headers)

    return res.json()

def upbit_post(api, query, query_string):
    global access_key
    global secret_key

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }
    
    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}
    
    res = requests.post(server_url + api, params=query, headers=headers)

    return res.json()

def upbit_delete(api, query, query_string):
    global access_key
    global secret_key

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }
    
    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}
    
    res = requests.delete(server_url + api, params=query, headers=headers)

    return res.json()

def get_balances():
    return upbit_get("/v1/accounts", None, None)

def get_order_chance(symbol):
    query = {
        'market': symbol,
    }
    query_string = urlencode(query).encode()
    return upbit_get("/v1/orders/chance", query, query_string)

def get_day_candle(symbol):
    query = {
        'market': symbol,
        'count': 1000
    }
    query_string = urlencode(query).encode()
    return upbit_get("/v1/candles/days", query, query_string)

def get_minute_candle(symbol, unit):
    query = {
        'market': symbol,
        'count': 1000
    }
    query_string = urlencode(query).encode()
    return upbit_get("/v1/candles/minutes/" + str(unit), query, query_string)

def post_limit_order(symbol, volume, price):
    if volume > 0:
        side = 'bid'
    else:
        side = 'ask'
    price = '%f' % ceil_to_n_sigdits(price, 4)
#     log('order param', mos, price)
    query = {
        'market': symbol,
        'side': side,
        'volume': abs(volume),
        'price': str(price),
        'ord_type': 'limit',
    }
    query_string = urlencode(query).encode()
    return upbit_post("/v1/orders", query, query_string)

def post_market_buy_order(symbol, amount_in_krw):
    query = {
        'market': symbol,
        'side': 'bid',
        'price': '%f' % amount_in_krw,
        'ord_type': 'price',
    }
    query_string = urlencode(query).encode()
    return upbit_post("/v1/orders", query, query_string)

def post_market_sell_order(symbol, amount):
    query = {
        'market': symbol,
        'side': 'ask',
#         'volume': '%f' % amount,
        'volume': amount,
        'ord_type': 'market',
    }
    query_string = urlencode(query).encode()
    return upbit_post("/v1/orders", query, query_string)


def upbeat_get_orders(state):
    query = {
        'state': state,
    }
    query_string = urlencode(query)

    # uuids = [
    #     '9ca023a5-851b-4fec-9f0a-48cd83c2eaae',
    #     #...
    # ]
    # uuids_query_string = '&'.join(["uuids[]={}".format(uuid) for uuid in uuids])

    # query['uuids[]'] = uuids
    # query_string = "{0}&{1}".format(query_string, uuids_query_string).encode()

    query_string = "{0}".format(query_string).encode()

    return upbit_get("/v1/orders", query, query_string)

def get_order(uuid):
    query = {
        'uuid': uuid,
    }
    query_string = urlencode(query)
    query_string = "{0}".format(query_string).encode()

    return upbit_get('/v1/order', query, query_string)
    
# data = get_order('94db830e-658f-4f46-ba2c-94980c335edf')
# log(data)
# log(data['price'], data['remaining_volume'], data['executed_volume'])

# get_order_chance('KRW-LTC')

# post_limit_order('KRW-LTC', 1, 1000)
# post_limit_order('KRW-LTC', -1, 100000)

# data = upbeat_get_orders('wait')
# for it in data:
#     log(it['uuid'], it['side'], it['market'], it['price'], it['remaining_volume'], it['executed_volume'], it['paid_fee'])


# In[ ]:


def get_free_balances():
    free_balances = {}

    data = get_balances()
#     log(data)
    for it in data:
#         log(it)
#         log(it['currency'], it['balance'], it['avg_buy_price'], it['unit_currency'])
        if it['currency'] == 'KRW':
            continue
        symbol = it['unit_currency'] + '-' + it['currency']
        amount = float(it['balance'])
        price = float(it['avg_buy_price'])
        free_balances[symbol] = { 'amount': amount, 'price': price }
    
    return free_balances

def get_total_balances():
    total_balances = get_free_balances().copy()

    data = upbeat_get_orders('wait')
    for it in data:
        if it['side'] != 'ask':
            continue
        symbol = it['market']
        amount = total_balances[symbol]['amount'] + float(it['remaining_volume'])
        total_balances[symbol] = {'amount': amount, 'price': total_balances[symbol]['price']}

    import math

    for it in total_balances:
        investment = total_balances[it]['amount'] * total_balances[it]['price']
#         log(it, ':', total_balances[it], math.floor(investment))
        data = get_order_chance(it)
#         if 'error' not in data:
#             log(it, ':', total_balances[it], math.floor(investment), data['market']['ask']['min_total'])
#         else:
#             log(it, ':', total_balances[it], math.floor(investment), data['error']['name'])
    
    return total_balances

# 'error' in data and data['error']['name'] == 'validation_error' and data['error']['message'] == 'market does not have a valid value'
# 'error' in data and data['error']['name'] == 'under_min_total_ask' and data['error']['message'] == '최소주문금액 이상으로 주문해주세요'
# 'error' in data and data['error']['name'] == 'insufficient_funds_ask' and data['error']['message'] == '주문가능한 금액(WAX)이 부족합니다.'
# 'error' in data and data['error']['name'] == 'insufficient_funds_ask' and data['error']['message'] == '주문가능한 금액(BTC)이 부족합니다.'
# market_sell: {'error': {'message': '최소 주문 금액은 1000.0 KRW입니다. 시장가 매도시 주문금액은 주문 수량 * 매수 1호가로 계산합니다.', 'name': 'under_min_total_market_ask'}}

# data = post_limit_order('KRW-MER', -1, 100)
# log(data)
# data = post_limit_order('KRW-WAX', -1, 500)
# log(data)
# data = post_limit_order('KRW-IOST', -1, 400)
# log(data)
# data = post_limit_order('KRW-IOST', -1, 500)
# log(data)
# data = post_limit_order('KRW-IOST', -2, 249)
# log(data)
# data = post_limit_order('KRW-IOST', -2, 250)
# log(data)
# data = post_limit_order('KRW-IOST', -1, 5000)
# log(data)

def upbit_cancel_orders(symbol):
    data = upbeat_get_orders('wait')
    for it in data:
        if symbol != it['market']:
            continue
#         log(it)
        query = {
            'uuid': it['uuid']
        }
        query_string = urlencode(query).encode()
        data2 = upbit_delete("/v1/order", query, query_string)
        log(data2)

#     for it in data:
#         log(it['uuid'], it['side'], it['price'], it['market'], it['remaining_volume'], it['executed_volume'], it['paid_fee'])

# free_balances = get_free_balances()
# log('free_balances')
# for it in free_balances:
#     log(it, ':', free_balances[it])

# total_balances = get_total_balances()
# log('total_balances')
# for it in total_balances:
#     log(it, ':', total_balances[it])

# upbit_cancel_orders('KRW-IOST')

import math

def ceil_to_n_sigdits(x, n):
    decimals = 10 ** (n - 1 - int(math.floor(math.log10(abs(x)))))
    return math.ceil(x * decimals) / decimals

def lay_out_liquidation_orders(free_balances, symbol, min_ratio, max_ratio, divisor):
#     free_balances = get_free_balances()
    if symbol not in free_balances:
        log(symbol, 'not in free_balances')
        return
#     log(free_balances[symbol])
    data = get_order_chance(symbol)
#     log('chance', symbol, data)
    if 'error' in data and data['error']['name'] == 'validation_error' and data['error']['message'] == 'market does not have a valid value':
        log('chance', symbol, data)
        return
    log('chance', symbol, data['ask_fee'], data['market']['ask']['min_total'])
    position_amount = free_balances[symbol]['amount']
    position_price = free_balances[symbol]['price']
    min_price = position_price * min_ratio
    max_price = position_price * max_ratio
    mos =  ceil_to_n_sigdits(data['market']['ask']['min_total'] / min_price, 3)
    log('mos', symbol, mos)
    amount = mos
    count = int(math.floor(position_amount / amount))
    if count == 0:
        log('order impossible', symbol, position_amount, amount)
        return
    if count > divisor:
        count = divisor
    amount = position_amount / count
    step = (max_price - min_price) / count
    log('order layout', symbol, position_amount, amount, count)
    for i in range(count):
        if i == count - 1:
            amount = position_amount
        price = min_price + i * step
        data = post_limit_order(symbol, -amount, price)
        position_amount -= amount
#         log(data)
        if 'error' in data: # and data['error']['name'] == 'under_min_total_ask' and data['error']['message'] == '최소주문금액 이상으로 주문해주세요':
            log(data)
            continue
        log('order result', i, symbol, data['uuid'], data['remaining_volume'], data['price'], float(data['price']) / position_price, position_amount)

# data = lay_out_liquidation_orders('KRW-IOST', 1.01, 1.10, 10)
# log(data)

def reset_liquidations():
    free_balances = get_free_balances()
    for it in free_balances:
        log(it, ':', free_balances[it], int(free_balances[it]['amount'] * free_balances[it]['price']))
        upbit_cancel_orders(it)

    free_balances = get_free_balances()
    for it in free_balances:
        log(it, ':', free_balances[it], int(free_balances[it]['amount'] * free_balances[it]['price']))
        data = lay_out_liquidation_orders(free_balances, it, 1.01, 1.10, 1)
    #     log(data)

    free_balances = get_free_balances()
    for it in free_balances:
        log(it, ':', free_balances[it], int(free_balances[it]['amount'] * free_balances[it]['price']))

    log('reset_liquidations done')

# reset_liquidations()


# In[ ]:


import time
import asyncio

# free_balances = get_free_balances()
# for it in free_balances:
#     log(it, ':', free_balances[it], int(free_balances[it]['amount'] * free_balances[it]['price']))
#     upbit_cancel_orders(it)

async def wait_order_fulfillment(order_id):
    while True:
        await asyncio.sleep(1)
        data = get_order(order_id)
        if data['remaining_volume'] is None or float(data['remaining_volume']) == 0:
            break
        log(data)
#         log(data['price'], data['remaining_volume'], data['executed_volume'])

async def market_buy(pair, investment_amount_in_krw):
    data = post_market_buy_order(pair, investment_amount_in_krw)
    log(data)
    if 'error' in data:
        return None
    order_id = data['uuid']
    await wait_order_fulfillment(order_id)
    log('MARKET BUY FULFILLED!')
    return order_id

async def market_sell(pair, amount):
    data = post_market_sell_order(pair, amount)
    log(data)
    if 'error' in data:
        return None
    order_id = data['uuid']
    await wait_order_fulfillment(order_id)
    return order_id

import numpy as np
def get_average_price(order):
    a = np.empty((0,2))
    for it in order['trades']:
        price = float(it['price'])
        volume = float(it['volume'])
#         log(price, volume)
        a = np.append(a, [[price, volume]], axis=0)
    average_price = np.average(a[:,0], None, a[:,1])
    return average_price

def fp(ratio):
    return '{0:.3g}%'.format(round((ratio - 1) * 100, 3))

# ratio = 1.001555
# ratio = 0.9954
# log((ratio - 1) * 100)
# log(round((ratio - 1) * 100, 3))
# log(fp(ratio))

# async def skim(pair, balance, limit_ratio, stop_ratio):
#     position_price = balance['price']
#     position_amount = balance['amount']
#     log('balance', position_price, position_amount)
#     order = post_limit_order(pair, -position_amount, position_price * limit_ratio)
#     log('order', order)
#     order_id = order['uuid']
#     log('liquidation target', float(order['price']) / position_price)
    
#     while True:
#         await asyncio.sleep(1)
#         order = get_order(order_id)
#         if order['remaining_volume'] is None or float(order['remaining_volume']) == 0:
#             break
# #         log(order)
# #         log(order['price'], order['remaining_volume'], order['executed_volume'])
        
#         import requests
#         url = "https://api.upbit.com/v1/ticker"
#         querystring = {"markets":pair}
#         response = requests.request("GET", url, params=querystring)
# #         log('ticker', response.text)
#         ticker = json.loads(response.text)[0]
#         price = float(ticker['trade_price'])
#         log('profit', fp(price / position_price))
#         loss = position_price / price
#         if  loss >= stop_ratio:
#             while True:
#                 upbit_cancel_orders(pair)
#                 order_id = await market_sell(pair, position_amount)
#                 if order_id is not None:
#                     break
#                 await asyncio.sleep(1)
#             order = get_order(order_id)
#             average_price = get_average_price(order)
#             log('stopped at loss', fp(average_price / position_price))
#             break

#     order = get_order(order_id)
#     log(order)
#     average_price = get_average_price(order)
#     log('liquidated at', fp(average_price / position_price), round(average_price - position_price) * position_amount)

#     free_balances = get_free_balances()
# #     log(free_balances)
#     for it in free_balances:
#         if it == pair:
#             log(it)

async def trailing_oco(pair, balance, c):
    position_price = balance['price']
    position_amount = balance['amount']
    log('balance', position_price, position_amount)
    order = post_limit_order(pair, -position_amount, position_price * c.limit_ratio)
    log('order', order)
    order_id = order['uuid']
    log('liquidation target', float(order['price']) / position_price)
    
    stop_ratio = 1 / c.adverse_movement_limit_ratio
    log(fp(c.adverse_movement_limit_ratio), fp(stop_ratio))
    
    while True:
        await asyncio.sleep(1)
        order = get_order(order_id)
        log(order)
        log(order['price'], order['remaining_volume'], order['executed_volume'])
        if order['remaining_volume'] is None or float(order['remaining_volume']) == 0:
            break
        
        import requests
        url = "https://api.upbit.com/v1/ticker"
        querystring = {"markets":pair}
        response = requests.request("GET", url, params=querystring)
#         log('ticker', response.text)
        ticker = json.loads(response.text)[0]
        price = float(ticker['trade_price'])
        log('profit', fp(price / position_price))
        movement_ratio = price / position_price
        if movement_ratio <= stop_ratio:
            while True:
                upbit_cancel_orders(pair)
                order_id = await market_sell(pair, position_amount)
                if order_id is not None:
                    break
                await asyncio.sleep(1)
            order = get_order(order_id)
            average_price = get_average_price(order)
            break
        elif movement_ratio >= c.lossless_ratio * c.lossless_distance_ratio:
            if stop_ratio < c.lossless_ratio:
                log('losslesss secured at', fp(c.lossless_ratio))
                stop_ratio = c.lossless_ratio

    order = get_order(order_id)
    log(order)
    average_price = get_average_price(order)
    log('liquidated at', fp(average_price / position_price), round(average_price - position_price) * position_amount)

    free_balances = get_free_balances()
#     log(free_balances)
    for it in free_balances:
        if it == pair:
            log(it)

# order = get_order('70136643-8f89-4e1c-83d8-511a2df9a38d')
# # log(order)
# average_price = get_average_price(order)
# log(average_price)

async def start_quickie(pair):
    free_balances = get_free_balances()
    log(free_balances)
    if pair in free_balances:
        log('Position already exists!')
        return False
    await market_buy(pair, 2000)
    return True

# class Config():
#     pass

# config_upbit = Config()
# config_upbit.lossless_ratio = 1.0015
# config_upbit.lossless_distance_ratio = 1.0005
# config_upbit.adverse_movement_limit_ratio = 1.0015
# config_upbit.limit_ratio = 1.1
# config_upbit.pair = 'KRW-LTC'

async def handle_liquidations(c):
    notify_admin('handle_liquidations is up and running!')
    while True:
        try:
            pair = c.pair
            upbit_cancel_orders(pair)
            free_balances = get_free_balances()
            log(free_balances)
            if pair in free_balances:
                log('balance', free_balances[pair])
#                 await skim(pair, free_balances[pair], 1.002, 1.002)
                await trailing_oco(pair, free_balances[pair], c)
            await asyncio.sleep(1)
        except Exception as e:
            log(repr(e))
            notify_admin(repr(e))
            await asyncio.sleep(30)

# await market_buy(pair, 1000)
# await handle_liquidations()


# In[ ]:


# res = requests.get('https://api-pub.bitfinex.com/v2/candles/trade:1m:tLTCUSD/hist')
# log(res)
# log(json.loads(res.content))


# In[ ]:


# data = get('/v1/candles/minutes/1?market=KRW-LTC&count=200', None, None)
# # log(data)
# for it in data:
#     log(it['timestamp'], it['opening_price'], it['trade_price'], it['high_price'], it['low_price'], it['candle_acc_trade_volume'], it['candle_date_time_utc'], it['candle_date_time_kst'])


# In[ ]:


from common import running_in_notebook

from data_manager import DataManager
from data_manager import on_candles2
from data_manager import to_segment


# In[ ]:


if running_in_notebook():
    get_ipython().run_line_magic('matplotlib', 'inline')

import matplotlib.pyplot as plt
from mpl_finance import candlestick2_ohlc
from time import sleep
import datetime

candles = []

def upbit_append_candles(data, interval_seconds):
    global candles
    additional_candles = []
    data.reverse()
#     print(len(data))
    for it in data:
        dt = it['candle_date_time_utc']
#         print(dt[0:4], dt[5:7], dt[8:10], dt[11:13], dt[14:16], dt[17:19])
        timestamp = int(datetime.datetime(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]), int(dt[11:13]), int(dt[14:16]), int(dt[17:19])).timestamp())
        additional_candles.append([timestamp, it['opening_price'], it['trade_price'], it['high_price'], it['low_price'], it['candle_acc_trade_volume']])
    candles = on_candles2(candles, additional_candles, interval_seconds)
    npcandles = to_segment(candles)
    return npcandles

# while True:
#     data = get_minute_candle('KRW-BTC', 5)
#     npcandles = upbit_append_candles(data)
#     npcandles = npcandles[-300:,:]
#     fig, ax = plt.subplots()
#     candlestick2_ohlc(ax, npcandles[:,1], npcandles[:,3], npcandles[:,4], npcandles[:,2], width=0.6)
#     plt.show()
#     sleep(5)


# In[ ]:




