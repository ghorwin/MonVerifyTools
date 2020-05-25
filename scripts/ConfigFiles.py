#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File contains the class ConfigFiles that encapsulate the various configuration files:
- .exp
- .ref
- .phy
"""


import json
import re
import os
import platform
import subprocess
from datetime import datetime

from Logger import error_log
from print_funcs import *

TEST_GROUPS = [
    'IBK_Mon_DHT22',
    'IBK_Mon_1Wire',
    'IBK_Mon_WinStat',
    'IBK_Mon_conCom',
    'IBK_TimeSeries',
    'IBK_EventData',
    'IBK_Custom' ]

class ConfigFiles:
	"""Class to read config files.

	Also provides functions to check for bypass-Rules and perform the basic entry checks.
	"""
	def __init__(self):
		self.configFilePath = ""
		self.expectedFiles = dict() # dictionary for expected files, key = filename, value = array of attributes
		self.bypassRules = []
		self.headerDefinitions = dict()

	def checkReferencedFile(self, name, refFile, fileType):
		"""Checks, if a file referenced in the exp-file exists.

		Arguments
		---------
		name
		    File prefix of a definition line in the exp file
		refFile
		    Path to referenced file
		fileType
		    Description of type of referenced file (used in error message)

		Raises
		------
		RuntimeError
		    Exception when an error in the referenced file definition is encountered.
		"""
		# only check if file is actually given
		if len(refFile) > 0:
			if not os.path.exists(self.configFilePath + "/" + refFile):
				raise RuntimeError("Error in definition of file '{}': missing {} '{}'"
				                   .format(name, fileType, self.configFilePath + "/" + refFile))
			relPath = os.path.relpath(self.configFilePath + "/" + refFile, self.configFilePath)
			if os.path.isabs(relPath) or relPath.find('..') != -1:
				raise RuntimeError("Error in definition of file '{}': path to {} '{}' leaves config dir."
				                   .format(name, fileType, self.configFilePath + "/" + refFile))


	def readExp(self, expFilePath):
		"""Reads given expectation file.

		Raises an exception of syntax is invalid or file content is not conforming to standard.

		Arguments
		---------
		expFilePath
		    Full path to .exp file to read

		Raises
		------
		RuntimeError
		    Exception when critical error in config file is encountered.

		"""
		pparts = expFilePath.split("/")
		self.configFilePath = "/".join(pparts[:-1])
		self.expectedFiles = dict()
		self.bypassRules = []
		with open(expFilePath, 'r') as json_file:
			try:
				data = json.load(json_file)
			except ValueError as e:
				raise RuntimeError("Error parsing JSON content from file '{}'.".format(expFilePath))
			if not 'ExpectedFiles' in data:
				raise RuntimeError("Missing mandatory 'ExpectedFiles' array in exp file '{}'.".format(expFilePath))
			for expectedFile in data['ExpectedFiles']:
				if len(expectedFile) != 10:
					raise RuntimeError("Invalid expected file definition: {}".format(expectedFile))

				name = expectedFile[0]
				# check that name is not already given
				if name in self.expectedFiles:
					raise RuntimeError("File '{}' defined twice.".format(name))
				if name[-1] != '_':
					raise RuntimeError("Malformed file name '{}', expected trailing _ character".format(name))

				# set defaults for not specified values
				if expectedFile[1] == "":
					expectedFile[1] = "IBK_TimeSeries"

				# TODO : Additional checks for content of expected file definition, i.e. negative file sizes, 
				#        negative line counts etc.

				# check test groups keyword
				if expectedFile[1] not in TEST_GROUPS:
					raise RuntimeError("Error in definition of file '{}': unknown/undefined test group '{}'"
					                   .format(name, expectedFile[1]))
				# check for existance of referenced files and wether file path's for ref or phy file go outside 
				# the config directory
				self.checkReferencedFile(name, expectedFile[6], 'header reference file')
				self.checkReferencedFile(name, expectedFile[7], 'content test definition file')
				
				# check for valid numbers for toleranzes
				if expectedFile[5] < 0:
					raise RuntimeError("Error in definition of file '{}': negative value for tolerance '{}' is not allowed"
					                   .format(name, expectedFile[9]))
				if expectedFile[9] < 0:
					raise RuntimeError("Error in definition of file '{}': negative value for tolerance '{}' is not allowed"
					                   .format(name, expectedFile[9]))
				

				# store file definition
				self.expectedFiles[name] = expectedFile
				#print("Registering expected file pattern '{}'".format(name))
				
			if 'BypassFiles' in data:
				for bypassRule in data['BypassFiles']:
					self.bypassRules.append( bypassRule )


	def bypassRuleAppliesToFile(self, fname):
		"""Tests, if the filename (full path relative to dropbox folder)
		is matched by any of the bypass rules.

		Matching is done by either:

		- testing if fname begins the either of the bypass file names
		- a regexp-search matches the fname

		Example:

		'TestHaus/dummy_' matches a file 'TestHaus/dummy_2019-09-20_10:00:00.csv'
		but does not match 'TestHaus2/dummy_2019-09-20_10:00:00.csv'.

		Arguments
		---------
		fname
		    File path relative to dropbox directory, for example 'Haus1/Wg2/dummy_'

		Returns True, if a rule applied, or False if no rule exists for this file.
		"""

		for bypassRule in self.bypassRules:
			if fname.find(bypassRule) == 0:
				return True
			match = re.search(bypassRule, fname)
			if match:
				return True

		return False


	def entryCheckPassedForFile(self, dropboxDir, fname, ef):
		"""Tests, if the filename (full path relative to dropbox folder)
		passes all entry checks.

		Note: Entry checks are only those that do not require reading the
		content of the entire file.

		Arguments
		---------
		
		fname
		    File path relative to dropbox directory
		ef
		    ExpectedFile data definition array

		Returns True, if all tests have passed successfully.
		"""

		fnameFixed = fname.replace('\\', '/') # windows fix
		fnameParts = fnameFixed.split('/')
		filename = fnameParts[-1]
		print("Processing file '{}'".format(filename))

		# file name check - check for correct number of _ and - characters
		tokens = filename.split('_')
		checkFailed = False
		if len(tokens) != 3:
			checkFailed = True
		else:
			dstring = tokens[1]
			tstring = tokens[2]
			# date stamp is of format 'yyyy-mm-dd'
			if len(dstring) != 10 or dstring[4] != '-' or dstring[7] != '-':
				checkFailed = True
			# time stamp is of format 'HH-MM-ss.csv'
			if len(tstring) != 12 or tstring[2] != '-' or tstring[5] != '-':
				checkFailed = True

		if checkFailed:
			printError("Invalid file name '{}'".format(fname))
			error_log('BadFilename', fname, '')
			return False
		
		# check for 00-00-00 time stamp
		# TODO : adjust this if sub-daily samples are expected
		if tstring != "00-00-00.csv":
			printError("Invalid time stamp of file '{}', expected 00-00-00".format(fname))
			error_log('BadFilename', fname, "Invalid time stamp of file '{}', expected 00-00-00".format(fname))
			return False
			

		# determine test group
		testGroup = ef[1]

		# if test group is IBK_Custom, we just accept the file as-is
		if testGroup == "IBK_Custom":
			return True

		fullPath = dropboxDir + '/' + fname
		
		# first check if file is empty
		fileSize = os.path.getsize(fullPath) 
		if fileSize == 0:
			printError("File is empty.\n")
			error_log('EmptyFile', fname, "")
			return False

		# test for correct header (done in all test groups), except header file definition is missing
		if ef[6] != "":
			if not ef[6] in self.headerDefinitions:
				# try to read header file
				try:
					headerRefFile = self.configFilePath + "/" + ef[6]
					with open(headerRefFile, 'r') as f:
						lines = f.readlines()
					lines = [l.strip() for l in lines] # remove trailing /r and /n chars
					self.headerDefinitions[ef[6]] = lines
				except IOError as e:
					printError("Error reading header reference file '{}'.".format(headerRefFile))
					error_log('Critical', "Error reading header reference file '{}'.".format(headerRefFile), '')
					exit(1)

			headerReference = self.headerDefinitions[ef[6]]
			try:
				# now read all lines of the headerReference from file and compare line by line
				with open(fullPath, 'r') as f:
					errorLineCount = []
					errorLines = []
					expectedLines = []
					lineCount = 0
					for refLine in headerReference:
						lineCount = lineCount + 1
						line = f.readline().strip() # remove trailing /r and /n chars
						if line != refLine:
							expectedLines.append(refLine)
							errorLines.append(line)
							errorLineCount.append(lineCount)
					if len(errorLineCount) != 0:
						errorStrings = ""
						for i in range(len(errorLineCount)):
							errorStrings = errorStrings + "{:2d}: ".format(errorLineCount[i]) + expectedLines[i] + "\n" + "  : " + errorLines[i] + "\n"
						printError("Header line mismatch:\n" + errorStrings)
						error_log('InvalidHeader', fname, "Header line mismatch:\n" + errorStrings)
						return False
					
			except IOError as e:
				printError("Error reading data file '{}'.".format(fname))
				# get ls output on Linux
				permissions = ""
				if platform.system() == "Linux":
					proc = subprocess.Popen(['ls','-l',fullPath], stdout=subprocess.PIPE)
					tmp = proc.stdout.read()
					permissions = tmp[:tmp.find('/')]
				error_log('AccessDenied', fname, permissions)
				return False


		# file size check, only if expected file size is given; not for testGroup "IBK_Mon_WinStat"
		# Note: file size check is done *after* header check - so if header is correct and file size still differs,
		#       the reason must be in the data section
		expFileSize = ef[2]
		if testGroup != "IBK_Mon_WinStat" and testGroup != "IBK_EventData":
			expFileSizeMin = expFileSize # min and exact size are defined by the same parameter
			expFileSizeMax = ef[3]

			# exact check only for support level 1
			if testGroup == "IBK_Mon_1Wire":
				if (expFileSize != 0 and expFileSize != fileSize):
					printError("Mismatching file size, expected {} bytes, got {} bytes.".format(expFileSize, fileSize))
					error_log('FileSizeMismatch', fname, "Mismatching file size, expected {} bytes, got {} bytes.".format(expFileSize, fileSize))
					return False
			else:
				if (expFileSizeMax != 0 and fileSize > expFileSizeMax) or (expFileSizeMin != 0 and fileSize < expFileSizeMin):
					printError("File size {} bytes is not in expected size range [{}..{}] bytes."
				               .format(fileSize, expFileSizeMin, expFileSizeMax))
					error_log('FileSizeMismatch', fname, "File size {} bytes is not in expected size range [{}..{}] bytes."
				              .format(fileSize, expFileSizeMin, expFileSizeMax))
					return False


		# data line and interval checks
		if testGroup != "IBK_EventData":
			# read data file
			try:
				with open(fullPath, 'r') as f:
					lines = f.readlines()
					lines = [l.strip('\r\n') for l in lines] # remove trailing /r and /n chars, but keep tabs
			except IOError as e:
				printError("Error reading data file '{}'.".format(fname))
				error_log('AccessDenied', fname, '')
				return False
			
			# read over header section and extract SensorID line
			blankLineIndex = 0
			sensorTokens = []
			while blankLineIndex < len(lines) and lines[blankLineIndex] != "":
				if lines[blankLineIndex].find("SensorID") == 0:
					sensorTokens = lines[blankLineIndex].split(',')
				blankLineIndex = blankLineIndex + 1
			if blankLineIndex == len(lines):
				printError("Data section missing in file '{}'.".format(fname))
				error_log('SampleCountMismatch', fname, 'Data section missing in file.')
				return False

			# read data section, extract samples and compute time difference between samples
			sampleCount = 0
			lastTimeStamp = None
			for i in range(blankLineIndex+1, len(lines)):
				line = lines[i]
				tokens = line.split(',')
				if len(tokens) != len(sensorTokens):
					printError("Data section in file '{}' contains line '{}' with mismatching column count (expected {}, got {} columns)"
					           .format(fname, line, len(sensorTokens), len(tokens)))
					error_log('ColumnCountMismatch', fname, "Data section in file '{}' contains line '{}' with mismatching column count (expected {}, got {} columns)"
					           .format(fname, line, len(sensorTokens), len(tokens)))
					return False
				sampleCount = sampleCount + 1
				# now parse time stamp
				try:
					ts = datetime.strptime(tokens[0], "%Y-%m-%d %H:%M:%S")
				except ValueError:
					printError("Data section in file '{}' contains invalid time stamp format '{}'"
					           .format(fname, tokens[0]))
					error_log('InvalidTimeStamp', fname, "Data section in file '{}' contains invalid time stamp format '{}'"
					           .format(fname, tokens[0]))
					return False
				
				if lastTimeStamp != None:
					timeDiff = ts-lastTimeStamp
					timeDiffSec = timeDiff.total_seconds()
					# if we have a sample interval given, and the test is enabled, perform test
					if ef[8] > 0:
						minIntervalLength = ef[8] - ef[9]
						maxIntervalLength = ef[8] + ef[9]
						# if we have a toleranz > 0, compare with toleranz band
						if timeDiffSec < minIntervalLength or timeDiffSec > maxIntervalLength:
							if ef[9] == 0:
								printError("Sampling interval before time stamp '{}' was {} s, but expected was {} s"
									       .format(tokens[0], timeDiffSec, ef[8]))
								error_log('InvalidSamplingInterval', fname, "Sampling interval before time stamp '{}' was {} s, but expected was {} s"
									       .format(tokens[0], timeDiffSec, ef[8]))
							else:
								printError("Sampling interval before time stamp '{}' was {} s, but was expected in range [{},{}] s"
									       .format(tokens[0], timeDiffSec, minIntervalLength, maxIntervalLength))
								error_log('InvalidSamplingInterval', fname, "Sampling interval before time stamp '{}' was {} s, but was expected in range [{},{}] s"
									       .format(tokens[0], timeDiffSec, minIntervalLength, maxIntervalLength))
							return False
				lastTimeStamp = ts
			
			# check for sample count
			if testGroup != "IBK_Mon_WinStat":
				expLineCount = ef[4]
				if expLineCount != 0:
					expLineMin = expLineCount - ef[5]
					expLineMax = expLineCount + ef[5]
					if sampleCount < expLineMin or sampleCount > expLineMax:
						printError("Expected {} samples, got {}.".format(expLineCount, sampleCount))
						error_log('SampleCountMismatch', fname, "Expected {} samples, got {}.".format(expLineCount, sampleCount))
						return False

		return True
