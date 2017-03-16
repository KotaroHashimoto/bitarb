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
        self.root.bind('<Up>', self.expand)
        self.root.bind('<Right>', self.expand)
        self.root.bind('<Down>', self.shrink)
        self.root.bind('<Left>', self.shrink)

    def run(self):
    
        while True:
            self.str.set(datetime.now().strftime('%Y/%m/%d  %H:%M:%S'))
            sleep(Window.PERIOD)

    def update(self, delta):
    
        Window.FSIZE = Window.FSIZE + delta
    
        for widget in self.root.children.values():
            widget.configure(font = (Window.FONT, Window.FSIZE))

    def onMouseWheel(self, mouseEvent):
        self.update(1 if 0 < mouseEvent.delta else -1)

    def expand(self, keyEvent):
        self.update(1)

    def shrink(self, keyEvent):
        self.update(-1)


class OANDA(Thread):

    PRICE = {'USD_JPY':1, 'EUR_JPY':1, 'GBP_JPY':1, 'CNY_JPY':1, 'USD_CNY':1}
    
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
            self.label.configure(fg = ('black' if OANDA.PRICE[self.symbol] == up else ('red' if OANDA.PRICE[self.symbol] > up else 'green')))
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
            self.label.configure(fg = ('black' if self.p == up else ('red' if self.p > up else 'green')))
            self.p = up
        
            a = str(self.ask)
            b = str(self.bid)
            l = str(self.p)
    
            self.str.set(self.name + (' ' * (20 - len(self.name))) + '\t' + l[:3] + ',' + l[3:] + '\t' +  a[:3] + ',' + a[3:] + '\t' +  b[:3] + ',' + b[3:])
            sleep(Window.PERIOD)


class ForExchange(Exchange):

    def __init__(self, root, name, url, last, sask, sbid):    
        Exchange.__init__(self, root, name, url, last, sask, sbid)
        
        if 'Houbi' == self.name or 'BTCC' == self.name or 'OKCoinCN' == self.name:
            self.base = 'CNY_JPY'
        else:
            self.base = 'USD_JPY'

    def run(self):
    
        while True:
            data = load(urlopen(Request(self.url, headers = {'User-Agent':'Hoge Browser'})))

            if self.name == 'BTC-e':
                data = data['btc_usd']
            elif self.name == 'Poloniex':
                data = data['USDT_BTC']
            elif 'OKCoin' in self.name or 'Houbi' == self.name or 'BTCC' == self.name :
                data = data['ticker']

            self.ask = float(data[self.sask]) * OANDA.PRICE[self.base]
            self.bid = float(data[self.sbid]) * OANDA.PRICE[self.base]
            up = float(data[self.last]) * OANDA.PRICE[self.base]

            self.label.configure(fg = ('black' if self.p == up else ('red' if self.p > up else 'green')))
            self.p = up

            a = str(int(round(self.ask)))
            b = str(int(round(self.bid)))
            l = str(int(round(self.p)))

            self.str.set(self.name + (' ' * (20 - len(self.name))) + '\t' + l[:3] + ',' + l[3:] + '\t' +  a[:3] + ',' + a[3:] + '\t' +  b[:3] + ',' + b[3:])
            sleep(Window.PERIOD)


class EthereumExchange(ForExchange):

    def __init__(self, root, name, url, last, sask, sbid):    

        if name == 'Bitfinex ETH':
            Label(root).pack()

        ForExchange.__init__(self, root, name, url, last, sask, sbid)

    def run(self):
    
        while True:
            data = load(urlopen(Request(self.url, headers = {'User-Agent':'Hoge Browser'})))

            if self.name == 'BTC-e ETH':
                data = data['eth_usd']

            self.ask = float(data[self.sask]) * OANDA.PRICE[self.base]
            self.bid = float(data[self.sbid]) * OANDA.PRICE[self.base]
            up = float(data[self.last]) * OANDA.PRICE[self.base]

            self.label.configure(fg = ('green' if self.p < up else ('red' if self.p > up else 'black')))
            self.p = up

            a = str(int(10.0 * self.ask))
            b = str(int(10.0 * self.bid))
            l = str(int(10.0 * self.p))

            self.str.set(self.name + (' ' * (20 - len(self.name))) + '\t' + l[:4] + '.' + l[4:] + '\t' +  a[:4] + '.' + a[4:] + '\t' +  b[:4] + '.' + b[4:])
            sleep(Window.PERIOD)


