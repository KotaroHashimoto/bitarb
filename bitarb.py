#!/usr/bin/env python

from urllib import urlopen
from json import load
from datetime import datetime
import oandapy

from  Tkinter import *


class Window:

    def __init__(self, title):
        self.root = Tk()
        self.root.title(title)
#        root.geometry('400x300')

#        self.editbox = Entry(width = 3)
#        self.editbox.insert(END, '1')
#        self.editbox.pack()

        self.str = StringVar()
        self.str.set('')
        self.label = Label(self.root, textvariable = self.str)
        self.label.pack()

        Label(text = 'Exchange' + (' '*8) + '\tLast\tAsk\tBid').pack()

    def update(self):
        self.str.set('Last Update:  ' + datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
        

class OANDA:

    usdjpy = 0
    eurjpy = 0
    
    def __init__(self, root):

        self.label = Label(root, text = '')
        self.label.pack()

        self.usdjpy = StringVar()
        self.usdjpy.set('')
        self.label = Label(root, textvariable = self.usdjpy)
        self.label.pack()

        self.eurjpy = StringVar()
        self.eurjpy.set('')
        self.label = Label(root, textvariable = self.eurjpy)
        self.label.pack()

        self.oanda = oandapy.API(environment='practice', access_token='f80296b600eddebbb0402eeabce34139-55d481314b19c1127978ecd05c9dca65')

    def getPrice(self):

        prices = self.oanda.get_prices(instruments='USD_JPY').get('prices')
        OANDA.usdjpy = (prices[0].get('ask') + prices[0].get('bid')) / 2.0
        ask = str(int(1000 * prices[0].get('ask')))
        bid = str(int(1000 * prices[0].get('bid')))
        self.usdjpy.set('USDJPY\t\t\t' + ask[:3] + '.' + ask[3:] + '\t' + bid[:3] + '.' + bid[3:])

        prices = self.oanda.get_prices(instruments='EUR_JPY').get('prices')
        OANDA.eurjpy = (prices[0].get('ask') + prices[0].get('bid')) / 2.0
        ask = str(int(1000 * prices[0].get('ask')))
        bid = str(int(1000 * prices[0].get('bid')))
        self.eurjpy.set('EURJPY\t\t\t' + ask[:3] + '.' + ask[3:] + '\t' + bid[:3] + '.' + bid[3:])


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

    def getPrice(self):

        data = load(urlopen(self.url))
    #    print(exchange + '\t' + str(data[last]) + '\t' +  str(data[ask]) + '\t' +  str(data[bid]))
        self.ask = int(data[self.sask])
        self.bid = int(data[self.sbid])

        a = str(self.ask)
        b = str(self.bid)
        l = str(int(data[self.last]))
    
        self.str.set(self.name + (' ' * (20 - len(self.name))) + '\t' + l[:3] + ',' + l[3:] + '\t' +  a[:3] + ',' + a[3:] + '\t' +  b[:3] + ',' + b[3:])


class USDExchange(Exchange):

    def __init__(self, root, name, url, last, sask, sbid):    
        Exchange.__init__(self, root, name, url, last, sask, sbid)

    def getPrice(self):

        data = load(urlopen(self.url))
    #    print(exchange + '\t' + str(data[last]) + '\t' +  str(data[ask]) + '\t' +  str(data[bid]))
        self.ask = float(data[self.sask]) * OANDA.usdjpy
        self.bid = float(data[self.sbid]) * OANDA.usdjpy

        a = str(int(round(self.ask)))
        b = str(int(round(self.bid)))
        l = str(int(round(float(data[self.last]) * OANDA.usdjpy)))

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
OANDA(window.root), \
]
exchangeList.reverse()


def updatePrice():

    minAsk = 100000000
    maxBid = 0

    for e in exchangeList:
        e.getPrice()

#        if e.ask < minAsk:
#            minAsk = e.ask
#            askLabel = e.label
#        if maxBid < e.bid:
#            maxBid = e.bid
#            bidLabel = e.label

#    askLabel.configure(fg = 'red')
#    bidLabel.configure(fg = 'blue')

    window.update()    
    window.root.after(1000, updatePrice)

updatePrice()
window.root.mainloop()
