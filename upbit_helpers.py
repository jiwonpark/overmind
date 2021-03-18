#-*-coding:utf-8 -*-

# 파일에서 API 키 정보를 읽어들인다.

import json

file = open('keys.json',mode='r')
all_of_it = file.read()
file.close()
obj = json.loads(all_of_it)
access_key = obj['upbit'][0]
secret_key = obj['upbit'][1]

# 읽어들인 키 정보로 sigining된 업비트 서버에 HTTP 요청을 보내는 루틴

import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode

import requests
import time

server_url = 'https://api.upbit.com'

class RequestQuotaManager:
    def __init__(self, max_count_per_second, max_count_per_minute):
        self.max_count_per_second = max_count_per_second
        self.max_count_per_minute = max_count_per_minute
        self.circular_queue = [0] * max_count_per_minute
        self.next_index = 0
    
    def good_to_go(self):
        now = time.time()
        index = self.next_index - self.max_count_per_second
        if index < 0:
            index += self.max_count_per_minute
        # print(self.circular_queue)
        # print(self.circular_queue[self.next_index])
        # print(self.circular_queue[index])
        # print(now - self.circular_queue[self.next_index])
        # print(now - self.circular_queue[index])
        return (now - self.circular_queue[self.next_index] > 60) and (now - self.circular_queue[index] > 1)

    def pace(self):
        now = time.time()
        index = self.next_index - self.max_count_per_second
        if index < 0:
            index += self.max_count_per_minute
        # print(self.circular_queue)
        # print(self.circular_queue[self.next_index])
        # print(self.circular_queue[index])
        # print(now - self.circular_queue[self.next_index])
        # print(now - self.circular_queue[index])
        pause_seconds = max(60 - (now - self.circular_queue[self.next_index]), 1 - (now - self.circular_queue[index]))
        if pause_seconds > 0:
            print('Cool down for {} seconds...'.format(pause_seconds))
            time.sleep(pause_seconds)

    def push(self):
        self.circular_queue[self.next_index] = time.time()
        self.next_index += 1
        if self.next_index == self.max_count_per_minute:
            self.next_index = 0
        if self.next_index > self.max_count_per_minute:
            self.next_index -= self.max_count_per_minute

# https://docs.upbit.com/docs/user-request-guide
order_quota = RequestQuotaManager(8, 200)
exchange_quota = RequestQuotaManager(30, 900)
# candles_quota = RequestQuotaManager(10, 600)
candles_quota = RequestQuotaManager(10, 600)

# last_request_time = time.time()
# MIN_INTERVAL_SECONDS = 0.1

# def keep_interval():
#     global last_request_time
#     now = time.time()
#     if now - last_request_time < MIN_INTERVAL_SECONDS:
#         time.sleep(MIN_INTERVAL_SECONDS - (now - last_request_time))
#     last_request_time = time.time()

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
    
    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    if query_string is None:
        res = requests.get(server_url + api, headers=headers)
    else:
        res = requests.get(server_url + api, params=query, headers=headers)

    if res.status_code == 429:
        time.sleep(10)
        return upbit_get(api, query, query_string)

    print(res.status_code)
    print(res.headers)
    print(res.headers['Remaining-Req'])

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
    
    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}
    
    res = requests.post(server_url + api, params=query, headers=headers)

    while res.status_code == 429:
        res = requests.post(server_url + api, params=query, headers=headers)

    # print(res.status_code)
    # print(res.headers['Remaining-Req'])

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
    
    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}
    
    res = requests.delete(server_url + api, params=query, headers=headers)

    return res.json()

####################################################################################################################################

def get_balances():
    exchange_quota.pace()
    data = upbit_get("/v1/accounts", None, None)
    exchange_quota.push()
    return data

# 차트 정보를 읽어오는 루틴

def get_day_candle(symbol):
    query = {
        'market': symbol,
        'count': 1000
    }
    query_string = urlencode(query).encode()
    candles_quota.pace()
    data = upbit_get("/v1/candles/days", query, query_string)
    candles_quota.push()
    return data

def get_minute_candle(symbol, unit):
    query = {
        'market': symbol,
        'count': 1000
    }
    query_string = urlencode(query).encode()
    candles_quota.pace()
    data = upbit_get("/v1/candles/minutes/" + str(unit), query, query_string)
    candles_quota.push()
    return data

####################################################################################################################################

# 업비트 계좌 조회 및 거래를 위한 기본 루틴들

def get_free_balances():
    free_balances = {}

    data = get_balances()
    # log(data)
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

    data = get_orders('wait')
    for it in data:
        if it['side'] != 'ask':
            continue
        symbol = it['market']
        amount = total_balances[symbol]['amount'] + float(it['remaining_volume'])
        total_balances[symbol] = {'amount': amount, 'price': total_balances[symbol]['price']}

    # import math

    # for it in total_balances:
    #     investment = total_balances[it]['amount'] * total_balances[it]['price']
    #     print(it, ':', total_balances[it], math.floor(investment))
    #     data = get_order_chance(it)
    #     if 'error' not in data:
    #         log(it, ':', total_balances[it], math.floor(investment), data['market']['ask']['min_total'])
    #     else:
    #         log(it, ':', total_balances[it], math.floor(investment), data['error']['name'])
    
    return total_balances

