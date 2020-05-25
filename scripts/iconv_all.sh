#!/bin/bash


# Syntax: iconv_all.sh

#FROM_ENCODING=$1
#if [ -n "$1" ]; then
#	echo "Converting from $1"
#else
#	echo "Converting from ISO_8859-15"
#	FROM_ENCODING='ISO_8859-15'
#fi

for f in *.csv
do
	# check if file is already in utf-8 encoding
	FILEINFO=$(file -bi $f)
	#echo $FILEINFO
	CHARSET=$(echo $FILEINFO | cut -d'=' -f2)
	echo "Converting from '$CHARSET'"
	mv $f $f.orig &&
	iconv -f $CHARSET -t UTF-8 -o $f $f.orig &&
	rm $f.orig
done
