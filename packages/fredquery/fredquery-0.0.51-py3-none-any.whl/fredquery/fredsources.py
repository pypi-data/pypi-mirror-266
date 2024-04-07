
#! env python

# return information on sources and their releases
#

import os
import sys
import argparse
import re
import time
import urllib.request
import xml

try:
    from fredquery import query
    from fredquery import aa2html
    from fredquery import xmlstr2aa
except ImportError as e:
    import query
    import aa2html
    import xmlstr2aa

class FREDSources():

    def __init__(self):
        """ FREDSources

        collects sources and their releases
        data
        """
        # fred sources
        self.surl = 'https://api.stlouisfed.org/fred/sources'
        self.osurl = 'https://api.stlouisfed.org/fred/source'
        self.sourcedict = {}
        # releases for a source_id
        self.srurl = 'https://api.stlouisfed.org/fred/source/releases'
        self.releasedict = {}
        self.rurl = 'https://api.stlouisfed.org/fred/releases'
        # series for a release id
        self.rsurl = 'https://api.stlouisfed.org/fred/release/series'
        self.seriesdict = {}
        # observations for a series id
        self.sourl = 'https://api.stlouisfed.org/fred/series/observations'
        self.observationsdict = {}
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
        self.verbose = False
        self.sid     = None
        self.rid     = None

        self.uq = query._URLQuery()
        self.ah = aa2html._AA2HTML()
        self.xa = xmlstr2aa._XMLStr2AA()


    def reportobservation(self, id, units, obsa, odir):
        """ reportobservation(sid, obsa, odir)

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
        for rid in self.seriesdict:
            aa = self.seriesdict[rid]
            assert aa[0][0] == 'id'
            assert aa[0][8] == 'units'
            for i in range(1, len(aa) ):
                a = aa[i]
                sid = a[0]
                url = '%s?series_id=%s&api_key=%s' % (self.sourl, sid,
                       self.api_key)
                units = a[8]
                resp = self.uq.query(url)
                rstr = resp.read().decode('utf-8')
                # observation data doesn't identify itself
                oaa = self.xa.xmlstr2aa(rstr)
                self.reportobservation(sid, units, oaa, odir)
                time.sleep(1)

    def returnseries(self):
        saa = []
        for id in self.seriesdict.keys():
            aa = self.seriesdict[id]
            if len(saa) == 0:
                saa.append(aa[0])
            saa.append(aa[1])
        return saa

    def showseries(self):
        """ showseries()

        show the series list for a source in your browser
        """
        saa = self.returnseries()
        self.ah.aashow(saa, 'Source ID %s Series' % (self.sid))

    def reportseries(self, fp):
        """ reportseries(fp)

        report series for each release_id collected
        fp - file pointer to destination file
        """
        saa = self.returnseries()
        for a in saa:
            row = "','".join(a)
            fp.write("'%s'" % (row) )

    def getseriesforrid(self, rid):
        """ getseriesforrid(rid)

        get all series for a release_id
        rid - release_id - required
        """
        if not rid:
            print('getseriesforrid: rid required', file=stderr)
            sys.exit(1)
        url = '%s?release_id=%s&api_key=%s' % (self.rsurl,
                                           rid, self.api_key)
        resp = self.uq.query(url)
        rstr = resp.read().decode('utf-8')
        aa = self.xa.xmlstr2aa(rstr)
        if len(aa) == 0:
            print('getseriesforrid(rid): no data' % (sid), file=sys.stderr)
            return
        # eliminate discontinued series
        raa = []
        for i in range(len(aa) ):
            if 'DISCONTINUED' in aa[i][3]:
                continue
            raa.append(aa[i])
        self.seriesdict[rid] = raa

    def returnseriesforsid(self, sid):
        """ returnseriesforsid(sid)

        get and return series for a source_id
        sid source_id
        """
        self.getreleasesforsid(sid)
        aa = self.releasedict[sid] 
        saa = []          # releases array of arrays
        for i in range(1, len(aa) ):
            a = aa[i]     # data on a release
            self.getseriesforrid(a[0])
            raa = self.seriesdict[a[0]]  # series for a release
            if len(saa) == 0:
                saa.append(raa[0])       # header
            saa.extend(raa[1:])
        return saa

    def getseries(self):
        """ getseries()

        convenience function to get series data for a source
        """
        for sid in self.releasedict.keys():
            aa = self.releasedict[sid]
            for i in range(1, len(aa) ):
                rid = aa[i][0]
                self.getseriesforrid(rid)
                time.sleep(1)


    def reportreleasesforsid(self, sid, ofp):
        """ reportreleasesforsid(sid, ofp)

        report all releases collected
        sid - source_id
        ofp - file pointer to which to write
        """
        aa = self.releasedict[sid]
        for a in aa:
            row = "','".join(a)
            print("'%s'" % (row), file=ofp)

    def showreleasesforsid(self, sid):
        aa = self.releasedict[sid]
        name = 'Releases for source_id %s' % (sid)
        self.ah.aashow(aa, name)

    def getreleasesforsid(self, sid):
        """ getreleasesforsid(sid)

        get releases for a source_id
        sid - source_id
        """
        self.sid = sid
        url = '%s?source_id=%s&api_key=%s' % (self.srurl, sid, self.api_key)
        resp=self.uq.query(url)
        rstr = resp.read().decode('utf-8')
        aa = self.xa.xmlstr2aa(rstr)
        self.releasedict[sid] = aa

    def getreleases(self):
        """ getreleases()

        collect all releases for sources collected
        """
        for sid in self.sourcedict:
            self.getreleasesforsid(sid)
            time.sleep(1)

    def returnsources(self):
        saa = []
        for k in self.sourcedict.keys():
            saa.extend(self.sourcedict[k])
        return saa

    def showsources(self):
        """ showsources()

        show the sources in your browser
        """
        aa = self.returnsources()
        self.ah.aashow(aa, 'FRED Sources')

    def reportsources(self, ofp):
        """reportsources(ofp)

        report data on all sources collected
        ofp - file pointer to which to write
        """
        aa = self.returnsources()
        for a in aa:
            row = "','".join(a)
            print("'%s'" % (row), file=ofp)

    def getsourceforsid(self, sid):
        """ getsourceforsid(sid)

        collect FRED source for a source_id
        """
        url = '%s?source_id=%s&api_key=%s' % (self.osurl, sid, self.api_key)
        resp = self.uq.query(url)
        rstr = resp.read().decode('utf-8')
        #  print(rstr)
        aa = self.xa.xmlstr2aa(rstr)
        self.sourcedict[sid] = aa

    def getsources(self):
        """ getsources()

        collect all FRED sources
        """
        url = '%s?api_key=%s' % (self.surl, self.api_key)
        resp = self.uq.query(url)
        rstr = resp.read().decode('utf-8')
        #  print(rstr)
        aa = self.xa.xmlstr2aa(rstr)
        keys = aa[0]
        assert keys[0] == 'id'
        aa[0].append('url')
        for i in range(1, len(aa) ):
            a = aa[i]
            id = a[0]
            url = '%s?source_id=%s&api_key=%s' % (self.srurl, id, self.rapi_key)
            a.append(url)
        self.sourcedict[1] = aa

def main():
    argp = argparse.ArgumentParser(description='collect and report stlouisfed.org  FRED sources and/or their releases')

    argp.add_argument('--sources', action='store_true', default=False,
       help='return sources')
    argp.add_argument('--showsources', action='store_true', default=False,
       help='show sources in your browser')
    argp.add_argument('--releases', action='store_true', default=False,
       help='return releases for a source_id')
    argp.add_argument('--showreleasesforsid', action='store_true', default=False,
       help='show releases for a source_id in your browser')
    argp.add_argument('--series', action='store_true', default=False,
       help='return series for a source_id')
    argp.add_argument('--showseries', action='store_true', default=False,
       help='show series for a series_id in your browser')
    argp.add_argument('--observations', action='store_true', default=False,
       help='return observations for a source_id')

    argp.add_argument('--sourceid', required=False,
       help='a source_id identifies a FRED source')

    argp.add_argument('--file', help="path to an output filename\n\
            if just a filename and--directory is not provided\
            the file is created in the current directory")
    argp.add_argument('--directory',
                    help="directory to write the output, if --observations\
                         filenames are autogenerated")

    args=argp.parse_args()

    if not args.sources and not args.releases and\
       not args.series and not args.observations:
        argp.print_help()
        sys.exit(1)

    fp = sys.stdout
    ofn = None

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

    fs = FREDSources()

    if args.observations:
        if not args.directory:
            argp.print_help()
            sys.exit()
        if args.sourceid:
            fs.getsourceforsid(args.sourceid)
            fs.getreleasesforsid(args.sourceid)
            fs.getseries()
            fs.getandreportobservations(args.directory)
    elif args.series and args.sourceid:
        fs.getreleasesforsid(args.sourceid)
        fs.getseries()
        if args.showseries:
            fs.showseries()
            if fp != sys.stdout:
                fs.reportseries(fp)
        else:
            fs.reportseries(fp)
    elif args.sources and args.sourceid:
        fs.getsourceforsid(args.sourceid)
        fs.reportsources(fp)
    elif args.sources:
        fs.getsources()
        if args.showsources:
            fs.showsources()
            if fp != sys.stdout:
                fs.reportsources(fp)
        else:
            fs.reportsources(fp)
    elif args.releases and args.sourceid:
        fs.getreleasesforsid(args.sourceid)
        if args.showreleasesforsid:
            fs.showreleasesforsid(args.sourceid)
            if fp != sys.stdout:
                fs.reportreleasesforsid(args.sourceid, fp)
        else:
            fs.reportreleasesforsid(args.sourceid, fp)

if __name__ == '__main__':
    main()
