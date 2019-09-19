import plotly.graph_objs as go
import pandas as pd
import sys
import math

def rendermain(stats_list):
    list_df = []
    for item in stats_list:
        sys.argv[1] = item
        df = pd.read_csv(item)
        df['msm_id'] = item.split('-')[0]
        list_df.append(df)

    # df_several includes all chosen measurements in the form of one big DataFrame
    df_several = pd.concat(list_df)
    render(df_several)


def render(dataframe):

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

    df = dataframe
    maps = df['msm_id'].unique()

    # Communal layout for all measurements
    layout = dict(
        title=dict(
            xanchor='left',
            text='Median RTT for .se NameServers: <br> <i> specific NameServer and IPv for each map can be found by hovering mouse over '
              'whichever country</i>'
              '<br>Source: <a href="https://atlas.ripe.net/dnsmon/group/se.">\
              Ripe NCC</a>',
            font=dict(
                family='Times New Roman',
                size=15
            )
        ),
        showlegend=False,
        autosize=True
    )

    data = []
    for i in range(len(maps)):
        geo_key = 'geo' + str(i + 1) if i != 0 else 'geo'
        medianRTT = pd.DataFrame(df.loc[df['msm_id'] == maps[i], 'medianRTT'])
        country = pd.DataFrame(df.loc[df['msm_id'] == maps[i], 'country'])

        for index, row in country.iterrows():
            with open('iso2toiso3.csv', 'r') as f:
                lines = f.readlines()
                for l in lines:
                    sp = l.split(',')
                    sp[1] = sp[1].strip('\n')
                    if row['country'] == sp[0]:
                        row['country'] = sp[1]

        measurementID = measurementID_dict[maps[i]]
        msm_dataframe = country.join(medianRTT)

        # data for specific measurement
        data.append(
            dict(
                type='choropleth',
                locations=msm_dataframe['country'],
                z=msm_dataframe['medianRTT'],
                geo=geo_key,
                hoverinfo='location + z + name',
                name='NameServer:<br>' + str(measurementID),
                hoverlabel=dict(
                    namelength=-1
                ),
                colorscale=[[0, 'rgb(255, 83, 26)'], [0.1, 'rgb(255,95,36)'], [0.2, 'rgb(255,107,46)'],
                            [0.3, 'rgb(254,119,56)'], [0.4, 'rgb(254,131,65)'], [0.45, 'rgb(254,143,75)'],
                            [0.5, 'rgb(254,155,85)'], [0.55, 'rgb(254,168,95)'], [0.6, 'rgb(254,180,105)'],
                            [0.7, 'rgb(253,192,114)'], [0.8, 'rgb(253,204,124)'], [0.9, 'rgb(253,216,134)'],
                            [1, 'rgb(253,228,144)']],
                autocolorscale=False,
                zmin=df['medianRTT'].min(),
                zmax=df['medianRTT'].max(),
                reversescale=False,
                marker=dict(
                    line=dict(
                        color='rgb(180,180,180)',
                        width=0.5
                    )),
                colorbar=dict(
                    tickfont=dict(
                        family='Times New Roman',
                        size=11
                    ),
                    titlefont=dict(
                        family='Times New Roman',
                        size=13
                    ),
                    title='ms',
                    titleside='top')
            )
        )

        # layout for specific measurement
        layout[geo_key] = dict(
            domain=dict(x=[], y=[]),
            showcoastlines=False,
            showcountries=False,
            showframe=True,
            framewidth=0.5,
            projection=dict(
                type='mercator'
                )
        )

    z = 0
    if len(maps) != 1:
        if math.sqrt(len(maps)) in range(21):
            ROWS = int(math.sqrt(len(maps)))
            COLS = ROWS
        else:
            COLS = int(round(math.sqrt(len(maps))))
            if len(maps) == 2:
                ROWS = 2
            elif len(maps) == 3:
                ROWS = 2
            elif 4 < len(maps) < 9:
                ROWS = 3
            elif 9 < len(maps) < 16:
                ROWS = 4
            else:
                print('Look at ROWS in script')

        for y in reversed(range(ROWS)):
            for x in range(COLS):
                geo_key = 'geo' + str(z + 1) if z != 0 else 'geo'
                layout[geo_key]['domain']['x'] = [float(x) / float(COLS), float(x + 1) / float(COLS)]
                layout[geo_key]['domain']['y'] = [float(y) / float(ROWS), float(y + 1) / float(ROWS)]
                z = z + 1
                if z > len(maps) - 1:
                    break
    else:
        COLS = 1
        ROWS = 1
        x = 0
        y = 0
        geo_key = 'geo'
        layout[geo_key]['domain']['x'] = [float(x) / float(COLS), float(x + 1) / float(COLS)]
        layout[geo_key]['domain']['y'] = [float(y) / float(ROWS), float(y + 1) / float(ROWS)]

    sp = sys.argv[1].split("-")
   # mid = sp[0]
   # if "/" in mid:
   #     # take the last
   #     mid = mid.split("/")[-1]

    start = sp[2]
    end = sp[3].strip()
    outHTML = start + "-" + end + ".html"

    fig = go.Figure(data=data, layout=layout)
    fig.update_layout(width=800)
    fig.write_html(outHTML, auto_open=True)