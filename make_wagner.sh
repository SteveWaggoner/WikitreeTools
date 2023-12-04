#!/bin/bash

PREV_DATE=${PREV_DATE:-`ls data_20* -d -1 | tr -d "/" | cut -d_ -f2- | tr _ "-" | sort | tail -n2 | head -n1`}
DATE=`ls data_20* -d -1 | tr -d "/" | cut -d_ -f2- | tr _ "-" | sort | tail -n1`

echo "Date: $DATE, Prev Date: $PREV_DATE"

if ! [ -f Wagner_Lineages-$PREV_DATE.txt ]; then
    time ./get_lineages.py Wagner Wagoner Waggoner Waggener Wagener --exact 2 --date $PREV_DATE
fi
time ./get_lineages.py Wagner Wagoner Waggoner Waggener Wagener "Van Wagner" "Van Wagener" --exact 2 --date $DATE --last-update $PREV_DATE

