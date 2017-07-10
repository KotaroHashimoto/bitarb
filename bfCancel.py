#!/usr/bin/env python3

API_KEY = ''
API_SECRET = ''


import pybitflyer
from math import sqrt, floor
from json import loads, dump
from datetime import datetime
from threading import Thread
from time import sleep, time
import ssl
import requests
import os
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


class BitFlyer(Thread):

    api = None

    equity = 0
    pnl = 0
    margin = 0
    quantity = '0'

    REPORT = ''

    def __init__(self, root):
        Thread.__init__(self)
    
        self.name = 'biyFlyer'
        self.reset()

        self.str = StringVar()
        self.str.set('')
        Label(root, textvariable = self.str, font = (Window.FONT, Window.FSIZE)).pack()

        Button(root, text = 'cancell all orders', command = self.cancelOrders).pack()

    def reset(self):
        BitFlyer.api = pybitflyer.API(api_key = API_KEY, api_secret = API_SECRET)

    def cancelOrders(self):
        for code in {'BTC_JPY', 'FX_BTC_JPY', 'ETH_BTC', 'BTCJPY_MAT1WK', 'BTCJPY_MAT2WK'}:
            ret = BitFlyer.api.cancelallchildorders(product_code = code)
            print(code, ret)

    def run(self):

        while True:
            if BitFlyer.api.gethealth(product_code = 'FX_BTC_JPY')['status'] != 'STOP':
                ret = BitFlyer.api.getcollateral()
                BitFlyer.pnl = ret['open_position_pnl']
                BitFlyer.equity = ret['collateral'] + BitFlyer.pnl
                m = ret['require_collateral']

                result = BitFlyer.api.getpositions(product_code = 'FX_BTC_JPY')
                if 0 < len(result):
                    size = 0
                    for r in result:
                        size += r['size']
                    BitFlyer.quantity = result[0]['side'] + ' ' + str(size) + (': +' if 0 < BitFlyer.pnl else ': ') + str(round(BitFlyer.pnl, 2))

                else:
                    BitFlyer.quantity = '0'

                if 0 < m:
                    BitFlyer.margin = 100.0 * BitFlyer.equity / m
                else:
                    BitFlyer.margin = 0.0

            else:
                BitFlyer.pnl = 0
                BitFlyer.equity = 0
                BitFlyer.margin = 0
                self.reset()

            BitFlyer.REPORT = 'JPY:' + str(round(BitFlyer.equity)) + ' (PNL: ' + BitFlyer.quantity + '), ' + str(round(BitFlyer.margin, 2)) + '%'
            self.str.set(BitFlyer.REPORT)
            sleep(Window.PERIOD)


class Window(Thread):

    PERIOD = 1
    FONT = 'Arial'
    FSIZE = 12
    REPORT = ''

    def __init__(self, title):
        Thread.__init__(self)
    
        self.root = Tk()
        self.root.title(title)

        self.tstr = StringVar()
        self.tstr.set('')
        Label(self.root, textvariable = self.tstr, font = (Window.FONT, Window.FSIZE)).pack()
        
        self.root.bind('<MouseWheel>', self.onMouseWheel)
        self.root.bind('<Up>', self.expand)
        self.root.bind('<Right>', self.expand)
        self.root.bind('<Down>', self.shrink)
        self.root.bind('<Left>', self.shrink)

    def run(self):

        while True:
            try:
                self.tstr.set(datetime.now().strftime('%Y/%m/%d  %H:%M:%S'))
                sleep(Window.PERIOD)

            except Exception as e:
                print(e)
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



if __name__ == '__main__':

    ssl._create_default_https_context = ssl._create_unverified_context
    window = Window('bitFlyer Position Canceller')

    exchangeList = tuple([ \
        window, \
        BitFlyer(window.root), \
        ]
    )

    for e in exchangeList:
        e.setDaemon(True)
        e.start()

    window.root.mainloop()
