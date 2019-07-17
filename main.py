#!/usr/bin/env python3

import requests
import os
import time
import json
from interface import *
from usbconfig import *
from repeater import *

config = get_current_config()

id = config['id']
card_receiver = "https://test.qwickly.tools/cardreaderrequest/"
checkin_receiver = "https://test.qwickly.tools/requestinfo/"

session = requests.Session()


def is_connected():
	# Ping a DNS server to check connection
	return os.system('ping 8.8.8.8 -c 1 -w 1 -q') == 0
	

def transmit(event):
	iface.indicate_pending()
	
	payload = {'device_id':id, 'card_swipe_value':iface.get_entry()}
	r = session.post(card_receiver, data=payload).json()
	print(r)
		
	if (r['Status'] == 'success'):
		iface.indicate_success()
	else:
		iface.indicate_failure()
		
	
def on_close():
	config_repeater.stop.set()
	checkin_repeater.stop.set()
		
	
def detect_and_apply_config():
	conf = get_provided_config()
	
	if conf:
		iface.indicate_usb_connect()
		
		if config_needed():
			perform_config()
			iface.indicate_reboot()
			time.sleep(5)
			os.popen('reboot')
	
	else:
		iface.indicate_no_usb()


def check_in():
	if not is_connected():
		iface.set_unconfigured()
		return
	
	r = session.get(checkin_receiver).json()
	
	if r['found_open_session']:
		iface.set_active()
	else:
		iface.set_idle()
		

iface = Interface(is_connected())
iface.set_on_entry(transmit)
iface.set_on_close(on_close)

config_repeater = Repeater(action=detect_and_apply_config, duration=1)
config_repeater.start()

checkin_repeater = Repeater(action=check_in, duration=int(config['ping_frequency']))
checkin_repeater.start()

iface.mainloop()
