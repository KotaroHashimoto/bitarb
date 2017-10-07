#!/usr/bin/env python3

API_KEY = ''
API_SECRET = ''


# 売買するBTC量
Trade_Amount = 1.001

# 価格監視間隔 [秒]
Monitor_Cycle_Sec = 10

# Ask + Order_Diff_Sell に売りが入る
Order_Diff_Sell = 8000

# Bid - Order_Diff_Buy に買いが入る
Order_Diff_Buy = 8000

# 監視タイミングで Bid が Mod_Diff_Bid より上がっていたら指値し直し
Mod_Diff_Bid = 2000

# 監視タイミングで Ask が Mod_Diff_Ask より下がっていたら指値し直し
Mod_Diff_Ask = 2000

# 利確幅
Close_Diff = 3000


import pybitflyer
from json import loads, dump
import ssl
import requests
import os
from time import sleep
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


def tc():
    res = api.ticker(product_code = pcode)
    return (int(res['best_bid']), int(res['best_ask']))


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
    return [c for c in res if (c['size'] * 1000) % 10 == 1]


def ca():

   res = api.getchildorders(product_code = pcode, child_order_state = 'ACTIVE')
   for o in [c for c in res if (c['size'] * 1000) % 10 == 1]:
       res = api.cancelchildorder(product_code = pcode, child_order_id = o['child_order_id'])


def ps():

    res = api.getpositions(product_code = pcode)
    return [c for c in res if (c['size'] * 1000) % 10 == 1]


def hl():

    res = api.gethealth(product_code = pcode)
    return res['status']



if __name__ == '__main__':

    lastBid = 0
    lastAsk = 0

    while True:
        
        bid, ask = tc()
        openOrders = oo()
        positions = ps()

        print('bid = ' + str(bid) + ', ask = ' + str(ask) + ', pos = ' + str(len(positions)) + ', openOrders = ' + str(len(openOrders)))

        if (not openOrders) and (not positions):
            s(Trade_Amount, ask + Order_Diff_Sell)
            b(Trade_Amount, bid - Order_Diff_Buy)

            while len(openOrders) < 2:
                sleep(1)
                openOrders = oo()


        elif (not positions) and (len(openOrders) == 2):
            if lastBid + Mod_Diff_Bid < bid or ask < lastAsk - Mod_Diff_Ask:
                
                while openOrders:
                    ca()
                    openOrders = oo()

                continue
                    
        elif (len(positions) == 1) and (len(openOrders) == 1):
            if positions[0]['side'] == openOrders[0]['side']:
            
                while openOrders:
                    ca()
                    openOrders = oo()
            
                if positions[0]['side'] == 'SELL':
                    b(positions[0]['size'], positions[0]['price'] - Close_Diff)

                elif positions[0]['side'] == 'BUY':
                    s(positions[0]['size'], positions[0]['price'] + Close_Diff)

                while len(openOrders) < 1:
                    sleep(1)
                    openOrders = oo()


        elif (not positions) and (len(openOrders) == 1):
            while openOrders:
                ca()
                openOrders = oo()

            continue
                
        lastBid = bid
        lastAsk = ask
        sleep(Monitor_Cycle_Sec)
