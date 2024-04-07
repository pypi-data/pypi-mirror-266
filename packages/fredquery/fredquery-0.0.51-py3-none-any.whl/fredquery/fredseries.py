#! env python

# return information on series, their categories, releases, sources, etc
#
#

import os
import sys
import argparse
import html
from html.parser import HTMLParser
import re
import time
import urllib.request
import xml
from xml.etree import ElementTree as ET

try:
    from fredquery import query
    from fredquery import aa2html
    from fredquery import xmlstr2aa
except ImportError as e:
    import query
    import aa2html
    import xmlstr2aa

class FREDSeries():
    """ FREDSeries

    collect and report stlouisfed.org FRED series, and
    their observations(timeseries data)
    """
    def __init__(self):
        self.surl = 'https://fred.stlouisfed.org/series'
        self.ssurl = 'https://api.stlouisfed.org/fred/series'
        self.sourl = 'https://api.stlouisfed.org/fred/series/observations'
        self.scurl = 'https://api.stlouisfed.org/fred/series/categories'
        self.srurl = 'https://api.stlouisfed.org/fred/series/release'
        self.sturl = 'https://api.stlouisfed.org/fred/series/tags'
        self.suurl = 'https://api.stlouisfed.org/fred/series/updates'
        self.kurl = 'https://fred.stlouisfed.org/docs/api/api_key.html'
        self.rapi_key = '$FRED_API_KEY'
        if 'FRED_API_KEY' in os.environ:
            self.api_key = os.environ['FRED_API_KEY']
        else:
            print('FRED api_key required: %s' % (self.kurl), file=sys.stderr)
            print('assign this key to FRED_API_KEY env variable',
                                  file=sys.stderr)
            sys.exit()
        self.verbose = False
        self.seriesdict = {}
        self.observationsdict = {}
        self.categorydict = {}
        self.releasedict = {}
        self.sourcedict = {}
        self.tagdict = {}
        self.updatedict = {}

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

    def returnobservation(self, sid):
        url = '%s?series_id=%s&api_key=%s' % (self.sourl, sid,
           self.api_key)
        resp = self.uq.query(url)
        rstr = resp.read().decode('utf-8')
        aa = self.xa.xmlstr2aa(rstr)
        return aa


    def getandreportobservations(self, odir):
        """ getandreportobservations()

        incrementally get and store observation data for all
        series collected
        observation = time series data
        """
        for sid in self.seriesdict:
            aa = self.seriesdict[sid]
            assert aa[0][8] == 'units'
            assert aa[0][0] == 'id'
            keys = aa[0]
            for i in range(1, len(aa) ):
                a = aa[i]
                id = a[0]
                units = a[8]
                obsa = self.returnobservation(id)
                self.reportobservation(id, units, obsa, odir)
                time.sleep(1)

    def showseries(self, id):
        """ showseries(id)

        show the series in your browser
        id - series_id
        """
        if id not in self.seriesdict:
            print('no data for id %s' % (id), file=sys.stderr)
            return
        aa = self.seriesdict[id]
        self.ah.aashow(aa, 'Series %s' % (id) )


    def reportseries(self, id, ofp):
        """ reportseries(ofp)

        report series data for categories
        rstr - decoded response of a urllib request
        id  - key to the series data
        """
        aa = self.seriesdict[id]
        for a in aa:
            row = "','".join(a)
            print("'%s'" % (row), file=ofp)

    def returnseriesforsid(self, sid):
        """ returnseriesforsid(sid)

        get a series for a series_id and return result
        sid - series_id
        """
        url = '%s?series_id=%s&api_key=%s' % (self.ssurl, sid,
                                              self.api_key)
        resp = self.uq.query(url)
        rstr = resp.read().decode('utf-8')
        aa = self.xa.xmlstr2aa(rstr)
        if 'DISCONTINUED' in aa[1][3]:
            return None
        return aa


    def getseriesforsid(self, sid):
        """ getseriesforsid(sid)

        get a series for a series_id
        sid - series_id
        """
        aa = self.returnseriesforsid(sid)
        if len(aa) == 0:
            print('getseriesforsid(sid): no data' % (sid), file=sys.stderr)
            return
        self.seriesdict[sid] = aa

    def reportdata(self, dict, ofp):
        """ reportdata(ofp)

        report data for a collection
        dict - dictionary containing the data
        ofp - file pointer for the output file
        """
        if dict == None:
            print('nothing to report', file=sys.sterr)
            return
        for id in dict.keys():
            aa = dict[id]
            for a in aa:
                row = "´,'".join(a)
                print("'%s'" % (row), file=ofp)

    def reportcategories(self, ofp):
        self.reportdata(self.categorydict, ofp)

    def getcategoriesforsid(self, sid):
        """ getseriesforsid(sid)

        get a series for a series_id
        sid - series_id
        """
        url = '%s?series_id=%s&api_key=%s' % (self.scurl, sid,
                                              self.api_key)
        resp = self.uq.query(url)
        rstr = resp.read().decode('utf-8')
        aa = self.xa.xmlstr2aa(rstr)
        self.categorydict[sid] = aa

    def reportreleases(self, ofp):
        self.reportdata(self.releasedict, ofp)

    def getreleasesforsid(self, sid):
        """ getreleasesforsid(sid)

        get releasєs for a series_id
        sid - series_id
        """
        url = '%s?series_id=%s&api_key=%s' % (self.srurl, sid,
                                              self.api_key)
        resp = self.uq.query(url)
        rstr = resp.read().decode('utf-8')
        aa = self.xa.xmlstr2aa(rstr)
        self.releasedict[sid] = aa

    def reportsources(self, ofp):
        self.reportdata(self.sourcedict, ofp)

    def getsourcesforsid(self, sid):
        """ getsourcesforsid(sid)

        get sources for a series_id
        sid - series_id
        """
        url = '%s?series_id=%s&api_key=%s' % (self.ssurl, sid,
                                              self.api_key)
        resp = self.uq.query(url)
        rstr = resp.read().decode('utf-8')
        aa = self.xa.xmlstr2aa(rstr)
        self.sourcedict[sid] = aa

    def reporttags(self, ofp):
        self.reportdata(self.tagdict, ofp)

    def gettagsforsid(self, sid):
        """ gettagsforsid(sid)

        get tags for a series_id
        sid - series_id
        """
        url = '%s?series_id=%s&api_key=%s' % (self.sturl, sid,
                                              self.api_key)
        resp = self.uq.query(url)
        rstr = resp.read().decode('utf-8')
        aa = self.xa.xmlstr2aa(rstr)
        self.tagdict[sid] = aa

    def reportupdates(self, ofp):
        self.reportdata(self.updatedict, ofp)

    def getupdatesforsid(self, sid):
        """ getseriesforsid(sid)

        get updates for a series_id
        sid - series_id
        """
        url = '%s?series_id=%s&api_key=%s' % (self.suurl, sid,
                                              self.api_key)
        resp = self.uq.query(url)
        rstr = resp.read().decode('utf-8')
        aa = self.xa.xmlstr2aa(rstr)
        self.updatedict[sid] = aa


