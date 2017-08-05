#!/usr/bin/env python3

import pybitflyer
from json import loads, dump
from datetime import datetime
from threading import Thread
from time import sleep, time
from math import floor
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
    
    N = 32
    api = None

    def __init__(self, root):
        Thread.__init__(self)
    
        self.name = 'biyFlyer'

        self.scrollbar = Scrollbar(root)
        self.listbox = Listbox(root, yscrollcommand = self.scrollbar.set, width = 0)
        self.listbox.pack(side = LEFT, fill = BOTH)

        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.scrollbar.config(command = self.listbox.yview)

        self.reset()

    def reset(self):
        BitFlyer.api = pybitflyer.API()

        self.listbox.delete(0, END)
                    
        for i in range(1 + 2 * BitFlyer.N):
            self.listbox.insert(END, '')

        self.listbox.see(BitFlyer.N)

    def getOrderBook(self):
        return BitFlyer.api.board(product_code = 'FX_BTC_JPY')

    def run(self):

        while True:
            try:
                if BitFlyer.api.gethealth(product_code = 'FX_BTC_JPY')['status'] != 'STOP':
                    ret = self.getOrderBook()

                    barpos = self.scrollbar.get()[0]
                    index = 0

                    for i in range(BitFlyer.N):
                        b = str(ret['asks'][BitFlyer.N - 1 - i]['size'])

                        bsp = b.split('.')
                        b = (len(bsp[0]) - 1) * '_' + b

                        b += '0' * (8 - len(bsp[-1]) - len(bsp[0]) + 1)
                        content = b + ('_' * (15 - len(b))) + str(ret['asks'][BitFlyer.N - 1 - i]['price']).split('.')[0] + ('_' * 13) + ('.' if BitFlyer.N - i > 9 else '.0') + str(BitFlyer.N - i)
                        self.listbox.insert(index, content)
                        index += 1
                        self.listbox.delete(index)

                    content = '00.' + ('_' * 12) + str(ret['mid_price']).split('.')[0] + ('_' * 13) + '.00'
                    self.listbox.insert(index, content)
                    index += 1
                    self.listbox.delete(index)

                    for i in range(BitFlyer.N):
                        a = str(ret['bids'][i]['size'])
                        a += '0' * (8 - len(a.split('.')[-1]))
                        content =  ('' if i + 1 > 9 else '0') + str(i + 1) + '.' + ('_' * 12) + str(ret['bids'][i]['price']).split('.')[0] + ('_' * (16 - len(a))) + a
                        self.listbox.insert(index, content)
                        index += 1
                        self.listbox.delete(index)

                    self.listbox.yview_moveto(barpos)

                else:
                    self.reset()

                sleep(Window.PERIOD)

            except:
                self.reset()
                first = True
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
