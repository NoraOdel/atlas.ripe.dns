import os
import pandas as pd
import plotly.graph_objs as go
import sys
from plotly.subplots import make_subplots


def rendermain(stats):

    layout = dict(
        title='median rtt for all',
        autosize=False,
        width=1000,
        height=900,
        hovermode=False,
        legend=dict(
            x=0.7,
            y=-0.1,
            bgcolor='rgba(255, 255, 255, 0)',
            font=dict(size=11)
        )
    )

    list_of_files = os.listdir('/Users/nora.odelius/pycharmprojects/atlas-dns-chaos-2-rtt-countries/tests')
    substring = '-stats-country.csv'
    for file in list_of_files:
        if substring in file:
            measurementID = file.split('-')[0]
            date = stats.split('-')[1]
            year = date[0:4]
            month = date[4:6]
            day = date[6:8]

            measurementID_dict = {
                '1413741': 'a.ns.se (IPv6)',
                '1413717': 'a.ns.se (IPv4)',
                '1413745': 'b.ns.se (IPv4)',
                '1413689': 'b.ns.se (IPv6)',
                '1413725': 'c.ns.se (IPv4)',
                '1413705': 'c.ns.se (IPv6)',
                '1413729': 'f.ns.se (IPv4)',
                '1413693': 'f.ns.se (IPv6)',
                '1413733': 'g.ns.se (IPv4)',
                '1413749': 'g.ns.se (IPv6)',
                '1413697': 'i.ns.se (IPv4)',
                '1413701': 'i.ns.se (IPv6)',
                '1413721': 'j.ns.se (IPv4)',
                '1413713': 'j.ns.se (IPv6)',
                '6960402': 'x.ns.se (Ipv4)',
                '6960407': 'x.ns.se (IPv6)',
                '11156555': 'y.ns.se (Ipv4)',
                '11156560': 'y.ns.se (Ipv6)',
                '11156550': 'z.ns.se (IPv4)',
                '11156545': 'z.ns.se (IPv6)'}

            measurementID = measurementID_dict[measurementID]

            sys.argv[1] = file
            iso2iso3 = dict()
            with open('iso2toiso3.csv', 'r') as f:
                lines = f.readlines()
                for l in lines:
                    sp = l.split(',')
                    iso2iso3[sp[0]] = sp[1].strip()

            tempFile = open('tempCSV.csv', 'w')
            tempFile.write("country,medianRTT\n")

            with open(sys.argv[1], 'r') as f:
                lines = f.readlines()
                for l in lines:
                    sp = l.split(',')
                    cc = sp[0]
                    if cc != "country":
                        cc3 = iso2iso3[cc]
                        median = sp[4]
                        tempFile.write(cc3+","+median+"\n")

            tempFile.close()

            df = pd.read_csv('tempCSV.csv', sep=",")

            data.append(
                dict(
                    type='choropleth',
                    locations=df['country'],
                    z=df['medianRTT'],
                    # text=df['country'],
                    colorscale=[[0, 'rgb(255, 83, 26)'], [0.35, 'rgb(254, 112, 49)'], [0.5, 'rgb(254, 141, 73)'],
                                [0.6, 'rgb(253, 170, 96)'], [0.7, 'rgb(253, 199, 120)'], [1, 'rgb(253, 228, 144)']],
                    autocolorscale=False,
                    reversescale=False,
                    marker=dict(
                        line=dict(
                            color='rgb(180,180,180)',
                            width=0.5
                        )),
                    colorbar=dict(
                       # bordercolor='rgb(232,238,250)',
                       # bgcolor='white',
                       # borderwidth=0.5,
                        # 'rgb(232,238,250)',
                        tick0=0,
                        dtick=50,
                        title='ms',
                        titleside='top')
                  ))

            sp = sys.argv[1].split("-")
            mid = sp[0]
            if "/" in mid:
                # take the last
                mid = mid.split("/")[-1]

            start = sp[2]
            end = sp[3].strip()

           # layout(annotations=(list=(x=1, y=1, text='hejejehejjkndkalndlksa',
           # xref='paper', yref='paper', ),)

            # <i></i> italics
            # <a href='...'></a> links
            # opacity
            # font

            #  annotations=[
            #      go.layout.Annotation(
            #          x=0.15,
            #          y=-0.17,
            #          font=dict(size=15, color='gray'),
            #          xref='paper',
            #          yref='paper',
            #          bgcolor='whitesmoke',
            #          text='This is a visualization of the round trip time (rtt) '
            #        'for specific .se nameservers <br> '
            #       'in regards to the country from which the request was sent',
            # showarrow=False)],


            layout = dict(
                title='Median RTT in milliseconds (ms) <br> for ' + measurementID + ' on ' + year + '-' + month + '-' + day,
                paper_bgcolor='whitesmoke',
                font=dict(
                    size=15,
                    color='black'
                ),
                geo=dict(
                    framecolor='black',
                    framewidth=0.5,
                    showframe=True,
                    showcoastlines=False,
                    projection=dict(
                        type='mercator'
                    )
                )
            )

    outHTML = mid + "-" + start + "-" + end + ".html"

    fig = go.Figure(data=data, layout=layout)
    fig.write_html(outHTML, auto_open=True)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Wrong number of parameters\n")
        print(str(len(sys.argv)))
        print("Usage:  python3 render.py $inputFileCSV ")
        #print("e.g.: python3 render.py  ../tests/10310-20181212-1544572800-1544573100-stats-country.csv")

    else:
        rendermain()
        print('END')
