#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Developed at IBK, TU Dresden, Germany
#
# Authors: Andreas Nicolai <andreas.nicolai -at- tu-dresden[dot]de>
#
# License: BSD(2) License, see LICENSE file

"""
Script to process incoming (measurement) data, check and process it, and handle any errors along the way.

Basic functionality:
- read config
- init/check working directory structure
- process new files

Error handling:

- any errors related to general script operation, reading of configuration files etc. are logged
  into file 'log/errors'

Syntax:

    > MonVerifyTool.py [<path/to/serverRoot>]
  
If no path is given as argument, the current working directory is expected to be the server root.
"""

import os
import stat
import platform
import argparse
import shutil # for copyfile
import datetime

from print_funcs import *
from ConfigFiles import ConfigFiles
from Logger import process_log, error_log
import Logger

def checkForMissingFiles(archiveDir, projectConfig):
	# first collect a list of expected files
	archivesFiles = dict() # key is the expected file prefix, value is a list a of files found in archive directory
	# initialize map
	for exp in projectConfig.expectedFiles:
		archivesFiles[exp] = []
	
	# now process all files in archive dir
	archivePathParts = archiveDir.split('/') # split into path components
	for root, dirs, files in os.walk(archiveDir, topdown=False):
	
		rootStr = root.replace('\\', '/') # windows fix
		pathParts = rootStr.split('/') # split into component
		pathParts = pathParts[len(archivePathParts):] # keep only path parts below toplevel dir
	
		# check for valid files
		for nf in files:
			if len(pathParts) == 0:
				newFilePath = nf
			else:
				newFilePath = "/".join(pathParts) + "/" + nf
			
			# insert into appropriate list
			for exp in projectConfig.expectedFiles:
				if newFilePath.find(exp) == 0:
					archivesFiles[exp].append(nf)
					break
	
	missingFiles = []
	
	# now process all directories and get a sorted list
	for exp in projectConfig.expectedFiles:
		af = sorted(archivesFiles[exp])
		# skip empty directories/not existing expected files
		if len(af) == 0:
			# only mention that todays file is missing
			missingFiles.append( exp + datetime.datetime.today().strftime('%Y-%m-%d_00-00-00.csv') )
			continue 
	
		# if list is not empty, get the first time stamp
		firstDateStr = af[0].split("_")[1]
		# now process all dates since this first day and check if one is missing
		firstDate = datetime.datetime.strptime(firstDateStr, '%Y-%m-%d')
		todaysDate = datetime.datetime.today()
		d = firstDate + datetime.timedelta(1) # add one day
		while d <= todaysDate:
			dStr = exp + d.strftime('%Y-%m-%d_00-00-00.csv')
			if not dStr in af:
				missingFiles.append( dStr )
			d = d + datetime.timedelta(1) # add one day
	
	retcode = 0
	if len(missingFiles) == 0:
		if os.path.exists(logDir + "/missing"):
			os.remove(logDir + "/missing")
	else:
		retcode = 1
		# now create missing file
		with open(logDir + "/missing",'w') as fobj:
			fobj.write("\n".join(missingFiles))
		printError("There are {} missing files.".format(len(missingFiles)) )
		error_log('MissingFiles', "", "There are {} missing files.".format(len(missingFiles)) )
		
	return (retcode,len(missingFiles))


# ---- main ----

# command line arguments
parser = argparse.ArgumentParser(description="Process incoming files and perform conversions and sanity checks.")
parser.add_argument('projectDir', nargs='?', help='Root directory for a project to process.', default=os.getcwd())

args = parser.parse_args()

print("Processing directory '{}'".format(args.projectDir))

# check if directory structure does not exist and bail out of not available
if not os.path.exists(args.projectDir):
	printError("Directory '{}' does not exist. You need to create the directory structure first and set the required permissions.".format(args.projectDir))
	exit(1)
	
	
