#!/usr/bin/env python


from urllib.request import urlopen
from json import load
from datetime import datetime
from threading import Thread
from time import sleep
import oandapy

from tkinter import *


class Window(Thread):

    PERIOD = 0.5

    def __init__(self, title):
        Thread.__init__(self)
    
        self.root = Tk()
        self.root.title(title)

        self.str = StringVar()
        self.str.set('')
        self.label = Label(self.root, textvariable = self.str)
        self.label.pack()

        Label(text = 'Exchange' + (' '*8) + '\tLast\tAsk\tBid').pack()

    def run(self):
    
        while True:
            self.str.set(datetime.now().strftime('%Y/%m/%d  %H:%M:%S'))
            sleep(Window.PERIOD)


class OANDA(Thread):

    PRICE = {'USD_JPY':0, 'EUR_JPY':0, 'GBP_JPY':0}
    
    def __init__(self, root, symbol):
        Thread.__init__(self)
        
        if symbol == 'USD_JPY':
            Label(root).pack()

        self.lstr = StringVar()
        self.lstr.set('')
        self.label = Label(root, textvariable = self.lstr)
        self.label.pack()
        self.symbol = symbol

        self.oanda = oandapy.API(environment='practice', access_token='f80296b600eddebbb0402eeabce34139-55d481314b19c1127978ecd05c9dca65')

    def run(self):

        while True:
            prices = self.oanda.get_prices(instruments = self.symbol).get('prices')
            
            up = (prices[0].get('ask') + prices[0].get('bid')) / 2.0
            self.label.configure(fg = ('green' if OANDA.PRICE[self.symbol] < up else ('red' if OANDA.PRICE[self.symbol] > up else 'black')))
            OANDA.PRICE[self.symbol] = up
            ask = str(int(1000 * prices[0].get('ask')))
            bid = str(int(1000 * prices[0].get('bid')))
            self.lstr.set(self.symbol.replace('_', '/') + '\t\t\t' + ask[:3] + '.' + ask[3:] + '\t' + bid[:3] + '.' + bid[3:])


class Exchange(Thread):

    def __init__(self, root, name, url, last, sask, sbid):
        Thread.__init__(self)
    
        self.name = name
        self.url = url
        self.last = last
        self.sask = sask
        self.sbid = sbid

        self.str = StringVar()
        self.str.set('')
        self.label = Label(root, textvariable = self.str)
        self.label.pack()

        self.ask = 0
        self.bid = 0
        self.p = 0

    def run(self):

        while True:
            data = load(urlopen(self.url))

            self.ask = int(data[self.sask])
            self.bid = int(data[self.sbid])
        
            up = int(data[self.last])
            self.label.configure(fg = ('green' if self.p < up else ('red' if self.p > up else 'black')))
            self.p = up
        
            a = str(self.ask)
            b = str(self.bid)
            l = str(self.p)
    
            self.str.set(self.name + (' ' * (20 - len(self.name))) + '\t' + l[:3] + ',' + l[3:] + '\t' +  a[:3] + ',' + a[3:] + '\t' +  b[:3] + ',' + b[3:])
            sleep(Window.PERIOD)


class USDExchange(Exchange):

    def __init__(self, root, name, url, last, sask, sbid):    
        Exchange.__init__(self, root, name, url, last, sask, sbid)

    def run(self):
    
        while True:
            data = load(urlopen(self.url))

            if self.name == 'BTC-e':
                data = data['btc_usd']

            self.ask = float(data[self.sask]) * OANDA.PRICE['USD_JPY']
            self.bid = float(data[self.sbid]) * OANDA.PRICE['USD_JPY']
        
            up = float(data[self.last]) * OANDA.PRICE['USD_JPY']
            self.label.configure(fg = ('green' if self.p < up else ('red' if self.p > up else 'black')))
            self.p = up

            a = str(int(round(self.ask)))
            b = str(int(round(self.bid)))
            l = str(int(round(self.p)))

            self.str.set(self.name + (' ' * (20 - len(self.name))) + '\t' + l[:3] + ',' + l[3:] + '\t' +  a[:3] + ',' + a[3:] + '\t' +  b[:3] + ',' + b[3:])
            sleep(Window.PERIOD)


if __name__ == '__main__':

    window = Window('BTC/JPY Live Price')

    exchangeList = ( \
        window, \
        Exchange(window.root, 'bitFlyerFX', 'https://api.bitflyer.jp/v1/getticker?product_code=FX_BTC_JPY', 'ltp', 'best_ask', 'best_bid'), \
        Exchange(window.root, 'bitFlyer', 'https://api.bitflyer.jp/v1/getticker?product_code=BTC_JPY', 'ltp', 'best_ask', 'best_bid'), \
        Exchange(window.root, 'BtcBox', 'https://www.btcbox.co.jp/api/v1/ticker/', 'last', 'buy', 'sell'), \
        Exchange(window.root, 'Zaif', 'https://api.zaif.jp/api/1/ticker/btc_jpy', 'last', 'ask', 'bid'), \
        Exchange(window.root, 'coincheck', 'https://coincheck.com/api/ticker', 'last', 'ask', 'bid'), \
        #Exchange(window.root, 'Quoine', 'https://api.quoine.com/products/5', 'last_traded_proce', 'market_ask', 'market_bid'), \
        USDExchange(window.root, 'Bitstamp', 'https://www.bitstamp.net/api/v2/ticker/btcusd/', 'last', 'ask', 'bid'), \
        USDExchange(window.root, 'BTC-e', 'https://btc-e.com/api/3/ticker/btc_usd', 'last', 'buy', 'sell'), \
        OANDA(window.root, 'USD_JPY'), \
        OANDA(window.root, 'EUR_JPY'), \
        OANDA(window.root, 'GBP_JPY'), \
    )

    for e in exchangeList:
        e.setDaemon(True)
        e.start()

    window.root.mainloop()
