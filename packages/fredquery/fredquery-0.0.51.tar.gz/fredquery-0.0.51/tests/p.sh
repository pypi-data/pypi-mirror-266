#¡ sh
set -ex

D='src/fredquery'
cd $D

python fredcategories.py --categories --file /tmp/categories.csv 
python fredcategories.py --categories --showcategories
python fredcategories.py --series --categoryid 32455 --file /tmp/cseries32455.csv 
python fredcategories.py --series --categoryid 32455 --showseries
python fredcategories.py --observations --directory /tmp --categoryid 32455
#    fredcategories.py --observations --directory /tmp --seriesid
set +x
ls /private/tmp/[0-9A-Z]*.csv | wc -l
rm /private/tmp/[0-9A-Z]*.csv > /dev/null
set -x


python fredreleases.py --releases --file /tmp/releases.csv
python fredreleases.py --releases --showreleases
python fredreleases.py --series --releaseid 365 --file /tmp/rseries365.csv
python fredreleases.py --series --releaseid 365 --showseries
python fredreleases.py --observations --directory /tmp --releaseid 9
set +x
ls /private/tmp/[0-9A-Z]*.csv | wc -l
rm /private/tmp/[0-9A-Z]*.csv >/dev/null
set -x

python fredseries.py --series     --seriesid AKIRPD --file /tmp/AKIRPD_series.csv
python fredseries.py --observations --seriesid AKIRPD --directory /tmp
python fredseries.py --categories --seriesid AKIRPD --file /tmp/AKIRPD_categories.csv
python fredseries.py --releases   --seriesid AKIRPD --file /tmp/AKIRPD_releases.csv
python fredseries.py --sources    --seriesid AKIRPD --file /tmp/AKIRPD_sources.csv
python fredseries.py --tags       --seriesid AKIRPD --file /tmp/AKIRPD_tags.csv
python fredseries.py --updates    --seriesid AKIRPD --file /tmp/AKIRPD_updates.csv
set +x
ls /private/tmp/[0-9A-Z]*.csv | wc -l
rm /private/tmp/[0-9A-Z]*.csv >/dev/null
set -x

python fredsources.py --sources  --file /tmp/sources.csv
python fredsources.py --sources  --showsources
python fredsources.py --releases --sourceid 57 --file /tmp/sreleases57.csv
python fredsources.py --releases --sourceid 57 --showreleases
python fredsources.py --series --sourceid 57 --file /tmp/Source57.csv
python fredsources.py --series --sourceid 57 --showseries
python fredsources.py --observations --sourceid 57 --directory /tmp
set +x
ls /private/tmp/[0-9A-Z]*.csv | wc -l
rm /private/tmp/[0-9A-Z]*.csv >/dev/null
set -x


python fredtags.py --tags   --file /tmp/tags.csv
python fredtags.py --tags   --showtags
python fredtags.py --series --tagname inflation --file /tmp/tseriesinflation.csv
python fredtags.py --series --tagname inflation --showseries
python fredtags.py --observations --tagname inflation --directory /tmp
set +x
ls /private/tmp/[0-9A-Z]*.csv | wc -l
rm /private/tmp/[0-9A-Z]*.csv >/dev/null
set -x

