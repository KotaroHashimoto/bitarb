#!/usr/bin/env python3

from json import load
from datetime import datetime
from threading import Thread
from time import sleep
from oandapy import API
import ssl
from sys import version_info, exit

if version_info.major == 2 and version_info.minor == 7:
    from urllib2 import urlopen, Request
    from Tkinter import *
elif version_info.major == 3 and version_info.minor == 6:
    from urllib.request import urlopen, Request
    from tkinter import *
else:
    print('Please install python2.7.x or python3.6.x')
    exit(1)


class Window(Thread):

    PERIOD = 0.5
    FONT = 'Arial'
    FSIZE = 12

    def __init__(self, title):
        Thread.__init__(self)
    
        self.root = Tk()
        self.root.title(title)

        self.str = StringVar()
        self.str.set('')
        self.label = Label(self.root, textvariable = self.str, font = (Window.FONT, Window.FSIZE))
        self.label.pack()

        Label(text = 'Exchange' + (' '*8) + '\tLast\tAsk\tBid', font = (Window.FONT, Window.FSIZE)).pack()
        
        self.root.bind('<MouseWheel>', self.onMouseWheel)

    def run(self):
    
        while True:
            self.str.set(datetime.now().strftime('%Y/%m/%d  %H:%M:%S'))
            sleep(Window.PERIOD)

    def onMouseWheel(self, mouseEvent):
    
        Window.FSIZE = Window.FSIZE + (1 if 0 < mouseEvent.delta else -1)
    
        for widget in self.root.children.values():
            widget.configure(font = (Window.FONT, Window.FSIZE))


class OANDA(Thread):

    PRICE = {'USD_JPY':0, 'EUR_JPY':0, 'GBP_JPY':0, 'CNY_JPY':0, 'USD_CNY':0}
    
    def __init__(self, root, symbol):
        Thread.__init__(self)
        
        if symbol == 'USD_JPY':
            Label(root).pack()

        self.lstr = StringVar()
        self.lstr.set('')
        self.label = Label(root, textvariable = self.lstr, font = (Window.FONT, Window.FSIZE))
        self.label.pack()
        self.symbol = symbol

        self.oanda = API(environment='practice', access_token='f80296b600eddebbb0402eeabce34139-55d481314b19c1127978ecd05c9dca65')

    def run(self):

        while True:
            prices = self.oanda.get_prices(instruments = self.symbol).get('prices')
            
            up = (prices[0].get('ask') + prices[0].get('bid')) / 2.0
            self.label.configure(fg = ('green' if OANDA.PRICE[self.symbol] < up else ('red' if OANDA.PRICE[self.symbol] > up else 'black')))
            OANDA.PRICE[self.symbol] = up
            
            if 'CNY_JPY' == self.symbol:
                ask = str(int(1000 * prices[0].get('ask')))
                bid = str(int(1000 * prices[0].get('bid')))
                self.lstr.set(self.symbol.replace('_', '/') + ':  \t\t ' + ask[:2] + '.' + ask[2:] + '\t ' + bid[:2] + '.' + bid[2:])
            elif 'USD_CNY' == self.symbol:
                ask = str(int(10000 * prices[0].get('ask')))
                bid = str(int(10000 * prices[0].get('bid')))
                self.lstr.set(self.symbol.replace('_', '/') + ':  \t\t ' + ask[:1] + '.' + ask[1:] + '\t ' + bid[:1] + '.' + bid[1:])
            else:
                ask = str(int(1000 * prices[0].get('ask')))
                bid = str(int(1000 * prices[0].get('bid')))
                self.lstr.set(self.symbol.replace('_', '/') + ':  \t\t' + ask[:3] + '.' + ask[3:] + '\t' + bid[:3] + '.' + bid[3:])


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
        self.label = Label(root, textvariable = self.str, font = (Window.FONT, Window.FSIZE))
        self.label.pack()

        self.ask = 0
        self.bid = 0
        self.p = 0

    def run(self):

        while True:
            data = load(urlopen(Request(self.url, headers = {'User-Agent':'Hoge Browser'})))

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
            data = load(urlopen(Request(self.url, headers = {'User-Agent':'Hoge Browser'})))

            if self.name == 'BTC-e':
                data = data['btc_usd']
            elif self.name == 'Poloniex':
                data = data['USDT_BTC']

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

    ssl._create_default_https_context = ssl._create_unverified_context

    window = Window('BTC/JPY Live Price')

    exchangeList = ( \
        window, \
        Exchange(window.root, 'bitFlyerFX', 'https://api.bitflyer.jp/v1/getticker?product_code=FX_BTC_JPY', 'ltp', 'best_ask', 'best_bid'), \
        Exchange(window.root, 'bitFlyer', 'https://api.bitflyer.jp/v1/getticker?product_code=BTC_JPY', 'ltp', 'best_ask', 'best_bid'), \
        Exchange(window.root, 'BtcBox', 'https://www.btcbox.co.jp/api/v1/ticker/', 'last', 'buy', 'sell'), \
        Exchange(window.root, 'Zaif', 'https://api.zaif.jp/api/1/ticker/btc_jpy', 'last', 'ask', 'bid'), \
        Exchange(window.root, 'coincheck', 'https://coincheck.com/api/ticker', 'last', 'ask', 'bid'), \
        Exchange(window.root, 'Quoine', 'https://api.quoine.com/products/5', 'last_traded_price', 'market_ask', 'market_bid'), \
        USDExchange(window.root, 'Poloniex', 'https://poloniex.com/public?command=returnTicker', 'last', 'lowestAsk', 'highestBid'), \
        USDExchange(window.root, 'Bitstamp', 'https://www.bitstamp.net/api/v2/ticker/btcusd/', 'last', 'ask', 'bid'), \
        USDExchange(window.root, 'Bitfinex', 'https://api.bitfinex.com/v1/pubticker/BTCUSD', 'last_price', 'ask', 'bid'), \
        USDExchange(window.root, 'BTC-e', 'https://btc-e.com/api/3/ticker/btc_usd', 'last', 'buy', 'sell'), \
        OANDA(window.root, 'USD_JPY'), \
        OANDA(window.root, 'EUR_JPY'), \
        OANDA(window.root, 'GBP_JPY'), \
        OANDA(window.root, 'CNY_JPY'), \
        OANDA(window.root, 'USD_CNY'), \
    )

    for e in exchangeList:
        e.setDaemon(True)
        e.start()

    window.root.mainloop()
