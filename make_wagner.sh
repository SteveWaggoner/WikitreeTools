#!/bin/bash

LAST_UPDATE=`ls data_20* -d -1 | tr -d "/" | cut -d_ -f2- | tr _ "-" | sort | tail -n2 | head -n1`
DATE=`ls data_20* -d -1 | tr -d "/" | cut -d_ -f2- | tr _ "-" | sort | tail -n1`

if ! [ -f Wagner_Lineages-$LAST_UPDATE.txt ]; then
    time ./get_lineages.py Wagner Wagoner Waggoner Waggener Wagener --exact 2 --date $LAST_UPDATE
fi
time ./get_lineages.py Wagner Wagoner Waggoner Waggener Wagener --exact 2 --date $DATE  --last-update $LAST_UPDATE

