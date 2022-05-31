#!/bin/bash

LAST_UPDATE_FILE=Wagner_Lineages-2022-05-29.txt
DATE=`date +%Y-%m-%d`

time ./get_lineages.py Wagner Wagoner Waggoner Waggener --exact 2 --last-update-file $LAST_UPDATE_FILE | sed -r '/^\s*$/d' > Wagner_Lineages-$DATE.txt

#time ./get_lineages.py Wagner Wagoner Waggoner Waggener --exact 2 --last-update-file $LAST_UPDATE_FILE --ignore-dna-cache | sed -r '/^\s*$/d' > Wagner_Lineages-$DATE.txt

#time ./get_lineages.py Wagner Wagoner Waggoner Waggener --exact 2 --test > Wagner_Lineages-$DATE.txt
#time ./get_lineages.py Wagner Wagoner Waggoner Waggener Wagener --exact 2 --ignore-dna-cache > Wagner_Lineages-$DATE.txt

#time ./get_lineages.py Wagner Wagoner Waggoner Waggener --exact 2 --min-gen-dna-exact 0 > Wagner_Lineages-$DATE.txt
