#!/bin/bash

LAST_UPDATE=2022-05-30
DATE=2022-06-05

#time ./get_lineages.py Wagner Wagoner Waggoner Waggener  --exact 2 --date $LAST_UPDATE
time ./get_lineages.py Wagner Wagoner Waggoner Waggener  --exact 2 --date $DATE        --last-update $LAST_UPDATE

