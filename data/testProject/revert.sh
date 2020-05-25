#!/bin/bash

rm -rf archive/Fehlertests
rm -rf bypass/Fehlertests
rm -rf review/Fehlertests
rm -rf review/TestHaus

rm log/errors_*
rm log/processed
rm log/missing

git checkout -- dropbox/Fehlertests
