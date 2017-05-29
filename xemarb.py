#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Zaif / Polo がこの数値％以上となったら Zaif XEM売り、Polo XEM買い
SellZaif_BuyPolo_Percentage = 5

# Zaif / Polo がこの数値％以下となったら Zaif XEM買い、Polo XEM売り
BuyZaif_SellPolo_Percentage = -5


# Zaif APIキー
Zaif_Key = ''

# Zaif シークレットキー
Zaif_Secret = ''


# Poloniex APIキー
Polo_Key = ''

# Poloniex シークレットキー
Polo_Secret = ''



from datetime import datetime
from zaifapi.impl import ZaifPublicApi, ZaifTradeApi
from poloniex import Poloniex
from oandapy import API
from math import floor
import sys
import json
import requests
import time
import hmac
import hashlib


class Zaif:

    private = None
    public = None

    BTCJPY = 1
    JPY = 0
    XEM = 0

    def __init__(self):
        
        Zaif.private = ZaifTradeApi(Zaif_Key, Zaif_Secret)
        Zaif.public = ZaifPublicApi()

    def watch(self):

        res = Zaif.private.get_info2()['funds']
        Zaif.JPY = res['jpy']
        Zaif.XEM = res['xem']

        Zaif.BTCJPY = Zaif.public.last_price('btc_jpy')['last_price']

        res = Zaif.public.depth('xem_jpy')

        self.ask = res['asks'][0]
        self.bid = res['bids'][0]

        return 'Zaif: ask' + str(self.ask) + ', bid' + str(self.bid)

    def sell(self, am):
        return self.private.trade(currency_pair = 'xem_jpy', action = 'bid', price = self.bid[0], amount = am)

    def buy(self, am):
        return self.private.trade(currency_pair = 'xem_jpy', action = 'ask', price = self.ask[0], amount = am)


class Polo:

    public = None
    private = None

    BTC = 0
    XEM = 0

    def __init__(self):
        
        Polo.public = Poloniex()
        Polo.private = Poloniex(Polo_Key, Polo_Secret)

    def watch(self):

        res = Polo.private.returnBalances()
        Polo.BTC = res['BTC']
        Polo.XEM = res['XEM']

        res = Polo.public.returnOrderBook('BTC_XEM')

        self.ask = [float(res['asks'][0][0]), float(res['asks'][0][1])]
        self.bid = [float(res['bids'][0][0]), float(res['bids'][0][1])]

        return 'Polo: ask' + str(self.ask) + ', bid' + str(self.bid)

    def sell(self, am):
        return self.private.sell('BTC_XEM', self.bid[0], am)

    def buy(self, am):
        return self.private.buy('BTC_XEM', self.ask[0], am)


class Position:

    DIFF = 0

    def __init__(self):
        pass

    def diff(self, zask, zbid, pask, pbid):

        zaif = zask[0] + zbid[0]
        polo = Zaif.BTCJPY * (pask[0] + pbid[0])

        Position.DIFF = 100 * (zaif / polo - 1)

        return ' ' + str(round(zaif/2, 2)) + (' (+' if 0 < Position.DIFF else ' (') + str(round(Position.DIFF, 2)) + '%) ' + str(round(polo/2, 2)) + ' '


    def operation(self, zask, zbid, pask, pbid):

        if BuyZaif_SellPolo_Percentage < Position.DIFF and Position.DIFF < SellZaif_BuyPolo_Percentage:
            return (None, 0)

        elif SellZaif_BuyPolo_Percentage <= Position.DIFF:
            return ('Sell Zaif', floor(min(zbid[1], pask[1])))

        elif Position.DIFF <= BuyZaif_SellPolo_Percentage:
            return ('Buy Zaif', floor(min(zask[1], pbid[1])))


    def checkFund(self, op, amount, zask, pask):

        if 'Sell Zaif' == op:
            if Zaif.XEM < amount or Polo.BTC < amount * pask[0]:
                return False
            else:
                return True

        elif 'Buy Zaif' == op:
            if Zaif.JPY < amount * zask[0] or Polo.XEM < amount:
                return False
            else:
                return True

        else:
            return True


if __name__ == '__main__':

    zaif = Zaif()
    polo = Polo()
    pos = Position()

    while(True):

        try:
            z = zaif.watch()
            p = polo.watch()
            d = pos.diff(zaif.ask, zaif.bid, polo.ask, polo.bid)

            print(z + d + p, end = '\r')

            op, amount = pos.operation(zaif.ask, zaif.bid, polo.ask, polo.bid)
            if pos.checkFund(op, amount, zaif.ask, polo.ask) or True:
                if op == 'Sell Zaif':
                    print('\nSell Zaif XEM, Buy Polo, XEM: ' + str(amount)  + '\n')
                    print(zaif.sell(amount))
                    print(polo.buy(amount))

                elif op == 'Buy Zaif':
                    print('\nBuy Zaif XEM, Sell Polo, XEM: ' + str(amount)  + '\n')
                    print(zaif.buy(amount))
                    print(polo.sell(amount))

            else:
                print('\nFunds not enough.\n')
                    
            time.sleep(1)

        except Exception as e:
            print(e)
            time.sleep(10)

