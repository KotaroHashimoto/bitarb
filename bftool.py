#!/usr/bin/env python3

API_KEY = ''
API_SECRET = ''


import pybitflyer
from json import loads, dump
import ssl
import requests
import os
from sys import version_info, exit, argv

if version_info.major == 2 and version_info.minor == 7:
    from urllib2 import urlopen, Request
elif version_info.major == 3 and version_info.minor == 6:
    from urllib.request import urlopen, Request
else:
    print('Please install python2.7.x or python3.6.x')
    exit(1)


api = pybitflyer.API(api_key = API_KEY, api_secret = API_SECRET)
pcode = 'FX_BTC_JPY'

def ob(p = 0, w = 10):
    res = api.board(product_code = pcode)
    z = False

    i = p + w - 1
    while p - w < i:
        if 0 <= i and i < len(res['asks']):
            sz = str(res['asks'][i]['size'])
            d = 4 - len(sz.split('.')[0])
            f = 8 - len(sz.split('.')[-1])
            j = 4 - len(str(i+1))
            print(' '*j + str(i+1) + ': ' + ' '*d + sz + ' '*f + '  ' + str(int(res['asks'][i]['price'])))

            if i == 0:
                print(' '*21 + str(int(res['mid_price'])))
                z = True
        i -= 1

    i = p + w - 1
    while p - w < i:
        if i <= 0 and abs(i) < len(res['bids']):

            if i == 0 and not z:
                print(' '*21 + str(int(res['mid_price'])))

            sz = str(res['bids'][i]['size'])
            d = 4 - len(sz.split('.')[0])
            f = 8 - len(sz.split('.')[-1])
            j = 4 - len(str(abs(i-1)))
            print(' '*j + str(abs(i-1)) + ': ' + ' '*15 + str(int(res['bids'][abs(i)]['price'])) + '  ' + ' '*d + sz + ' '*f)
        i -= 1


def tc():
    res = api.ticker(product_code = pcode)

    print('best ask : ' + str(int(res['best_ask'])) + '(' + str(res['best_ask_size']) + ')')
    print('las price: ' + str(int(res['ltp'])))
    print('best bid : ' + str(int(res['best_bid'])) + '(' + str(res['best_bid_size']) + ')')
    print('volume   : ' + str(res['volume_by_product']))


def bl():
    res = api.getbalance()

    for c in res:
        print(c['currency_code'] + ': ' + str(c['amount']))


def cl():

    res = api.getcollateral()

    print('証拠金評価額　(円): ' + str(res['collateral']))
    print('建玉評価損益　(円): ' + str(res['open_position_pnl']))
    print('建玉必要証拠金(円): ' + str(res['require_collateral']))
    print('証拠金維持率　(円): ' + str(res['keep_rate']))


def b(amount, p = 0):

    res = api.sendchildorder(product_code = pcode, \
                             child_order_type = ('MARKET' if p == 0 else 'LIMIT'), \
                             side = 'BUY', \
                             price = p, \
                             size = amount)

    if 'child_order_acceptance_id' in res:
        print('Buy order sent. ID = ' + res['child_order_acceptance_id'])
    else:
        print('Buy order failed. ' + str(res))


def s(amount, p = 0):

    res = api.sendchildorder(product_code = pcode, \
                             child_order_type = ('MARKET' if p == 0 else 'LIMIT'), \
                             side = 'SELL', \
                             price = p, \
                             size = amount)

    if 'child_order_acceptance_id' in res:
        print('Sell order sent. ID = ' + res['child_order_acceptance_id'])
    else:
        print('Sell order failed. ' + str(res))


def oo():

    res = api.getchildorders(product_code = pcode, child_order_state = 'ACTIVE')

    i = 1
    for c in res:
        print((' ' if i < 10 else '') + str(i) + ': ' + c['side'] + ' ' + c['child_order_type'] + ', size = ' + str(c['size']) + ', price = ' + str(c['price']))
        i += 1

    if not res:
        print('No open order')


def cc(i):

    res = api.getchildorders(product_code = pcode, child_order_state = 'ACTIVE')
    o = 1
    for c in res:
        if o == i:
            res = api.cancelchildorder(product_code = pcode, child_order_id = c['child_order_id'])
            print('Cancelled: ' + c['side'] + ' ' + c['child_order_type'] + ', size = ' + str(c['size']) + ', price = ' + str(c['price']))
            return

        o += 1

    print('No open order cancelled.')


def ca():

    res = api.cancelallchildorders(product_code = pcode)
    print(res)


def ps():

    res = api.getpositions(product_code = pcode)

    for c in res:
        print(c['side'] + ', size = ' + str(c['size']) + ', price = ' + str(c['price']) + ', pnl = ' + ('+' if 0 < c['pnl'] else '') + str(c['pnl']) + ', swap = ' + str(c['swap_point_accumulate']))

    if not res:
        print('No position')


def hl():

    res = api.gethealth(product_code = pcode)
    print('BitFlyer server status is', res['status'])



if __name__ == '__main__':

    argv[2:] = [float(v) if '.' in v else int(v) for v in argv[2:]]

    if argv[1] == 'ob':
        ob(*tuple(argv[2:]))
    elif argv[1] == 'tc':
        tc()
    elif argv[1] == 'bl':
        bl()
    elif argv[1] == 'cl':
        cl()
    elif argv[1] == 'b':
        b(*tuple(argv[2:]))
    elif argv[1] == 's':
        s(*tuple(argv[2:]))
    elif argv[1] == 'oo':
        oo()
    elif argv[1] == 'cc':
        cc(*tuple(argv[2:]))
    elif argv[1] == 'ca':
        ca()
    elif argv[1] == 'ps':
        ps()
    elif argv[1] == 'hl':
        hl()
    else:
        print('command', argv[1], 'doesn\'t exist.')
