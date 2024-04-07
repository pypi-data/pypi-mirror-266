#! /bin/sh
set -ex

python src/fredquery/fredcategories.py --categories --showcategories
python src/fredquery/fredcategories.py --series --categoryid 32145 --showseries
python src/fredquery/fredreleases.py --releases --showreleases
python src/fredquery/fredreleases.py --series --releaseid 53 --showseries
python src/fredquery/fredsources.py --sources --showsources
python src/fredquery/fredsources.py --series --sourceid 48 --showseries
python src/fredquery/fredtags.py --tags --showtags
python src/fredquery/fredtags.py --series --tagname gdp --showseries
