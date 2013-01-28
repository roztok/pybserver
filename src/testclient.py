#!/usr/bin/python3
#-*- coding: utf-8 -*-

"""
Easy xmlrpc client
"""


import xmlrpc.client
from datetime import datetime
import time




def test():
    proxy = xmlrpc.client.ServerProxy("http://10.50.111.169:8080/")

    timer = 0
    counter = 0

    while 1:
        second = datetime.now().second
        if timer == second:
            counter = counter+1
        else:
            print(timer, "-", counter)
            timer = second
            counter = 0
        #endif
        st = time.time()
        res = proxy.chat.listMessages()
        #print("===%sms===" % ((time.time()-st)*1000))
    #endwhile

import multiprocessing
    
for i in (1,2,3,4,5,6,7,8,9,10,11,12,13):
    
    process = multiprocessing.Process(target=test, args=())
    process.start()
#endfor
