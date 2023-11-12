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

kdmid_subdomain = 'madrid' 
order_id = '130238' 
code = 'CD9E05C1' 

checker = QueueChecker()

def run_check_queue(kdmid_subdomain, order_id, code, every_hours=1):
    success_file = order_id+"_"+code+"_success.json"
    error_file = order_id+"_"+code+"_error.json"

    while True:
        checker.check_queue(kdmid_subdomain, order_id, code)

        if os.path.isfile(success_file) or os.path.isfile(error_file):
            break

        time.sleep(every_hours*3600)  # Pause for every_hours * hour before the next check

run_check_queue(kdmid_subdomain, order_id, code)

# def run_check_queue(kdmid_subdomain, order_id, code, every_hours=1, event: threading.Event):
#     success_file = order_id + "_" + code + "_success.json"
#     error_file = order_id + "_" + code + "_error.json"

#     while not os.path.isfile(success_file) and not os.path.isfile(error_file):
#         checker.check_queue(kdmid_subdomain, order_id, code)
#         time.sleep(every_hours*3600)
#         event.set()  # Signal that the file has been written
        
# def run_check_queue(kdmid_subdomain, order_id, code, every_hours=1):
# 	success = False
# 	error = False
# 	while not success:
# 		if not os.path.isfile(order_id+"_"+code+"_success.json"):
# 			print('1', success)
# 			checker.check_queue(kdmid_subdomain, order_id, code)
# 			time.sleep(every_hours*3600)
# 			print('2', success)
# 		else:
# 			success = True
# 			print('3', success)

# def run_check_queue(kdmid_subdomain, order_id, code, every_hours=1):
# 	success_file = order_id + "_" + code + "_success.json"
# 	error_file = order_id + "_" + code + "_error.json"

# 	while not os.path.isfile(success_file) and not os.path.isfile(error_file):
# 		checker.check_queue(kdmid_subdomain, order_id, code)
# 		time.sleep(every_hours*3600)

# 	if os.path.isfile(success_file):
# 		with open(success_file, 'r') as f:
# 			d = json.load(f)
# 		return d
# 	elif os.path.isfile(error_file):
# 		with open(error_file, 'r') as f:
# 			d = json.load(f)
# 		print(d)
# 		return d

    # threading.Thread(target=checker.check_queue(kdmid_subdomain, order_id, code)).start()
    # print('threading started')

    # while not os.path.isfile(success_file) and not os.path.isfile(error_file):
    #     time.sleep(1)  # Check every 10 seconds













        
# run_check_queue('madrid', '130238', 'CD9E05C1', 1)