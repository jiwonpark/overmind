from bitfinex import *

from helper import get_bf_orders_min_max_price

def exists(orders):
    return orders is not None and len(orders)

async def tester_1(bf, dm, symbol, candle_type):
    log('hey')
    # if dm is not None:
    #     log(yaml.dump(dm.candles['tLTCUSD']['5m'][-1]))
    # bf.update_tradable_balance()
    segment = dm.get_segment(symbol, candle_type)
    last = segment[-1, 2]
    now = time.time()

    if bf.pending_order_request_exists(symbol):
        return

    if symbol in bf.positions and bf.positions[symbol]['plp'] is not None:
        position = bf.positions[symbol]
        profit_ratio = position['plp'] / 100 + 1
        profit_ratio2 = last / position['price']
        # log(yaml.dump(segment[-1]))
        # log('{} {:.5f} {:.3f} {:.3f} {:.3f} {:.3f} {:.0f} {} {}'.format(symbol, position['amount'], position['price'], price, profit_ratio, profit_ratio2, now - position['time'], ft(now * 1000), ft(position['time'] * 1000)))
        position_last_update_seconds = now - position['time']
        current_candle_age_seconds = now - segment[-1, 0] / 1000
        log('{} {:.2f} ({:.5f}) | {:.2f} {:.2f} | {:.3f} | {:.0f} {:.0f}'.format(symbol, position['amount'] * position['price'], position['amount'], position['price'], last, profit_ratio2, position_last_update_seconds, current_candle_age_seconds))
        if current_candle_age_seconds < 10:
            notify_admin('{} {:.2f} ({:.5f}) | {:.2f} {:.2f} | {:.3f} | {:.0f} {:.0f}'.format(symbol, position['amount'] * position['price'], position['amount'], position['price'], last, profit_ratio2, position_last_update_seconds, current_candle_age_seconds))

        a0 = position['amount']
        p0 = position['price']
        p1 = last

        min_profit_ratio = 1.01
        min_stop_distance_ratio = 1.01

        tolerance = 1.0001

        stop_orders = None
        limit_orders = None
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        print(bf.orders)
        if symbol in bf.orders:
            stop_orders = bf.query_orders(symbol, -position['amount'], 'STOP', 0)
            limit_orders = bf.query_orders(symbol, position['amount'], 'LIMIT', 111)
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        print(stop_orders)
        if position['amount'] < 0:
            eligible_for_stop = p0 / p1 > min_profit_ratio * min_stop_distance_ratio
            if exists(stop_orders):
                min_price, max_price = get_bf_orders_min_max_price(stop_orders)
                amount, price = bf.get_order_average(symbol, position, 'STOP', False, None)
                if max_price > p0 / min_profit_ratio * tolerance:
                    print(max_price, p0 / min_profit_ratio)
                    if p0 / p1 > min_profit_ratio * min_stop_distance_ratio:
                        for order in stop_orders:
                            print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                            print(order)
                            await bf.update_order_price(order, p0 / min_profit_ratio)
                        notify_admin('Adjusted stop to be at profit ({:.2f}%) for {} position.'.format(p0 / price * 100 - 100, symbol))
                    else:
                        notify_admin('Stop is at loss ({:.2f}%) for {} position!!!'.format(p0 / price * 100 - 100, symbol))
                else:
                    # if amount < -a0 and eligible_for_stop:
                    #     a1 = amount + a0
                    #     await bf.place_stop_order(symbol, a1, p0 / min_profit_ratio, True, None)
                    if len(limit_orders) == 0:
                        a1 = -bf.mos[symbol]
                        # a1 = a0 / 2
                        p2 = (a0 * p0 + a1 * p1) / (a0 + a1)
                        if p2 / min_profit_ratio > min_price:
                            await bf.place_limit_order(symbol, a1, p1 * 1.000001, False, 111)
            else:
                if eligible_for_stop:
                    await bf.place_stop_order(symbol, -a0 / 2, p0 / min_profit_ratio, True, None)
                else:
                    notify_admin('Unprotected {} position!!!'.format(symbol))
            
            pair_acq_orders = bf.query_orders(symbol, position['amount'], 'LIMIT', 222)
            pair_liq_orders = bf.query_orders(symbol, -position['amount'], 'LIMIT', 222)
            if not exists(pair_acq_orders) and not exists(pair_liq_orders):
                # # a1 = bf.mos[symbol]
                a1 = position['amount'] / 2
                a2 = a1 * 0.02
                # p1 = last * 1.0015
                p1 = last * 1.0000001
                p2 = p1 / 1.003
                await bf.place_limit_order(symbol, a1 + a2, p1, False, 222)
                await bf.place_l

