#! env python

import os
import sys
import argparse
import webbrowser

import plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go

try:
    from fredquery import fredseries
except ImportError as e:
    import fredseries

class FREDPlotSeries():
    def __init__(self):
        """ create a plot with a list of FRED series_id's
        """
        # settings

        self.fs = fredseries.FREDSeries()
        self.seriesdict={}
        self.observationsdict={}
        self.unitseriesdict = {}  # [units][sid]
        self.html = None

        self.df = None
        self.fig = None

    def getobservation(self, sid):
        """ getobservation(sid)

        get time series observations data for a FRED serieѕ_id
        sid - FRED series_id
        """
        aa = self.fs.returnobservation(sid)
        self.observationsdict[sid] = aa

    def getobservationlist(self, slist):
        sa = slist.split(',')
        for sid in sa:
            self.getobservation(sid)

    def getseries(self, sid):
        """ getseries(sid)

        get descriptive data for a FRED series_id
        sid - FRED series_id
        """
        aa = self.fs.returnseriesforsid(sid)
        units = aa[1][8]
        if units not in self.unitseriesdict.keys():
            self.unitseriesdict[units]={}
        self.unitseriesdict[units][sid] = aa

    def getserieslist(self, slist):
        """ getserieslist(slist)

        split comma separated slist into an array of series_id
        and get series data for each series
        """
        sa = slist.split(',')
        for sid in sa:
            self.getseries(sid)

    # https://plotly.com/python/multiple-axes/
    def composeunitseriesplot(self, u, ptitle):
        """ composeunitseriesplot()

        compose plotly figure for later display with the series_id as
        the legend
        units - units of the observations
        """
        #fig = go.Figure()
        fig  = make_subplots(shared_yaxes=True, shared_xaxes=True)

        issecond=False

        for sid in self.unitseriesdict[u]:
            saa = self.unitseriesdict[u][sid]
            sid    = saa[1][0]
            stitle = saa[1][3]
            units  = saa[1][8]

            oaa = self.observationsdict[sid]

            dates = [oaa[i][2] for i in range(len(oaa) )]
            vals  = [oaa[i][3] for i in range(len(oaa) )]

            fig.add_trace( go.Scatter( x=dates, y=vals, name=sid) )
            #fig.add_trace( go.Scatter( x=dates, y=vals, name=sid),
            #                          secondary_x=issecond)
            issecond=True

        fig.update_layout(
            title=ptitle,
            yaxis_title=units,
            xaxis_title='dates',
        )
        return fig

    def composeunitseriesplotwnotes(self, title):
        """ composeunitseriesplotwnotes()

        compost plots with notes organized by units
        """
        htmla = []
        htmla.append('<html>')
        if not title: title = 'FRED Series Plot'
        htmla.append('<title>%s</title>' % (title) )

        for u in self.unitseriesdict.keys():

            fig = self.composeunitseriesplot(u, title)
            fightml = fig.to_html()
            htmla.append(fightml)

            for sid in self.unitseriesdict[u].keys():
                saa = self.unitseriesdict[u][sid]
                sid=saa[1][0]
                stitle=saa[1][3]

                htmla.append('<h3>%s:  %s</h3>' % (sid, stitle) )

                # header
                htmla.append('<table border="1">')
                hrowa = [saa[0][i] for i in range(len(saa[0])-1) if i != 3]
                hrow = '</th><th>'.join(hrowa)
                htmla.append('<tr>%s</tr>' % (''.join(hrow)) )

                # data
                drowa = [saa[1][i] for i in range(len(saa[1])-1) if i != 3]
                drow = '</td><td>'.join(drowa)
                htmla.append('<tr>%s</tr>' % (''.join(drow)) )
                htmla.append('</table>')

                # notes
                htmla.append('<p>')
                htmla.append('%s: %s' % (saa[0][-1], saa[1][-1]) )
                htmla.append('</p>')

        htmla.append('</html>')

        self.html = ''.join(htmla)
        return self.html

    def saveplothtml(self, fn):
        """ saveplothtml(fn)

        save the plot html
        fn - filename
        """
        with open(fn, 'w') as fp:
            fp.write(self.html)

    def showplothtml(self, fn):
        """ showplothtml(fn)

        show the html in your web browser
        fn - filename of the html file
        """
        webbrowser.open('file://%s' % (fn) )

    def showplotfig(self):
        self.fig.show()

def main():
    argp = argparse.ArgumentParser(description='plot a series list')
    argp.add_argument('--serieslist', required=True,
        help="comma separated list of FRED series_id's")
    argp.add_argument('--htmlfile', default='/tmp/p.html',
        help="path to file that will contain the plot")
    args = argp.parse_args()

    PS = PlotSeries()

    PS.getserieslist(args.serieslist)
    PS.getobservationlist(args.serieslist)

    PS.composeunitseriesplotwnotes()

    PS.saveplothtml(args.htmlfile)
    PS.showplothtml(args.htmlfile)
    #PS.showplotfig()

if __name__ == '__main__':
    main()