def post_limit_order(symbol, volume, price):
    if volume > 0:
        side = 'bid'
    else:
        side = 'ask'
    # price = '%f' % ceil_to_n_sigdits(price, 4)
    print('order param', symbol, '{:.20f}'.format(volume), price)
    query = {
        'market': symbol,
        'side': side,
        'volume': '{:.20f}'.format(abs(volume)),
        'price': price,
        'ord_type': 'limit',
    }
    query_string = urlencode(query).encode()
    order_quota.pace()
    data = upbit_post("/v1/orders", query, query_string)
    order_quota.push()
    return data

def cancel_order(uuid):
    query = {
        'uuid': uuid
    }
    query_string = urlencode(query).encode()
    order_quota.pace()
    data = upbit_delete("/v1/order", query, query_string)
    order_quota.push()
    return data

def post_market_buy_order(symbol, amount_in_base_currency):
    query = {
        'market': symbol,
        'side': 'bid',
        'price': '%f' % amount_in_base_currency,
        'ord_type': 'price',
    }
    query_string = urlencode(query).encode()
    order_quota.pace()
    data = upbit_post("/v1/orders", query, query_string)
    order_quota.push()
    return data

def get_order(uuid):
    query = {
        'uuid': uuid,
    }
    query_string = urlencode(query)
    query_string = "{0}".format(query_string).encode()

    order_quota.pace()
    data = upbit_get('/v1/order', query, query_string)
    order_quota.push()
    return data

def get_orders(state):
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

    order_quota.pace()
    data = upbit_get("/v1/orders", query, query_string)
    order_quota.push()
    return data

####################################################################################################################################

# 상위 레벨 루틴들

import asyncio

def get_free_balances():
    free_balances = {}

    data = get_balances()
    # print(data)
    for it in data:
        # print(it)
        # print(it['currency'], it['balance'], it['avg_buy_price'], it['unit_currency'])
        if it['currency'] == 'KRW':
            continue
        symbol = it['unit_currency'] + '-' + it['currency']
        amount = float(it['balance'])
        price = float(it['avg_buy_price'])
        free_balances[symbol] = { 'amount': amount, 'price': price }
    
    return free_balances

async def wait_order_fulfillment(order_id, interval = 0.1):
    while True:
        await asyncio.sleep(interval)
        data = get_order(order_id)
        if data['remaining_volume'] is None:
            assert data['side'] == 'bid'
            assert data['ord_type'] == 'price'
            if float(data['executed_volume']) > 0:
                break
        else:
            if float(data['remaining_volume']) == 0:
                break
        print(data)
    print(data['price'], data['remaining_volume'], data['executed_volume'])
    print(data)
    return data

async def market_buy(pair, investment_amount_in_krw):
    data = post_market_buy_order(pair, investment_amount_in_krw)
    # print(data)
    if 'error' in data:
        print(data)
        return None
    order_id = data['uuid']
    data = await wait_order_fulfillment(order_id)
    print('MARKET BUY FULFILLED!')
    return data

import numpy as np
def get_average_price(order):
    a = np.empty((0,2))
    for it in order['trades']:
        price = float(it['price'])
        volume = float(it['volume'])
#         print(price, volume)
        a = np.append(a, [[price, volume]], axis=0)
    average_price = np.average(a[:,0], None, a[:,1])
    return average_price

####################################################################################################################################

import math

def round_up_to_unit(price, get_price_unit):
    unit = get_price_unit(price)
    return math.ceil(price / unit) * unit

upbit_krw_price_unit = [
    [ 2000000, 1000 ],
    [ 1000000, 500 ],
    [ 500000, 100 ],
    [ 100000, 50 ],
    [ 10000, 10 ],
    [ 1000, 5 ],
    [ 100, 1 ],
    [ 10, 0.1 ],
    [ 0, 0.01 ]
]

def get_upbit_krw_price_unit(price_krw):
    for it in upbit_krw_price_unit:
        if price_krw >= it[0]:
            return it[1]

####################################################################################################################################

# async def start_quickie(pair, amount_krw, target_profit_ratio):
#     free_balances = get_free_balances()
#     # print(free_balances)
#     # if pair in free_balances:
#     #     print('Position already exists!')
#     #     return False
#     order = await market_buy(pair, amount_krw)
#     if order is None:
#         return False
#     average_price = get_average_price(order)
#     print(order['executed_volume'], average_price)
#     order = post_limit_order(pair, -float(order['executed_volume']), round_up_to_unit(average_price * target_profit_ratio, get_upbit_krw_price_unit))
#     print('order', order)
#     order_id = order['uuid']
#     data = await wait_order_fulfillment(order_id) 
#     print('LIQUIDATION SELL FULFILLED!')
#     return True