async def tester(bf, dm, symbol, candle_type):
    log('hey')
    # if dm is not None:
    #     log(yaml.dump(dm.candles['tLTCUSD']['5m'][-1]))
    # bf.update_tradable_balance()
    segment = dm.get_segment(symbol, candle_type)
    last = segment[-1, 2]
    now = time.time()

    if bf.pending_order_request_exists(symbol):
        return

    if symbol in bf.positions and bf.positions[symbol]['plp'] is not None:
        position = bf.positions[symbol]
        profit_ratio = position['plp'] / 100 + 1
        profit_ratio2 = last / position['price']
        # log(yaml.dump(segment[-1]))
        # log('{} {:.5f} {:.3f} {:.3f} {:.3f} {:.3f} {:.0f} {} {}'.format(symbol, position['amount'], position['price'], price, profit_ratio, profit_ratio2, now - position['time'], ft(now * 1000), ft(position['time'] * 1000)))
        position_last_update_seconds = now - position['time']
        current_candle_age_seconds = now - segment[-1, 0] / 1000
        log('{} {:.2f} ({:.5f}) | {:.2f} {:.2f} | {:.3f} | {:.0f} {:.0f}'.format(symbol, position['amount'] * position['price'], position['amount'], position['price'], last, profit_ratio2, position_last_update_seconds, current_candle_age_seconds))
        if current_candle_age_seconds < 10:
            notify_admin('{} {:.2f} ({:.5f}) | {:.2f} {:.2f} | {:.3f} | {:.0f} {:.0f}'.format(symbol, position['amount'] * position['price'], position['amount'], position['price'], last, profit_ratio2, position_last_update_seconds, current_candle_age_seconds))

        a0 = position['amount']
        p0 = position['price']
        p1 = last

        min_profit_ratio = 1.01
        min_stop_distance_ratio = 1.01

        tolerance = 1.0001

        stop_orders = None
        dilution_orders = None
        limit_orders = None
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        print(bf.orders)
        if symbol in bf.orders:
            stop_orders = bf.query_orders(symbol, -position['amount'], 'STOP', 0)
            # limit_orders = bf.query_orders(symbol, -position['amount'], 'LIMIT', 111)
            dilution_orders = bf.query_orders(symbol, position['amount'], 'STOP', 222)
            limit_orders = bf.query_orders(symbol, -position['amount'], 'LIMIT', 0)
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        print(limit_orders)
        if position['amount'] > 0:

            if not exists(stop_orders) and p1 / p0 > min_profit_ratio * min_stop_distance_ratio:
                await bf.place_stop_order(symbol, -a0 / 2, p0 * min_profit_ratio, True, None)
            else:
                notify_admin('Unprotected {} position!!!'.format(symbol))

            if exists(limit_orders):
                pass
                # min_price, max_price = get_bf_orders_min_max_price(stop_orders)
                # amount, price = bf.get_order_average(symbol, position, 'STOP', False, None)
                # if max_price > p0 / min_profit_ratio * tolerance:
                #     print(max_price, p0 / min_profit_ratio)
                #     if p0 / p1 > min_profit_ratio * min_stop_distance_ratio:
                #         for order in stop_orders:
                #             print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                #             print(order)
                #             await bf.update_order_price(order, p0 / min_profit_ratio)
                #         notify_admin('Adjusted stop to be at profit ({:.2f}%) for {} position.'.format(p0 / price * 100 - 100, symbol))
                #     else:
                #         notify_admin('Stop is at loss ({:.2f}%) for {} position!!!'.format(p0 / price * 100 - 100, symbol))
                # else:
                #     # if amount < -a0 and eligible_for_stop:
                #     #     a1 = amount + a0
                #     #     await bf.place_stop_order(symbol, a1, p0 / min_profit_ratio, True, None)
                #     if len(limit_orders) == 0:
                #         a1 = -bf.mos[symbol]
                #         # a1 = a0 / 2
                #         p2 = (a0 * p0 + a1 * p1) / (a0 + a1)
                #         if p2 / min_profit_ratio > min_price:
                #             await bf.place_limit_order(symbol, a1, p1 * 1.000001, False, 111)
            else:
                if p1 / p0 < min_profit_ratio:
                    mo = bf.mos[symbol]
                    await bf.place_limit_order(symbol, -mo, p0 * min_profit_ratio, True, None)
                    await bf.place_limit_order(symbol, -mo, p0 * 1.01, True, None)
                    await bf.place_limit_order(symbol, -mo, p0 * 1.02, True, None)
                    await bf.place_limit_order(symbol, -mo, p0 * 1.05, True, None)
                    await bf.place_limit_order(symbol, -mo, p0 * 1.1, True, None)
                    a1 = a0 - mo * 5
                    await bf.place_limit_order(symbol, -a1 / 3, p0 * 1.2, True, None)
                    await bf.place_limit_order(symbol, -a1 / 3, p0 * 1.3, True, None)
                    await bf.place_limit_order(symbol, -a1 / 3, p0 * 1.4, True, None)
                
            if not exists(dilution_orders):
                if bf.positions[symbol]['amount'] > 0 and last > position['price'] * 1.001:
                    await bf.lay_out_smart_buy_orders(symbol, last * 1.003, last * 1.01, 1.01, 0.3, 8)

            # pair_acq_orders = bf.query_orders(symbol, position['amount'], 'LIMIT', 222)
            # pair_liq_orders = bf.query_orders(symbol, -position['amount'], 'LIMIT', 222)
            # if not exists(pair_acq_orders) and not exists(pair_liq_orders):
            #     # # a1 = bf.mos[symbol]
            #     a1 = position['amount'] / 2
            #     a2 = a1 * 0.02
            #     # p1 = last * 1.0015
            #     p1 = last * 1.0000001
            #     p2 = p1 / 1.003
            #     await bf.place_limit_order(symbol, a1 + a2, p1, False, 222)
            #     await bf.place_limit_order(symbol, -a1, p2, False, 222)

class Config():
    pass
config = Config()
config.symbols_of_interest = ['tBTCUSD', 'tETHUSD', 'tLTCUSD', 'tDOTUSD', 'tXRPUSD', 'tUNIUSD', 'tLINKUSD', 'tEOSUSD', 'tBTGUSD', 'tSUSHIUSD', 'tADAUSD']
# config.candles_of_interest = ['1m', '15m', '1h']
config.candles_of_interest = ['5m']
config.trade_margin_ratio = 1

# await run(config, None, tester2)

from common import running_in_notebook

if not running_in_notebook():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(config, None, tester))
    loop.close()
