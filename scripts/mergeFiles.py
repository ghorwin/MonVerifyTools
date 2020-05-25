#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Developed at IBK, TU Dresden, Germany
#
# Authors: Andreas Nicolai <andreas.nicolai -at- tu-dresden[dot]de>
#
# License: BSD(2) License, see LICENSE file

import os
import os.path
import argparse

# command line arguments
parser = argparse.ArgumentParser(description="Merges files with same date")
parser.add_argument('baseName', nargs='?', help="Basename (including path but without time and extension) to file to merge, for example '/path/to/review/WsIBK_2019-09-10'.")

args = parser.parse_args()

if args.baseName == None:
	print("Invalid syntax, use --help")
	exit(1)

basename = args.baseName.replace("\\","/")
pathParts  = basename.split("/")
pathTokens = os.path.dirname(basename)

prefix = pathParts[-1]

files = os.listdir(pathTokens)
mergeFiles = []
for f in files:
	if len(f) > 3 and f[-3:] == 'csv' and prefix in f and f.index(prefix) == 0:
		mergeFiles.append(f)
		
if len(mergeFiles) == 0:
	print("No files with given prefix '{}' in directory.".format(prefix))
	exit(1)
	
fileContent = []

# now process all files in sorted manner and store as tuples in fileContent
for f in sorted(mergeFiles):
	print("Merging file '{}'".format(f))
	f = pathTokens + "/" + f
	try:
		with open(f, 'r') as fobj:
			lines = fobj.readlines()
			# skip header lines
			headerLineCount = 0
			for i in range(len(lines)):
				if len(lines[i].strip()) == 0:
					headerLineCount = i+1
					break
			# copy header of first file to be read
			if len(fileContent) == 0:
				fileContent = lines[0:headerLineCount]
			# now append data section
			fileContent += lines[headerLineCount:]
		fobj.close()
		del fobj
	except:
		print("Error reading file {}".format(f))
		exit(0)

# rename original files
for f in sorted(mergeFiles):
	f = pathTokens + "/" + f
	os.rename(f, f+".orig")

# finally write file
with open(args.baseName+"_00-00-00.csv", 'w') as fobj:
	fobj.writeLines( fileContent ) # original line 
fobj.close()
del fobj

# and remove original files
#for f in sorted(mergeFiles):
#f = pathTokens + "/" + f
#	os.remove(f+".orig")