def fp(ratio):
    return '{:.2f}%'.format(ratio * 100 - 100)

async def start_quickie(pair, amount_krw, target_profit_ratios):
    free_balances = get_free_balances()
    # print(free_balances)
    # if pair in free_balances:
    #     print('Position already exists!')
    #     return False
    print('#############################################################################################')
    print('#############################################################################################')
    print('#############################################################################################')
    print('#############################################################################################')
    print('#############################################################################################')
    print('#############################################################################################')
    print('#############################################################################################')
    print('#############################################################################################')
    print('#############################################################################################')
    print('#############################################################################################')
    order = await market_buy(pair, amount_krw)
    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    if order is None:
        return False
    average_bought_price = get_average_price(order)
    print(order['executed_volume'], average_bought_price)
    a0 = float(order['executed_volume'])
    n = len(target_profit_ratios)
    a1 = 0
    orders = []
    for i in range(n):
        if i < n - 1:
            a = a0 / n
        else:
            a = a0 - a1
        orders.append(post_limit_order(pair, -a, round_up_to_unit(average_bought_price * target_profit_ratios[i], get_upbit_krw_price_unit)))
        a1 += a
    for i in range(len(orders)):
        order = orders[i]
        data = await wait_order_fulfillment(order['uuid'], 2)
        target_sell_price = float(order['price'])
        average_sold_price = get_average_price(data)
        amount_sold = float(data['executed_volume'])
        print('here')
        print('LIQUIDATION SELL[{}]@{} ({} {}) ({:.0f} KRW) FULFILLED!'.format(i,
            fp(target_sell_price / average_bought_price),
            fp(average_sold_price / average_bought_price),
            fp(target_profit_ratios[i]),
            (average_sold_price - average_bought_price) * amount_sold))
        print('there')
    return True

####################################################################################################################################

import numpy as np
import datetime

TIMESTAMP_INDEX = 0
OPEN_INDEX = 1
CLOSE_INDEX = 2
HIGH_INDEX = 3
LOW_INDEX = 4
VOLUME_INDEX = 5
VOLUME_KRW_INDEX = 6
VOLUME_RATIO_INDEX = 7
PRICE_CHANGE_RATIO_INDEX = 8
PRICE_HIGH_RATIO_INDEX = 9
MAX_INDEX = 10

def get_standard_minute_candles_history_upbit(raw_data):
    n = len(raw_data)
    # print(raw_data[0])
    history = np.empty((n - 2, MAX_INDEX))
    for i in range(n - 2):
        candle = raw_data[i + 1]
        next_candle = raw_data[i]
        previous_candle = raw_data[i + 2]
        volume = candle['candle_acc_trade_volume']
        volume_krw = candle['candle_acc_trade_price']
        volume_ratio = candle['candle_acc_trade_volume'] / previous_candle['candle_acc_trade_volume']
        price_change_ratio = (next_candle['opening_price'] - candle['opening_price']) / candle['opening_price']
        price_high_ratio = (candle['high_price'] - candle['opening_price']) / candle['opening_price']
        dt = candle['candle_date_time_kst']
        timestamp = int(datetime.datetime(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]), int(dt[11:13]), int(dt[14:16]), int(dt[17:19])).timestamp())
        history[-i-1] = [timestamp, candle['opening_price'], next_candle['opening_price'], candle['high_price'], candle['low_price'], volume, volume_krw, volume_ratio, price_change_ratio, price_high_ratio]
    # print(history.shape)
    return history

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def stringify_standard_candle(candle, color = None):
    if candle[VOLUME_RATIO_INDEX] is not None:
        string = '{} {:>16.2f} {:>11.1f}× {:>9.2f}% {:>9.2f}% {:>15} KRW'.format(
            str(datetime.datetime.fromtimestamp(candle[TIMESTAMP_INDEX])),
            candle[VOLUME_INDEX],
            candle[VOLUME_RATIO_INDEX],
            candle[PRICE_CHANGE_RATIO_INDEX] * 100,
            candle[PRICE_HIGH_RATIO_INDEX] * 100,
            f'{int(candle[VOLUME_KRW_INDEX]):,d}')
    else:
        string = '{} {:>16.2f} {:>11}  {:>9}  {: >9}  {:>15} KRW'.format(
            str(datetime.datetime.fromtimestamp(candle[TIMESTAMP_INDEX])),
            candle[VOLUME_INDEX],
            '',
            '',
            '',
            f'{int(candle[VOLUME_KRW_INDEX]):,d}')
    if color is not None:
        return color + string + bcolors.ENDC
    else:
        return string

####################################################################################################################################

# while True:
#     if not candles_quota.good_to_go():
#         break
#     candles_quota.push()
#     time.sleep(0.1)

# while True:
#     candles_quota.pace()
#     get_day_candle('KRW-BTC')
#     candles_quota.push()

# loop = asyncio.get_event_loop()
# loop.create_task(start_quickie('KRW-BTC', 70000, [1.003, 1.004, 1.005, 1.006, 1.01, 1.02, 1.03]))
# loop.run_forever()
