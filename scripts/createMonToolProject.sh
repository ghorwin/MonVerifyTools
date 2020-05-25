#!/bin/bash


# Syntax:
#
# > createMonToolProject.sh <group of project members> <group of project data clients> <project root>
#
# Example:
#
# > createMonToolProject.sh GrpMessprojekt1Manager GrpMessprojekt1Client Messprojekt1Service /srv/data/MessProject1
#
# Groups must exist!

if [ "$1" == "--help" ]
  then
    echo "Syntax:"
    echo "> createMonToolProject.sh <group of project managers> <group of project data clients> <project service user> <project root path>"
    exit 1
fi

if [ $# -lt 4 ]
  then
    echo "Missing arguments. Invalid syntax (use --help)."
    exit 1
fi

# create directory structure
if [ ! -d "$4" ]
then
    echo "Creating project in '$4'"
    mkdir "$4"
fi &&

if [ ! -d "$4/archive" ]; then mkdir "$4/archive"; fi &&
if [ ! -d "$4/bypass" ]; then mkdir "$4/bypass"; fi &&
if [ ! -d "$4/config" ]; then mkdir "$4/config"; fi &&
if [ ! -d "$4/dropbox" ]; then mkdir "$4/dropbox"; fi &&
if [ ! -d "$4/log" ]; then mkdir "$4/log"; fi &&
if [ ! -d "$4/review" ]; then mkdir "$4/review"; fi &&
if [ ! -d "$4/status" ]; then mkdir "$4/status"; fi &&

# restrict permissions

chmod -R 750 "$4" &&

# allow write access for group in config, logs and review

chmod 770 "$4/config" &&
chmod 770 "$4/log" &&
chmod 770 "$4/review" &&

# allow write access for group in dropbox (but remove group-read)

chmod 730 "$4/dropbox" &&

# set group ownership

chown -R $3:$1 "$4" &&

# set client group ownership 

chown $3:$2 "$4" &&
chown $3:$2 "$4/dropbox"


exit 0
