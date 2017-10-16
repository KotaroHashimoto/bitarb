#!/usr/bin/env python3

from json import load
from datetime import datetime
from threading import Thread
from time import sleep
from oandapy import API
import datetime as dt
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

    PERIOD = 1.5
    FONT = 'Arial'
    FSIZE = 12

    def __init__(self, title):
        Thread.__init__(self)
    
        self.root = Tk()
        self.root.title(title)

        self.str = StringVar()
        self.str.set('')
        Label(self.root, textvariable = self.str, font = (Window.FONT, Window.FSIZE)).pack()

        Label(text = 'Exchange' + (' '*8) + '\tLast\tAsk\tBid', font = (Window.FONT, Window.FSIZE)).pack()
        
        self.root.bind('<MouseWheel>', self.onMouseWheel)
        self.root.bind('<Up>', self.expand)
        self.root.bind('<Right>', self.expand)
        self.root.bind('<Down>', self.shrink)
        self.root.bind('<Left>', self.shrink)

    def run(self):
    
        while True:
            try:
                self.str.set(datetime.now().strftime('%Y/%m/%d  %H:%M:%S'))
                sleep(Window.PERIOD)

            except:
                sleep(10)
                continue

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
            try:
                data = load(urlopen(Request(self.url, headers = {'User-Agent':'Hoge Browser'})))

                if self.name == 'Zaif BTC/JPY':
                    XemExchange.ZAIFBTCJPY = float(data[self.last])

                self.ask = float(data[self.sask])
                self.bid = float(data[self.sbid])
        
                up = float(data[self.last])
                self.label.configure(fg = ('black' if self.p == up else ('red' if self.p > up else 'green')))
                self.p = up

                if self.name == 'Zaif BTC/JPY':
                    a = str(round(self.ask))
                    b = str(round(self.bid))
                    l = str(round(self.p))

                else:
                    a = str(format(self.ask, '.8f'))
                    b = str(format(self.bid, '.8f'))
                    l = str(format(self.p, '.8f'))
                
                self.str.set(self.name + (' ' * (20 - len(self.name))) + '\t' + l + '\t' +  a + '\t' +  b)
                sleep(Window.PERIOD)

            except Exception as e:
                print('Exchange ', e, ', ', self.name)
                self.label.configure(fg = 'gray')
                sleep(10)
                self.label.configure(fg = 'black')
                continue


class XemExchange(Exchange):

    TREXXEMBTC = 1
    ZAIFBTCJPY = 1

    ZXEM_ASK = 0
    TXEM_ASK = 0
    ZXEM_BID = 0
    TXEM_BID = 0

    mjstr = None
    ztstr = None

    def __init__(self, root, name, url, last, sask, sbid):    

        Exchange.__init__(self, root, name, url, last, sask, sbid)

        if name == 'Bittrex MONA/JPY':
            XemExchange.mjstr = StringVar()
            XemExchange.mjstr.set('')
            XemExchange.mjlabel = Label(root, textvariable = XemExchange.mjstr, font = (Window.FONT, Window.FSIZE))

            XemExchange.ztstr = StringVar()
            XemExchange.ztstr.set('')
            XemExchange.ztlabel = Label(root, textvariable = XemExchange.ztstr, font = (Window.FONT, Window.FSIZE))


    def run(self):
    
        while True:
            try:
                up = 0

                if self.name == 'Zaif MONA/JPY':
                    data = load(urlopen(Request(self.url, headers = {'User-Agent':'Hoge Browser'})))

                    self.ask = float(data[self.sask])
                    self.bid = float(data[self.sbid])
                    up = float(data[self.last])
                    XemExchange.ZXEM_ASK = self.ask
                    XemExchange.ZXEM_BID = self.bid

                elif self.name == 'Bittrex MONA/JPY':
                    data = load(urlopen(Request(self.url, headers = {'User-Agent':'Hoge Browser'})))
                    XemExchange.TREXXEMBTC = data['result']

                if self.name == 'Bittrex MONA/JPY' and XemExchange.ZAIFBTCJPY and XemExchange.TREXXEMBTC:
                    self.ask = float(XemExchange.TREXXEMBTC[self.sask]) * XemExchange.ZAIFBTCJPY
                    self.bid = float(XemExchange.TREXXEMBTC[self.sbid]) * XemExchange.ZAIFBTCJPY
                    up = float(XemExchange.TREXXEMBTC[self.last]) * XemExchange.ZAIFBTCJPY
                    XemExchange.TXEM_ASK = self.ask
                    XemExchange.TXEM_BID = self.bid

                self.label.configure(fg = ('black' if self.p == up else ('red' if self.p > up else 'green')))
                self.p = up

                a = str(round(self.ask, 1))
                b = str(round(self.bid, 1))
                l = str(round(self.p, 1))

                self.str.set(self.name + (' ' * (20 - len(self.name))) + '\t' + l + '\t' +  a + '\t' +  b)

                if self.name == 'Bittrex MONA/JPY' and 0 < XemExchange.TXEM_BID and 0 < XemExchange.TXEM_ASK:

                    if XemExchange.TXEM_ASK < XemExchange.ZXEM_BID:
                        v = round(100 * (XemExchange.ZXEM_BID / XemExchange.TXEM_ASK - 1), 4)
                    
                    elif XemExchange.ZXEM_ASK < XemExchange.TXEM_BID:
                        v = round(100 * (XemExchange.ZXEM_ASK / XemExchange.TXEM_BID - 1), 4)

                    else:
                        v = 0

                    l = str(format(XemExchange.TREXXEMBTC[self.last], '.8f'))
                    a = str(format(XemExchange.TREXXEMBTC[self.sask], '.8f'))
                    b = str(format(XemExchange.TREXXEMBTC[self.sbid], '.8f'))
                    self.mjstr.set('Bittrex MONA/BTC' + (' ' * (20 - len('Bittrex MONA/BTC'))) + '\t' + l + '\t' + a + '\t' + b)
                    self.ztstr.set('Zaif MONA / Bittrex MONA \t' + ('+' if 0 < v else '') + str(v) + ' %')

                sleep(Window.PERIOD)

            except Exception as e:
                print('Xem Exchange ', e, ', ', self.name)
                self.label.configure(fg = 'gray')
                sleep(10)
                self.label.configure(fg = 'black')
                continue


if __name__ == '__main__':

    ssl._create_default_https_context = ssl._create_unverified_context

    window = Window('MONA Live Price')

    base = [ \
        Exchange(window.root, 'Zaif BTC/JPY', 'https://api.zaif.jp/api/1/ticker/btc_jpy', 'last', 'ask', 'bid'), \
        ]

    xem = [ \
        XemExchange(window.root, 'Zaif MONA/JPY', 'https://api.zaif.jp/api/1/ticker/mona_jpy', 'last', 'ask', 'bid'), \
        XemExchange(window.root, 'Bittrex MONA/JPY', 'https://bittrex.com/api/v1.1/public/getticker?market=btc-mona', 'Last', 'Ask', 'Bid'), \
        ] 

    base.append(Exchange(window.root, 'Zaif MONA/BTC', 'https://api.zaif.jp/api/1/ticker/mona_btc', 'last', 'ask', 'bid'))

    XemExchange.mjlabel.pack()
    XemExchange.ztlabel.pack()

    exchangeList = tuple([window] + base + xem)

    for e in exchangeList:
        e.setDaemon(True)
        e.start()

    window.root.mainloop()
