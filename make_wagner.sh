#!/bin/bash

DATE=`date +%Y-%m-%d`
time ./get_lineages.py Wagner Wagoner Waggoner Waggener --exact 2 > Wagner_Lineages-$DATE.txt

