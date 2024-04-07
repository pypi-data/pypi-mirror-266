#! env python

# return information on releases or their sries
#

import os
import sys
import argparse
import re
import time
import urllib.request
import xml
from xml.etree import ElementTree as ET
import webbrowser

try:
    from fredquery import query
    from fredquery import aa2html
    from fredquery import xmlstr2aa
except ImportError as e:
    import query
    import aa2html
    import xmlstr2aa

class FREDReleases():

    def __init__(self):
        """ FREDReleases

        collects categories, their releases, series for the release
        and observations(timeseries data) for the series
        """
        # fred releases
        self.rurl = 'https://api.stlouisfed.org/fred/releases'
        self.releasesdict = {}
        # fred release tables
        self.rturl = 'https://api.stlouisfed.org/fred/release/tables'
        self.releasetabledict = {}
        # series for a release id
        self.rsurl = 'https://api.stlouisfed.org/fred/release/series'
        self.seriesdict = {}
        self.surl = 'https://api.stlouisfed.org/fred/series'
        # observations for a series id
        self.sourl = 'https://api.stlouisfed.org/fred/series/observations'
        # url for getting a FRED api_key
        self.kurl = 'https://fred.stlouisfed.org/docs/api/api_key.html'
        # probably a bad idea to put your real api_key in a report
        self.rapi_key = '$FRED_API_KEY'
        if 'FRED_API_KEY' in os.environ:
            self.api_key = os.environ['FRED_API_KEY']
        else:
            print('FRED api_key required: %s' % (self.kurl), file=sys.stderr)
            print('assign this key to FRED_API_KEY env variable',
                                  file=sys.stderr)
            sys.exit()
        self.npages  = 7
        self.verbose = True
        self.rid     = None
        self.sid     = None
        self.observationsdict = {}

        self.uq = query._URLQuery()
        self.ah = aa2html._AA2HTML()
        self.xa = xmlstr2aa._XMLStr2AA()


    def reportobservation(self, id, units, obsa, odir):
        """ reportobservation(id, obsa, odir)

        report observations for a series_id
        id - series_id
        obsa - list of observations for a series_id
        odir - directory for storing observations
        """
        # remove spaces and .
        units = re.sub('[ .]', '', units)
        fn = '%s_%s.csv' % (id, units)
        fpath = os.path.join(odir, fn)
        with open(fpath, 'w') as fp:
            for row in obsa:
                rw = "','".join(row)
                print("'%s'" % (rw), file=fp )

    def getandreportobservations(self, odir):
        """ getandreportobservations()

        incrementally get and store observation data for all
        series collected
        observation = time series data
        """
        for rid in self.seriesdict.keys():
            aa = self.seriesdict[rid]
            assert aa[0][8] == 'units'
            keys = aa[0]
            for i in range(1, len(aa) ):
                a = aa[i]
                id = a[0]
                units = a[8]
                url = '%s?series_id=%s&api_key=%s' % (self.sourl, id,
                   self.api_key)
                resp = self.uq.query(url)
                rstr = resp.read().decode('utf-8')
                obsa = self.xa.xmlstr2aa(rstr)
                self.reportobservation(id, units, obsa, odir)
                time.sleep(1)

    def returnseriesforid(self, id):
        if id in self.seriesdict:
            return self.seriesdict[id]
        return None

    def showseriesforid(self, id):
        """ showseriesforid(d)

        display series list for a release_id in your browser
        id release_id or series_id
        """
        aa = self.returnseriesforid(id)
        if aa == None:
            print('no data for %s' % (id), file=sys.stderr)
            return
        self.ah.aashow(self.seriesdict[id], 'Release %s series' % id)

    def reportseriesdorid(self, id, ofp):
        """ reportseriesdorid(id, ofp)

        report for a release_id or series_id 
        id = release_id or series_id
        ofp - file pointer to which to write
        """
        aa = self.returnseriesforid(id)
        if aa == None:
            return
        for a in aa:
            row = "','".join(a)
            print("'%s'" % (row), file=ofp)

    def getseriesforrid(self, rid):
        """ getseriesforrid(rid)

        get all series for a release_id
        rid - release_id - required
        """
        if not rid:
            print('getseriesforrid: rid required', file=stderr)
            sys.exit(1)
        self.rid = rid
        url = '%s?release_id=%s&api_key=%s' % (self.rsurl,
                                           rid, self.api_key)
        resp = self.uq.query(url)
        rstr = resp.read().decode('utf-8')
        aa = self.xa.xmlstr2aa(rstr)
        if len(aa) == 0:
            print('getseriesforrid(rid): no data' % (sid), file=sys.stderr)
            return
        assert aa[0][3] == 'title'
        raa = []
        raa.append(aa[0])
        raa[0].append('url')
        for i in range(1, len(aa) ):
            if 'DISCONTINUED' in aa[i][3]:
                continue
            raa.append(aa[i])
            url = '%s?series_id=%s&api_key=FRED_API_KEY' % (self.rsurl,
                     aa[i][0])
            raa[-1].append(url)
        self.seriesdict[rid] = raa

    def getseries(self):
        """ getseries()

        get all series for all releases collected
        """
        # a series is associated with a release
        for rid in self.releasesdict.keys():
            nurl = '%s?release_id=%s' % (self.rsurl, rid)
            # trying to avoid dups
            if rid not in self.seriesdict:
                self.getseriesforrid(rid)
                time.sleep(1)

    def returnreleases(self):
        # silly but helps me avoid having to remember the one key
        raa = []
        for k in self.releasesdict.keys():
            raa.extend(self.releasesdict[k])
        return raa

    def showreleases(self):
        """ showreleases()

        show stlouisfed.org FRED releases as a table in your browser
        """
        aa = self.returnreleases()
        self.ah.aashow(aa, 'FRED Releases')

    def reportreleases(self, ofp):
        """reportreleases(ofp)

        report data on all Dreleases collected
        ofp - file pointer to which to write
        """
        if not ofp: ofp=sys.stdout
        keys = []
        aa = self.returnreleases()
        for i in range(len(aa) ):
            rowa = aa[i]
            row  = "','".join(rowa)
            print("'%s'" % (row), file=ofp )

    def getreleases(self):
        """ getreleases()

        collect all releases
        """
        url = '%s?api_key=%s' % (self.rurl, self.api_key)
        resp = self.uq.query(url)
        rstr = resp.read().decode('utf-8')
        #  print(rstr)
        aa = self.xa.xmlstr2aa(rstr)
        aa[0].append('url')
        for i in range(1, len(aa) ):
            id = aa[i][0]
            url = '%s?series_id=%s&api_key=FRED_API_KEY' % (self.rsurl, id)
            aa[i].append(url)
        self.releasesdict[0] = aa

