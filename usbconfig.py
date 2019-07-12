#!/usr/bin/env python3

import os
import json
import re

def get_flashdrive_path():
	"""
	Return the path to a connected usb storage device.
	If no storage device is connected, return None
	"""
	
	media_list = os.listdir('/media/pi/')
	media_list.remove('SETTINGS')
	
	if media_list:
		drive_name = media_list[0]
		return '/media/pi/{}'.format(drive_name)
	else:
		return None


def get_provided_config(dir_path=None):
	"""
	Search the provided directory for CARDSWIPERCONFIG.json
	If it is present, return its contents as a dict
	If not present, return None
	"""
	
	# Allow use with any directory but flashdrive is default
	if dir_path == None:
		dir_path = get_flashdrive_path()

	dir_contents = os.listdir(dir_path)
	
	if 'CARDSWIPERCONFIG.json' in dir_contents:
		config_file = open(dir_path + '/CARDSWIPERCONFIG.json', 'r')
		config_data = json.load(config_file)
		config_file.close()
		
		return config_data
	else:
		return None
		

def get_current_config():
	"""
	Return contents of current configuration file, omit "id"
	"""
	
	config_file = open('/home/pi/qwickly/CONFIG.json', 'r')
	config_data = json.load(config_file)
	config_file.close()
	
	return config_data


def config_needed():
	"""
	Return True if provided configuration is not already implemented
	"""
	
	new_conf = get_provided_config()
	
	if not new_conf:
		return False
	
	old_conf = get_current_config()
	del old_conf['id']
	
	return new_conf != old_conf
	

def _get_network_config():
	"""
	Return current Wi-Fi configurations as a list of dicts
	"""
	
	config_file = open('/etc/wpa_supplicant/wpa_supplicant.conf', 'r')
	config_text = config_file.read()
	config_file.close()
	
	# Get each network configuration as a string
	network_texts = [
		t.strip().replace('\t', '') 
		for t 
		in re.findall('network={(.*?)}', config_text, re.S)
	]
	
	current_config = list()
	
	# Iterate over each string represantation of a configuration
	for text in network_texts:
		
		# Separate each of the network attributes
		attributes = text.split('\n')
		
		attributes_dict = dict()
		
		for attr in attributes:
			# Break down attribute to a name and value
			name, value = attr.split('=')
			attributes_dict[name] = value
		
		current_config.append(attributes_dict)
	
	return current_config


def _set_network_config(net_config):
	"""
	Apply provided config to Wi-Fi settings
	"""
	
	config_file = open('/etc/wpa_supplicant/wpa_supplicant.conf', 'r')
	config_text = config_file.read()
	config_file.close()
	
	# Get and remove all network configurations
	networks = re.findall('network={.*?}', config_text, re.S)
	
	for n in networks:
		config_text = config_text.replace(n, '')
	
	config_text = config_text.strip()
	config_text += '\n'
	
	for n in net_config:
		config_text += '\nnetwork={\n'
		
		for key, value in n.items():
			config_text += '\t{}={}\n'.format(key, value)
		
		config_text += '}'
		
	
	config_file = open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w')
	config_file.write(config_text)
	config_file.close()


def perform_config():
	"""
	Copy CARDSWIPERCONFIG and apply new settings
	"""
	
	id = get_current_config()['id']
	
	config_data = get_provided_config()
	config_data['id'] = id
	
	config_file = open('/home/pi/qwickly/CONFIG.json', 'w')
	json.dump(config_data, config_file)
	config_file.close()
	
	if _get_network_config() != config_data['network']:
		_set_network_config(config_data['network'])
	
	os.system("amixer sset 'Master' {}%".format(config_data['volume']))
	
