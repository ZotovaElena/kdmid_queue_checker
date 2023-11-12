import time
import os
import argparse 

from core.queue_checker import QueueChecker


# kdmid_subdomain = 'madrid' 
# order_id = '130238' 
# code = 'CD9E05C1' 

# kdmid_subdomain = 'barcelona' 
# order_id = '205619' 
# code = '8367159E' 

# every_hours = 3

checker = QueueChecker()

def run_check_queue(kdmid_subdomain, order_id, code, every_hours=1):
	success = False
	while not success:
		if not os.path.isfile(order_id+"_"+code+"_success.txt"):
			message, status = checker.check_queue(kdmid_subdomain, order_id, code)
			time.sleep(every_hours*3600)
		else:
			success = True
	return message, status