def main():
    argp = argparse.ArgumentParser(description='collect and report stlouisfed.org  FRED releases and/or their time series')

    argp.add_argument('--releases', action='store_true', default=False,
       help='return releases')
    argp.add_argument('--showreleases', action='store_true', default=False,
       help='show releases in your browser')
    argp.add_argument('--series', action='store_true', default=False,
       help='return series by series_id or by release_id')
    argp.add_argument('--showseries', action='store_true', default=False,
       help='show series for a  release_id in your browser')
    argp.add_argument('--observations', action='store_true', default=False,
       help='return timeseries for all series collected')

    argp.add_argument('--releaseid', required=False,
       help='a release_id identifies a FRED release')
    argp.add_argument('--seriesid', required=False,
       help='a series_id identifies a FRED series')

    argp.add_argument('--file', help="path to an output filename\n\
            if just a filename and--directory is not provided\
            the file is created in the current directory")
    argp.add_argument('--directory',
                    help="directory to write the output, if --observations\
                         filenames are autogenerated")

    args=argp.parse_args()

    if not args.releases and not args.series and not args.observations:
        argp.print_help()
        sys.exit(1)

    ofn=None
    fp = sys.stdout

    if not args.observations:
        if not args.directory and args.file:
            ofn = args.file
        elif args.directory and args.file:
            if '/' in args.file:
                argp.print_help()
                sys.exit()
            ofn = os.path.join(args.directory, args.file)
        if ofn:
            try:
                fp = open(ofn, 'w')
            except Exception as e:
                print('%s: %s' % (ofn, e) )
                sys.exit()

    fr = FREDReleases()

    if args.observations:
        if not args.directory:
            argp.print_help()
            sys.exit()
        if args.releaseid:
            fr.getseriesforrid(args.releaseid)
            fr.getandreportobservations(odir=args.directory)
        else:
            fr.getreleases()
            fr.getseries()
            fr.getandreportobservations(odir=args.directory)
    elif args.series and args.releaseid:
        fr.getseriesforrid(rid=args.releaseid)
        if args.showseries:
            fr.showseriesforid(args.releaseid)
            if fp != sys.stdout:
                fr.reportseriesdorid(args.releaseid, ofp=fp)
        else:
                fr.reportseriesdorid(args.releaseid, ofp=fp)
    elif args.releases:
        fr.getreleases()
        if args.showreleases:
            fr.showreleases()
            if fp != sys.stdout:
                fr.reportreleases(ofp=fp)
        else:
            fr.reportreleases(ofp=fp)

if __name__ == '__main__':
    main()
