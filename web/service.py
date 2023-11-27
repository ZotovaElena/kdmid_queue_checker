import time
import os
import argparse 
import threading
import json 

from core.queue_checker import QueueChecker


# kdmid_subdomain = 'madrid' 
# order_id = '130238' 
# code = 'CD9E05C1' 

# kdmid_subdomain = 'barcelona' 
# order_id = '205619' 
# code = '8367159E' 

# every_hours = 3

# kdmid_subdomain = 'madrid' 
# order_id = '151321' 
# code = '5CCF3A7C' 

# 'madrid', '151321', '5CCF3A7C'

checker = QueueChecker()

def run_check_queue(kdmid_subdomain, order_id, code, every_hours=1):
    success_file = order_id+"_"+code+"_success.json"
    error_file = order_id+"_"+code+"_error.json"

    while True:
        message, status = checker.check_queue(kdmid_subdomain, order_id, code)

        if os.path.isfile(success_file) or os.path.isfile(error_file):
            break

        time.sleep(every_hours*3600)  # Pause for every_hours * hour before the next check
    



# run_check_queue(kdmid_subdomain, order_id, code)
