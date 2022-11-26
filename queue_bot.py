# -*- coding: utf-8 -*-
"""
Created on Sat Nov 26 00:14:54 2022

@author: zotov
"""
import time
import sys
import os

from queue_class import QueueChecker

kdmid_subdomain = 'madrid' 
order_id = '123610' 
code = '7AE8EFCC' 
num_hours = 3


queue_checker = QueueChecker(kdmid_subdomain, order_id, code)

   
success = False

while not success:
    if not os.path.isfile(queue_checker.order_id+"_"+queue_checker.code+"_success.txt"): 
        queue_checker.check_queue()
        time.sleep(num_hours*3600)
    else: 
        print('file exists, exiting')
        success = True
        sys.exit()
