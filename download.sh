#!/bin/bash

echo pw:

sftp waggoner1719@apps.wikitree.com <<EOT
cd dumps
get dump_people_users.csv.gz
get dump_categories.csv.gz
get dump_people_marriages.csv.gz
bye
EOT

DATE=`date +%Y_%m_%d`

mkdir data_$DATE
mv dump*gz data_$DATE -v


