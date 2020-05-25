#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Log file writer implementation.
"""

import datetime

from print_funcs import *

LOG_DIR = "" # set in MonVerifyTool script
TIME_STAMP = "" # time stamp for start of main script run, set in MonVerifyTool script

def process_log(category, filepath):
	"""Opens the log file and appends a log message with given type. 
	
	Arguments
	---------
	
	- category
		'Archiving', 'Bypassing', 'Error', 'Corrected'
	- filepath
	    path to the file (relative to dropbox directory)
	"""
	with open(LOG_DIR + "/processed", 'a') as f:
		f.write("{:20s}\t{:10s}\t{}\n".format(datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), category, filepath))

def error_log(category, filepath, message):
	"""Opens the error log file and appends a log message with given type. 
	
	Arguments
	---------
	
	- category
		one of the error categories
	- filepath
	    path to the file (relative to dropbox directory)
	- message
		The message text.
	"""
	with open(LOG_DIR + "/errors_{}".format(TIME_STAMP), 'a') as f:
		f.write("{:20s}\t{:50s}\t{}\n".format(category, filepath, message))