# create subdirectories if not existing
subdirs = ['dropbox', 'config', 'log', 'review', 'archive', 'bypass']
for d in subdirs:
	subDir = args.projectDir + '/' + d
	if not os.path.exists(subDir):
		printError("Directory '{}' does not exist. You need to create the directory structure first and set the required permissions.".format(subDir))
		exit(1)

# ---- Convenience variables for subdirectories ----

configDir = args.projectDir + "/config"
statusDir = args.projectDir + "/status"
logDir = args.projectDir + "/log"
archiveDir = args.projectDir + "/archive"
dropboxDir = args.projectDir + "/dropbox"
reviewDir = args.projectDir + "/review"
bypassDir = args.projectDir + "/bypass"

Logger.LOG_DIR = logDir
Logger.TIME_STAMP = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S')

# initialize return code with 0 (all ok)
retcode = 0

# ---- Parse .exp files from config directory ----

configFiles = os.listdir(configDir)
expFiles = [f for f in configFiles if len(f)>4 and f[-4:] == '.exp']
if len(expFiles) == 0:
	printError("Missing .exp file in config directory. Please add exactly one .exp file into this directory!")
	error_log('Critical', '', "Missing .exp file in config directory. Please add exactly one .exp file into this directory!")
	exit(1)
if len(expFiles) != 1:
	printError("Exactly one .exp file is allowed in config directory. Please remove any surplus .exp files!")
	error_log('Critical', '', "Exactly one .exp file is allowed in config directory. Please remove any surplus .exp files!")
	exit(1)

projectConfig = ConfigFiles()
try:
	projectConfig.readExp(configDir + '/' + expFiles[0])
except RuntimeError as e:
	printError(str(e))
	printError("Error reading expectation file '{}'".format(expFiles[0]))
	error_log('Critical', e.message, '')
	error_log('Critical', "Error reading expectation file '{}'".format(expFiles[0]), '')
	exit(1)
except IOError as e:
	printError(e.strerror)
	printError("Error reading expectation file '{}'".format(expFiles[0]))
	error_log('Critical', e.strerror, '')
	error_log('Critical', "Error reading expectation file '{}'".format(expFiles[0]), '')
	exit(1)

if len(projectConfig.expectedFiles) == 0:
	printError("No files expected in this project. Please add content to the ExpectedFiles attribute!")
	error_log('Critical', "No files expected in this project. Please add content to the ExpectedFiles attribute!", '')
	exit(1)


# ---- check for new files in dropbox directory ----

dropboxPathParts = dropboxDir.split('/') # split into path components

