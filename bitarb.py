#!/usr/bin/env python


from urllib.request import urlopen
from json import load
from datetime import datetime
import oandapy

from tkinter import *


class Window:

    def __init__(self, title):
        self.root = Tk()
        self.root.title(title)

        self.str = StringVar()
        self.str.set('')
        self.label = Label(self.root, textvariable = self.str)
        self.label.pack()

        Label(text = 'Exchange' + (' '*8) + '\tLast\tAsk\tBid').pack()

    def update(self):
        self.str.set('Last Update:  ' + datetime.now().strftime('%Y/%m/%d %H:%M:%S'))


class OANDA:

    PRICE = {'USD_JPY':0, 'EUR_JPY':0, 'GBP_JPY':0}
    
    def __init__(self, root):

        self.label = Label(root, text = '')
        self.label.pack()

        self.usdjpy = StringVar()
        self.usdjpy.set('')
        Label(root, textvariable = self.usdjpy).pack()

        self.eurjpy = StringVar()
        self.eurjpy.set('')
        Label(root, textvariable = self.eurjpy).pack()

        self.gbpjpy = StringVar()
        self.gbpjpy.set('')
        Label(root, textvariable = self.gbpjpy).pack()

        self.oanda = oandapy.API(environment='practice', access_token='f80296b600eddebbb0402eeabce34139-55d481314b19c1127978ecd05c9dca65')

    def update(self, lstr, symbol):

        prices = self.oanda.get_prices(instruments = symbol).get('prices')
        OANDA.PRICE[symbol] = (prices[0].get('ask') + prices[0].get('bid')) / 2.0
        ask = str(int(1000 * prices[0].get('ask')))
        bid = str(int(1000 * prices[0].get('bid')))
        lstr.set(symbol.replace('_', '') + '\t\t\t' + ask[:3] + '.' + ask[3:] + '\t' + bid[:3] + '.' + bid[3:])

    def getPrice(self):

        self.update(self.usdjpy, 'USD_JPY')
        self.update(self.eurjpy, 'EUR_JPY')
        self.update(self.gbpjpy, 'GBP_JPY')


class Exchange:

    def __init__(self, root, name, url, last, sask, sbid):
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

    def getPrice(self):

        data = load(urlopen(self.url))

        self.ask = int(data[self.sask])
        self.bid = int(data[self.sbid])
        
        up = int(data[self.last])
#        self.label.configure(fg = ('green' if self.p < up else 'red'))
        self.p = up
        
        a = str(self.ask)
        b = str(self.bid)
        l = str(self.p)
    
        self.str.set(self.name + (' ' * (20 - len(self.name))) + '\t' + l[:3] + ',' + l[3:] + '\t' +  a[:3] + ',' + a[3:] + '\t' +  b[:3] + ',' + b[3:])


class USDExchange(Exchange):

    def __init__(self, root, name, url, last, sask, sbid):    
        Exchange.__init__(self, root, name, url, last, sask, sbid)

    def getPrice(self):
    
        data = load(urlopen(self.url))

        if self.name == 'BTC-e':
            data = data['btc_usd']

        self.ask = float(data[self.sask]) * OANDA.PRICE['USD_JPY']
        self.bid = float(data[self.sbid]) * OANDA.PRICE['USD_JPY']
        
        up = float(data[self.last]) * OANDA.PRICE['USD_JPY']
#        self.label.configure(fg = ('green' if self.p < up else 'red'))
        self.p = up

        a = str(int(round(self.ask)))
        b = str(int(round(self.bid)))
        l = str(int(round(self.p)))

        self.str.set(self.name + (' ' * (20 - len(self.name))) + '\t' + l[:3] + ',' + l[3:] + '\t' +  a[:3] + ',' + a[3:] + '\t' +  b[:3] + ',' + b[3:])


window = Window('BTC/JPY Live Price')

exchangeList = [ \
Exchange(window.root, 'bitFlyerFX', 'https://api.bitflyer.jp/v1/getticker?product_code=FX_BTC_JPY', 'ltp', 'best_ask', 'best_bid'), \
Exchange(window.root, 'bitFlyer', 'https://api.bitflyer.jp/v1/getticker?product_code=BTC_JPY', 'ltp', 'best_ask', 'best_bid'), \
Exchange(window.root, 'BtcBox', 'https://www.btcbox.co.jp/api/v1/ticker/', 'last', 'buy', 'sell'), \
Exchange(window.root, 'Zaif', 'https://api.zaif.jp/api/1/ticker/btc_jpy', 'last', 'ask', 'bid'), \
Exchange(window.root, 'coincheck', 'https://coincheck.com/api/ticker', 'last', 'ask', 'bid'), \
#Exchange(window.root, 'Quoine', 'https://api.quoine.com/products/5', 'last_traded_proce', 'market_ask', 'market_bid'), \
USDExchange(window.root, 'Bitstamp', 'https://www.bitstamp.net/api/v2/ticker/btcusd/', 'last', 'ask', 'bid'), \
USDExchange(window.root, 'BTC-e', 'https://btc-e.com/api/3/ticker/btc_usd', 'last', 'buy', 'sell'), \
OANDA(window.root), \
]
exchangeList.reverse()
exchangeList = tuple(exchangeList)

def updatePrice():

    for e in exchangeList:
        e.getPrice()

    window.update()    
    window.root.after(5000, updatePrice)

updatePrice()
window.root.mainloop()
