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
