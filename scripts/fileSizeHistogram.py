#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import os
import argparse

# command line arguments
parser = argparse.ArgumentParser(description="Generates a histogramm of file sizes")
parser.add_argument('projectDir', nargs='?', help='Directory to process.', default=os.getcwd())

args = parser.parse_args()

files = os.listdir(args.projectDir)

fsizes = []
for f in files:
	if len(f) > 3 and f[-3:] == 'csv':
		fileSize = os.path.getsize(os.path.join(args.projectDir,f)) 
		fsizes.append(fileSize)

mi = min(fsizes)
ma = max(fsizes)
	
plt.hist(fsizes, bins=30)

fname = "matplotlib_filesize_histogram.svg"
plt.savefig(fname)
print("Min: {}".format(mi))
print("Max: {}".format(ma))
print("Histogram file: {}".format(os.path.join(os.getcwd(),fname)) )
