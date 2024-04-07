#¡ sh
set -ex

D='src/fredquery'
cd $D

python fredplot.py --categoryid 32455
# fredplot --categoryid 32455

python fredplot.py --releaseid 365
# fredplot --releaseid 365

python fredplot.py  --sourceid 69
# fredplot  --sourceid 69

python fredplot.py --tagname inflation
# fredplot --tagname inflation
# python fredplot.py --tagname core

