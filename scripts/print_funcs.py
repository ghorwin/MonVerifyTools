#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Developed at IBK, TU Dresden, Germany
#
# Authors: Andreas Nicolai <andreas.nicolai -at- tu-dresden[dot]de>
#
# License: BSD(2) License, see LICENSE file

import config
from colorama import *

def printError(msg):
	if config.USE_COLORS:
		print (Fore.RED + Style.BRIGHT + msg + Fore.RESET + Style.RESET_ALL)
	else:
		print (msg)

def printWarning(msg):
	if config.USE_COLORS:
		print (Fore.YELLOW + Style.BRIGHT + msg + Fore.RESET + Style.RESET_ALL)
	else:
		print (msg)

def printNotification(msg):
	if config.USE_COLORS:
		print (Fore.GREEN + Style.BRIGHT + msg + Fore.RESET + Style.RESET_ALL)
	else:
		print (msg)