if __name__ == '__main__':

    ssl._create_default_https_context = ssl._create_unverified_context

    window = Window('BTC/JPY Live Price')

    exchangeList = tuple([ \
        window, \
        Exchange(window.root, 'bitFlyerFX', 'https://api.bitflyer.jp/v1/getticker?product_code=FX_BTC_JPY', 'ltp', 'best_ask', 'best_bid'), \
        Exchange(window.root, 'bitFlyer', 'https://api.bitflyer.jp/v1/getticker?product_code=BTC_JPY', 'ltp', 'best_ask', 'best_bid'), \
        Exchange(window.root, 'BtcBox', 'https://www.btcbox.co.jp/api/v1/ticker/', 'last', 'sell', 'buy'), \
        Exchange(window.root, 'Zaif', 'https://api.zaif.jp/api/1/ticker/btc_jpy', 'last', 'ask', 'bid'), \
        Exchange(window.root, 'coincheck', 'https://coincheck.com/api/ticker', 'last', 'ask', 'bid'), \
        Exchange(window.root, 'Quoine', 'https://api.quoine.com/products/5', 'last_traded_price', 'market_ask', 'market_bid'), \
        ForExchange(window.root, 'Poloniex', 'https://poloniex.com/public?command=returnTicker', 'last', 'lowestAsk', 'highestBid'), \
        ForExchange(window.root, 'Bitstamp', 'https://www.bitstamp.net/api/v2/ticker/btcusd/', 'last', 'ask', 'bid'), \
        ForExchange(window.root, 'Bitfinex', 'https://api.bitfinex.com/v1/pubticker/BTCUSD', 'last_price', 'ask', 'bid'), \
        ForExchange(window.root, 'BTC-e', 'https://btc-e.com/api/3/ticker/btc_usd', 'last', 'buy', 'sell'), \
        ForExchange(window.root, 'Houbi', 'http://api.huobi.com/staticmarket/ticker_btc_json.js', 'last', 'sell', 'buy'), \
        ForExchange(window.root, 'BTCC', 'https://pro-data.btcc.com/data/pro/ticker?symbol=XBTCNY', 'Last', 'AskPrice', 'BidPrice'), \
        ForExchange(window.root, 'OKCoinCN', 'https://www.okcoin.cn/api/v1/ticker.do?symbol=btc_usd', 'last', 'sell', 'buy'), \
        ForExchange(window.root, 'OKCoinCOM', 'https://www.okcoin.com/api/v1/ticker.do?symbol=btc_usd', 'last', 'sell', 'buy'), \
        ForExchange(window.root, 'OKCoin week', 'https://www.okcoin.com/api/v1/future_ticker.do?symbol=btc_usd&contract_type=this_week', 'last', 'sell', 'buy'), \
#        ForExchange(window.root, 'OKCoin next wk', 'https://www.okcoin.com/api/v1/future_ticker.do?symbol=btc_usd&contract_type=next_week', 'last', 'sell', 'buy'), \
        ForExchange(window.root, 'OKCoin quarter', 'https://www.okcoin.com/api/v1/future_ticker.do?symbol=btc_usd&contract_type=quarter', 'last', 'sell', 'buy'), \
        EthereumExchange(window.root, 'Bitfinex ETH', 'https://api.bitfinex.com/v1/pubticker/ETHUSD', 'last_price', 'ask', 'bid'), \
        EthereumExchange(window.root, 'BTC-e ETH', 'https://btc-e.com/api/3/ticker/eth_usd', 'last', 'buy', 'sell'), \
        ] + \
        [OANDA(window.root, currencyPair) for currencyPair in OANDA.PRICE.keys()], \
    )

    for e in exchangeList:
        e.setDaemon(True)
        e.start()

    window.root.mainloop()
