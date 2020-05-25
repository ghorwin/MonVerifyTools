# Scripts

This directory contains the actual scripts:

- `MonVerifyTool.py` the actual script to process the directory structure, usually to be executed automatically (e.g. daily)
- `mergeFiles.py` utility script to merge two data files that were split due to reboot of data logger/client
- `fileSizeHistogram.py` utility script to generate a histogram of file sizes from a set of data files in a directory, can be useful to determine meaningful lower and upper limits for expected file sizes
- `createMonToolProject.sh` shell script to create a directory structure and assign suitable permissions and group/user ownership to get some security into the data acquisition process