for root, dirs, files in os.walk(dropboxDir, topdown=False):

	rootStr = root.replace('\\', '/') # windows fix
	pathParts = rootStr.split('/') # split into component
	pathParts = pathParts[len(dropboxPathParts):] # keep only path parts below toplevel dir

	# check for valid files
	for nf in sorted(files):
		# path relative to dropbox dir
		if len(pathParts) == 0:
			newFilePath = nf
		else:
			newFilePath = "/".join(pathParts) + "/" + nf
		
		# check, if file is in bypass list
		if projectConfig.bypassRuleAppliesToFile(newFilePath):
			print("Applying bypass rule to file '{}'.".format(newFilePath))
			process_log('Bypassing', newFilePath)
			# move file to bypass folder
			# first create subdirectory, if not existing
			targetDir = bypassDir + "/" + "/".join(pathParts)
			if not os.path.exists(targetDir):
				os.makedirs(targetDir)
			shutil.move(dropboxDir + '/' + newFilePath, bypassDir + "/" + newFilePath)
			continue
		
		nameParts = os.path.splitext(nf)
		if len(nameParts) != 2 or (nameParts[1] != '.csv'):
			printError("Unexpected file '{}' in dropbox folder.".format(newFilePath))
			error_log('NotExpected', newFilePath, "Unexpected file in dropbox folder.")
			# move file to review folder
			# first create subdirectory, if not existing
			targetDir = reviewDir + "/" + "/".join(pathParts)
			if not os.path.exists(targetDir):
				os.makedirs(targetDir)
			shutil.move(dropboxDir + '/' + newFilePath, reviewDir + "/" + newFilePath)
			retcode = 1
			continue
		
		# must be a csv file
		# check, if we are expecting a file like this
		matchingEf = None
		for ef in projectConfig.expectedFiles:
			#print("Testing  file '{}' against expected file '{}'".format(newFilePath, ef))
			if newFilePath.find(ef) == 0:
				matchingEf = projectConfig.expectedFiles[ef]
				break
		
		if matchingEf == None:
			printError("Unexpected file '{}' in dropbox folder.".format(newFilePath))
			error_log('NotExpected', newFilePath, "Unexpected file in dropbox folder.")
			# move file to review folder
			# first create subdirectory, if not existing
			targetDir = reviewDir + "/" + "/".join(pathParts)
			if not os.path.exists(targetDir):
				os.makedirs(targetDir)
			shutil.move(dropboxDir + '/' + newFilePath, reviewDir + "/" + newFilePath)
			retcode = 1
			continue
		
		# skip files of current day
		# split filename at _
		tokens = nf.split('_')
		if len(tokens) == 3 and len(tokens[1])==10:
			fileDate = datetime.datetime.strptime(tokens[1], '%Y-%m-%d')
			todaysDate = datetime.datetime.today()
			if fileDate.date() == todaysDate.date():
				continue # ignore file in dropbox
		
		# apply entry checks
		if not projectConfig.entryCheckPassedForFile(dropboxDir, newFilePath, matchingEf):
			printError("Entry check failed for file '{}'.".format(newFilePath))
			# move file to review folder
			# first create subdirectory, if not existing
			targetDir = reviewDir + "/" + "/".join(pathParts)
			if not os.path.exists(targetDir):
				os.makedirs(targetDir)
			shutil.move(dropboxDir + '/' + newFilePath, reviewDir + "/" + newFilePath)
			retcode = 1
			continue


		# TODO : content checks

		# all successful, move to archive
		print("Archiving file '{}'.".format(newFilePath))
		process_log('Archiving', newFilePath)
		# move file to archive folder
		# first create subdirectory, if not existing
		targetDir = archiveDir + "/" + "/".join(pathParts)
		if not os.path.exists(targetDir):
			os.makedirs(targetDir)
		shutil.move(dropboxDir + '/' + newFilePath, archiveDir + "/" + newFilePath)


# ---- check for missing files ----

if retcode != 0:
	print("Errors:")
	errLogFilename = logDir + "/errors_{}".format(Logger.TIME_STAMP)
	if os.path.exists(errLogFilename):
		fobj = open(errLogFilename, 'r')
		print(fobj.read())
		del fobj

retCodeMissingFiles, missingFileCount = checkForMissingFiles(archiveDir, projectConfig)
if retCodeMissingFiles == 1:
	retcode = retCodeMissingFiles
	# print list of missing files as error to log
	print("\nList of missing files:")
	if os.path.exists(logDir + "/missing"):
		fobj = open(logDir + "/missing")
		print(fobj.read())
		del fobj
	

print("\nRemaining files:")

# if review directory is not empty, print list of open files
revFileCount = 0
for root, dirs, files in os.walk(reviewDir, topdown=False):
	rootStr = root.replace('\\', '/') # windows fix
	pathParts = rootStr.split('/') # split into component
	pathParts = pathParts[len(dropboxPathParts):] # keep only path parts below toplevel dir
	for f in files:
		relFile = "/".join(pathParts) + "/" + f
		print(relFile)
		revFileCount = revFileCount + 1

print("")

if revFileCount != 0:
	print("There are {} files remaining in the review directory".format(revFileCount))
	retcode = 1

if missingFileCount != 0:
	print("There are {} missing files".format(missingFileCount))
	retcode = 1

# return signaling caller the result: 0 = success, 1 = have error(s)
exit(retcode)
