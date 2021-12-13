#!/bin/bash

DATE=`date +%Y-%m-%d`
time ./get_lineages.py Wagner Wagoner Waggoner Waggener --exact 2 > Wagner_Lineages-$DATE.txt
#time ./get_lineages.py Wagner Wagoner Waggoner Waggener Wagener --exact 2 --ignore-dna-cache > Wagner_Lineages-$DATE.txt

