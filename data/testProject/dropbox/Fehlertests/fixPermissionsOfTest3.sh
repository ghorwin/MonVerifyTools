#!/bin/bash

echo 'changing permissions of Test_2016-03-04_00-00-03.csv to 500 and setting owner to root:root'
sudo chmod 600 Test_2016-03-04_00-00-03.csv
sudo chown root:root Test_2016-03-04_00-00-03.csv
