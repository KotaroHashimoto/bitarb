#!/usr/bin/env python3


import pybitflyer
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

    N = 16
    api = None
    space = 12

    def __init__(self, root):
        Thread.__init__(self)
    
        self.name = 'biyFlyer'
        self.reset()

        self.str = [StringVar() for i in range(1 + 2 * BitFlyer.N)]

        for i in range(1 + 2 * BitFlyer.N):
            self.str[i].set('')
            Label(root, textvariable = self.str[i], font = (Window.FONT, Window.FSIZE)).pack()

    def reset(self):
        BitFlyer.api = pybitflyer.API()

    def getOrderBook(self):
        return BitFlyer.api.board(product_code = 'FX_BTC_JPY')

    def run(self):

        while True:
            if BitFlyer.api.gethealth(product_code = 'FX_BTC_JPY')['status'] != 'STOP':
                ret = self.getOrderBook()

                for i in range(BitFlyer.N):
                    b = str(ret['asks'][i]['size'])
                    b += '0' * (10 - len(b))
                    self.str[BitFlyer.N-1 - i].set(b + ('  ' * (BitFlyer.space - len(b))) + str(ret['asks'][i]['price']) + ('  ' * BitFlyer.space))

                    a = str(ret['bids'][i]['size'])
                    a += '0' * (10 - len(a))
                    self.str[BitFlyer.N+1 + i].set(('  ' * BitFlyer.space) + str(ret['bids'][i]['price']) + ('  ' * (BitFlyer.space - len(a))) + a)

                self.str[BitFlyer.N].set(('  ' * BitFlyer.space) + str(ret['mid_price']) + ('  ' * BitFlyer.space))

            else:
                self.reset()

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
    window = Window('bitFlyer FX Order Book')

    exchangeList = tuple([ \
        window, \
        BitFlyer(window.root), \
        ]
    )

    for e in exchangeList:
        e.setDaemon(True)
        e.start()

    window.root.mainloop()