def main():
    argp = argparse.ArgumentParser(description='collect and report stlouisfed.org FRED series')

    argp.add_argument('--series', action='store_true', default=False,
                       help="report series urls for series_id")
    argp.add_argument('--showseries', action='store_true', default=False,
                       help="show the series in your browser")
    argp.add_argument('--observations', action='store_true', default=False,
                       help="report timeseries data for series")

    argp.add_argument('--categories', action='store_true', default=False,
                       help="report categories for this series")
    argp.add_argument('--releases', action='store_true', default=False,
                       help="report categories for this series")
    argp.add_argument('--sources', action='store_true', default=False,
                       help="report sources for this series")
    argp.add_argument('--tags', action='store_true', default=False,
                       help="report tags for this series")
    argp.add_argument('--updates', action='store_true', default=False,
                       help="report updates for this series")

    argp.add_argument('--seriesid', required=True,
        help="series are identified by series_id")

    argp.add_argument('--file', help="path to an output filename\n\
            if just a filename and--directory is not provided\
            the file is created in the current directory")
    argp.add_argument('--directory',
                    help="directory to write the output use --directory for\n\
                         storing observations, filenames autogenerated")

    args = argp.parse_args()

    ofn = None
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

    fc = FREDSeries()
    if args.observations:
        if not args.directory:
            argp.print_help()
            sys.exit()
        else:
            fc.getseriesforsid(args.seriesid)
            fc.getandreportobservations(odir=args.directory)
    elif args.series:
        fc.getseriesforsid(args.seriesid)
        if args.showseries:
            fc.showseries(args.seriesid)
            if fp != sys.stdout:
                fc.reportseries(args.seriesid, fp)
        else:
            fc.reportseries(args.seriesid, fp)
    elif args.categories:
        fc.getcategoriesforsid(args.seriesid)
        fc.reportcategories(fp)
    elif args.releases:
        fc.getreleasesforsid(args.seriesid)
        fc.reportreleases(fp)
    elif args.sources:
        fc.getsourcesforsid(args.seriesid)
        fc.reportsources(fp)
    elif args.tags:
        fc.gettagsforsid(args.seriesid)
        fc.reporttags(fp)
    elif args.updates:
        fc.getupdatesforsid(args.seriesid)
        fc.reportupdates(fp)

if __name__ == '__main__':
    main()
