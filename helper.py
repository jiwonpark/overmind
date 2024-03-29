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

def get_upbit_btc_price_unit(price_btc):
    return 0.00000001

def get_upbit_usdt_price_unit(price_usdt):
    return 0.001

assert get_upbit_krw_price_unit(1000000) == 500
assert get_upbit_krw_price_unit(999999) == 100
assert get_upbit_krw_price_unit(10) == 0.1
assert get_upbit_krw_price_unit(9.999999999) == 0.01
assert get_upbit_krw_price_unit(0) == 0.01

import math

def round_up_to_unit(price, get_price_unit):
    unit = get_price_unit(price)
    return math.ceil(price / unit) * unit

def round_down_to_unit(price, get_price_unit):
    unit = get_price_unit(price)
    return math.floor(price / unit) * unit

assert round_up_to_unit(2001000, get_upbit_krw_price_unit) == 2001000
assert round_up_to_unit(2000999, get_upbit_krw_price_unit) == 2001000
assert round_up_to_unit(2000001, get_upbit_krw_price_unit) == 2001000
assert round_up_to_unit(2000000, get_upbit_krw_price_unit) == 2000000
assert round_up_to_unit(1999999, get_upbit_krw_price_unit) == 2000000
assert round_up_to_unit(1999001, get_upbit_krw_price_unit) == 1999500
assert round_up_to_unit(1999000, get_upbit_krw_price_unit) == 1999000
assert round_up_to_unit(9.999, get_upbit_krw_price_unit) == 10
assert round_up_to_unit(9.99, get_upbit_krw_price_unit) == 9.99

assert round_down_to_unit(2001000, get_upbit_krw_price_unit) == 2001000
assert round_down_to_unit(2000999, get_upbit_krw_price_unit) == 2000000
assert round_down_to_unit(2000001, get_upbit_krw_price_unit) == 2000000
assert round_down_to_unit(2000000, get_upbit_krw_price_unit) == 2000000
assert round_down_to_unit(1999999, get_upbit_krw_price_unit) == 1999500
assert round_down_to_unit(1999001, get_upbit_krw_price_unit) == 1999000
assert round_down_to_unit(1999000, get_upbit_krw_price_unit) == 1999000
assert round_down_to_unit(9.999, get_upbit_krw_price_unit) == 9.99
assert round_down_to_unit(9.99, get_upbit_krw_price_unit) == 9.99

def get_required_price_for_dilution_target(current_price, current_amount, target_price, dilution_amount):
    assert dilution_amount != 0
    assert dilution_amount * current_amount >= 0
    return (target_price - current_price) * (current_amount / dilution_amount) + target_price

assert get_required_price_for_dilution_target(100, 100, 100, 100) == 100
assert get_required_price_for_dilution_target(100, 100, 101, 100) == 102
assert get_required_price_for_dilution_target(100, 100, 101, 50) == 103

assert get_required_price_for_dilution_target(100, -100, 100, -100) == 100
assert get_required_price_for_dilution_target(100, -100, 99, -100) == 98

def get_bf_orders_min_max_price(orders):
    assert len(orders) > 0
    min = 0
    max = 0
    for order in orders:
        if min == 0 or order['price'] < min:
            min = order['price']
        if max == 0 or order['price'] > max:
            max = order['price']
    return min, max

stop_fee = 0.0025
limit_fee = 0.001

def get_skim_amount(p0, p1, p2, a0, a1):
    if p1 < p0:
        return 0
    u = stop_fee * p1
    v = limit_fee * p2
    r0 = p2 - p0
    r1 = p2 - p1
    return a1 * (r1 - u - v) / (r0 - r1 + u)

print(get_skim_amount(100, 110, 110 * 1.0025, 1, 0.01))
print(get_skim_amount(100, 110, 110 * 1.0035, 1, 0.01))
print(get_skim_amount(100, 110, 110 * (1 + stop_fee) * (1 + limit_fee), 1, 0.01))


print(get_skim_amount(100, 110, 110 * 1.01, 1, 0.01))
print(get_skim_amount(100, 110, 110 * 1.1, 1, 0.01))
print(get_skim_amount(100, 110, 110 * 1.01, 1, 0.1))
print(get_skim_amount(100, 110, 110 * 1.1, 1, 0.1))
print(get_skim_amount(100, 110, 110 * 1.01, 1, 1))
print(get_skim_amount(100, 110, 110 * 1.1, 1, 1))

