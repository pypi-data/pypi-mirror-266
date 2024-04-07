#! /bin/sh
#set -ex


D=src/fredquery

for i in fredcategories.py \
         fredreleases.py \
         fredseries.py \
         fredplot.py \
         fredplotseries.py \
         fredsources.py \
         fredtags.py; do
     echo
     f=$(echo $i | cut -f1 -d.)
     echo '##'
     echo "## $f"
     echo '##'
     python $D/$i -h
     echo
done | while read line; do
    echo "$line<br/>"
done | sed 's/[.]py//'

