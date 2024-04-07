import time
import os
import logging

logger = logging.getLogger(__name__)

def ping_response_to_str(response, hostname):
	if response == 0:
		return f"Host '{hostname}' is up ({response})"
	else:
		return f"Host '{hostname}' is down ({response})"

def batch_filter_entrypoint(batch_item={}, config={}):
	hostname = batch_item.get("data", None)
	logger.info(f"PING BATCH FILTER IS RUNNING WITH {hostname} ######################")
	if hostname == None:
		return None, "No hostname specified as input"
	response = os.system(f"ping -c 1 -w2 {hostname} > /dev/null 2>&1")
	logger.info("#########################################################")
	return ping_response_to_str(response, hostname), None
