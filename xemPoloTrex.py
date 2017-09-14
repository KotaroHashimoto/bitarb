#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Bittrex / Polo がこの数値％以上となったら Bittrex XEM売り、Polo XEM買い
SellTrex_BuyPolo_Percentage = 1

# Bittrex / Polo がこの数値％以下となったら Bittrex XEM買い、Polo XEM売り
BuyTrex_SellPolo_Percentage = -1

# 一回に取引するXEMの最大枚数
Max_Xem_Trade_Amount = 1000

# １トレード後に開ける間隔 [秒]
Mask_After_Trade_Sec = 5


# 最も安い売り板の価格 x Buy_Rate_Ratio の価格に指値買いが入る
Buy_Rate_Ratio = 2.0

# 最も高い買い板の価格 x Sell_Rate_Ratio の価格に指値売りが入る
Sell_Rate_Ratio = 0.5

# 手数料％: (価格差％ - Commission) ％だけ多くXEMを買う
Commission = 0.35


# Bittrex APIキー
Trex_Key = ''

# Bittrex シークレットキー
Trex_Secret = ''


# Poloniex APIキー
Polo_Key = ''

# Poloniex シークレットキー
Polo_Secret = ''



from datetime import datetime
from bittrex.bittrex import Bittrex
from poloniex import Poloniex
from oandapy import API
from math import floor
import sys
import json
import requests
import time
import hmac
import hashlib


class Trex:

    public = None
    private = None

    BTC = 0
    XEM = 0

    def __init__(self):
        
        Trex.public = Bittrex('', '')
        Trex.private = Bittrex(Trex_Key, Trex_Secret)

    def watch(self):

        Trex.BTC = Trex.private.get_balance('BTC')['result']['Balance']
        Trex.XEM = Trex.private.get_balance('XEM')['result']['Balance']

        res = Trex.public.get_orderbook('BTC-XEM', 'both')['result']

        self.ask = [res['sell'][0]['Rate'], res['sell'][0]['Quantity']]
        self.bid = [res['buy'][0]['Rate'], res['buy'][0]['Quantity']]

        return 'Trex: ask' + str(self.ask) + ', bid' + str(self.bid)

    def sell(self, am):
        return self.private.sell_limit('BTC-XEM', am, round(self.bid[0] * Sell_Rate_Ratio, 8))

    def buy(self, am):
        return self.private.buy_limit('BTC-XEM', am, round(self.ask[0] * Buy_Rate_Ratio, 8))


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
        Polo.BTC = float(res['BTC'])
        Polo.XEM = float(res['XEM'])

        res = Polo.public.returnOrderBook('BTC_XEM')

        self.ask = [float(res['asks'][0][0]), float(res['asks'][0][1])]
        self.bid = [float(res['bids'][0][0]), float(res['bids'][0][1])]

        return 'Polo: ask' + str(self.ask) + ', bid' + str(self.bid)

    def sell(self, am):
        return self.private.sell('BTC_XEM', round(self.bid[0] * Sell_Rate_Ratio, 8), am)

    def buy(self, am):
        return self.private.buy('BTC_XEM', round(self.ask[0] * Buy_Rate_Ratio, 8), am)


class Position:

    DIFF = 0

    def __init__(self):
        pass

    def diff(self, task, tbid, pask, pbid):

        if pask[0] < tbid[0]:
            trex = tbid[0]
            polo = pask[0]
        elif task[0] < pbid[0]:
            trex = task[0]
            polo = pbid[0]

        else:
            trex = 1
            polo = 1

        Position.DIFF = 100 * (trex / polo - 1)

#        return ' ' + str(round(zaif/2, 2)) + (' (+' if 0 < Position.DIFF else ' (') + str(round(Position.DIFF, 2)) + '%) ' + str(round(polo/2, 2)) + ' '
        return ' (+' if 0 < Position.DIFF else ' (' + str(round(Position.DIFF, 2)) + '%) '


    def operation(self, task, tbid, pask, pbid):

        if BuyTrex_SellPolo_Percentage < Position.DIFF and Position.DIFF < SellTrex_BuyPolo_Percentage:
            return (None, 0)

        elif SellTrex_BuyPolo_Percentage <= Position.DIFF:
            return ('Sell Trex', floor(min(min(Max_Xem_Trade_Amount, tbid[1]), pask[1])))

        elif Position.DIFF <= BuyTrex_SellPolo_Percentage:
            return ('Buy Trex', floor(min(min(Max_Xem_Trade_Amount, task[1]), pbid[1])))


    def checkFund(self, op, amount, task, pask):

        if 'Sell Trex' == op:
            if Trex.XEM < amount or Polo.BTC < round(amount * (100.0 + abs(Position.DIFF) - Commission) / 100.0) * pask[0]:
                return False
            else:
                return True

        elif 'Buy Trex' == op:
            if Trex.BTC < round(amount * (100.0 + abs(Position.DIFF) - Commission) / 100.0) * task[0] or Polo.XEM < amount:
                return False
            else:
                return True

        else:
            return True


if __name__ == '__main__':

    trex = Trex()
    polo = Polo()
    pos = Position()

    while(True):

        try:
            t = trex.watch()
            p = polo.watch()
            d = pos.diff(trex.ask, trex.bid, polo.ask, polo.bid)

            print(t + d + p, end = '\r')

            op, amount = pos.operation(trex.ask, trex.bid, polo.ask, polo.bid)
            if pos.checkFund(op, amount, trex.ask, polo.ask):
                if op == 'Sell Trex':
                    print('\nSell Bittrex XEM, Buy Polo, XEM: ' + str(amount)  + '\n')
                    print(polo.buy(round(amount * (100.0 + abs(Position.DIFF) - Commission) / 100.0, 4)))
                    print(trex.sell(amount))
                    time.sleep(Mask_After_Trade_Sec)

                elif op == 'Buy Trex':
                    print('\nBuy Bittrex XEM, Sell Polo, XEM: ' + str(amount)  + '\n')
                    print(trex.buy(round(amount * (100.0 + abs(Position.DIFF) - Commission) / 100.0, 3)))
                    print(polo.sell(amount))
                    time.sleep(Mask_After_Trade_Sec)

            else:
                print('\nFunds not enough.\n')
                    
            time.sleep(1.5)

        except Exception as e:
            print(e)
            time.sleep(10)

