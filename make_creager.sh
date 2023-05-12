#!/bin/bash

LAST_UPDATE=`ls data_20* -d -1 | tr -d "/" | cut -d_ -f2- | tr _ "-" | sort | tail -n2 | head -n1`
DATE=`ls data_20* -d -1 | tr -d "/" | cut -d_ -f2- | tr _ "-" | sort | tail -n1`

time ./get_lineages.py Creager Creiger Kreiger Creeger Kriger Crager --min-gen 2 --exact 1 --date $LAST_UPDATE  || exit 1
time ./get_lineages.py Creager Creiger Kreiger Creeger Kriger Crager --min-gen 2 --exact 1 --date $DATE  --last-update $LAST_UPDATE || exit 1

