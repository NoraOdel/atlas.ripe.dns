import sys
from ripe.atlas.sagan import DnsResult
from datetime import datetime, timedelta
import pandas as pd
import bz2
import json
import requests
import gzip
import os
import csv
import dns.message
import base64
import numpy as np

def json_parser(f):

    answers = []
    try:
        measurement = json.loads(f)

        for lines in measurement:
            try:
                my_results = DnsResult(lines)

                try:
                    src_result = my_results.responses[0].source_address
                    dst_result = my_results.responses[0].destination_address
                    proto_result = my_results.responses[0].protocol
                    rtt_result = my_results.responses[0].response_time
                    abuf = str(my_results.responses[0].abuf)
                    dnsmsg = dns.message.from_wire(base64.b64decode(abuf))
                    rcode = dnsmsg.rcode()

                    prb_id = lines['prb_id']
                    fw = lines['fw']

                    answers.append(str(src_result) + ',' + str(dst_result) + ',' + str(proto_result) + ',' +
                                   str(rtt_result) + ',' + str(prb_id) + ',' + str(rcode) + ',' +
                                   str(fw))

                except:
                    # print("ERROR: EMPTY measurement")
                    # if measurement is empty set evert index as empty
                    answers.append(',' + ',' + ',' + ',' + ',' + ',' + ',' + ',')

            except:
                print('Error: Measurement is not a DNS measurement')
    except:
        # print("ERROR parsing json")
        # print("Unexpected error:", sys.exc_info())
        # answers=[]
        # answers.append("ERROR parsing json")
        pass

    return answers


def timestamped_url(arg):
    sys.argv[1] = arg

    now = datetime.utcnow()
    wanted = now - timedelta(days=1)
    wanted_after = wanted + timedelta(minutes=10)

    year = str(wanted).split('-')[0]
    month = str(wanted).split('-')[1]
    day = str(wanted).split('-')[2].split(' ')[0]

    hour = str(wanted).split(':')[0].split(' ')[1]
    minute = str(wanted).split(':')[1]
    minute = str(int(int(minute) / 10) * 10)
    if minute == '0':
        minute = '00'

    wanted_year = str(wanted_after).split('-')[0]
    wanted_month = str(wanted_after).split('-')[1]
    wanted_day = str(wanted_after).split('-')[2].split(' ')[0]

    wanted_hour = str(wanted_after).split(':')[0].split(' ')[1]
    wanted_minute = str(wanted_after).split(':')[1]
    wanted_minute = str(int(int(wanted_minute) / 10) * 10)
    if wanted_minute == '0':
        wanted_minute = '00'

    time1 = year + '-' + month + '-' + day + ' ' + hour + ':' + minute
    time2 = wanted_year + '-' + wanted_month + '-' + wanted_day + ' ' + wanted_hour + ':' + wanted_minute

    time_formated = pd.to_datetime(time1, format='%Y-%m-%d %H:%M')
    time_formated2 = pd.to_datetime(time2, format='%Y-%m-%d %H:%M')
    timestamp = str(int(datetime.timestamp(time_formated)))
    timestamp2 = str(int(datetime.timestamp(time_formated2)))

    end = '/results/?format=json&start=' + timestamp + '&stop=' + timestamp2
    beginning = 'https://atlas.ripe.net/api/v2/measurements/'
    # middle = the measurement id from the argument based on string indexing
    middle = sys.argv[1][43:51]
    middle = middle.strip('/')

    url = beginning + middle + end
    return url


def read_probe_data(f):
    f = gzip.open(f, 'rb')
    metadata = f.read()
    metadata = metadata.decode("utf-8")
    f.close()

    appendDict = dict()

    items = json.loads(metadata)


    for k in items['objects']:
        prid = k['id']

        trailler = k['country_code']+","+k['continent']+","+k['sub_region']
        appendDict[str(prid)] = trailler

    return appendDict


def read_iso_countries_list():

    url = "https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv"
    r = requests.get(url)
    print("Download regions code list from :\n" + url)
    cr = csv.reader(r.content.decode("utf-8").split("\n") )
    countryCode_info = dict()

    for row in cr:
        if len(row) > 2:
            countryCode_info[row[1]] = row
            # print(row)

    return countryCode_info


def read_ripe_probe_list(date,probeFile,geo_data):

    url = "https://ftp.ripe.net/ripe/atlas/probes/archive"
    year = date[0:4]
    month = date[4:6]
    day = date[6:8]
    date = year+month+day
    url = url+"/"+year+"/"+month+"/" + date+".json.bz2"

    print("Downloading ripe database from " + url)
    r = requests.get(url)
    decompressed = bz2.decompress(r.content)

    decompressed = decompressed.decode("utf-8")

    j = json.loads(decompressed)
    outz = open(probeFile,'w')

    tempList = j['objects']
    newDict = j
    # reset objects
    newDict['objects'] =[]
    newList = []
    for item in tempList:
        tempCC = item['country_code']

        # some handling of valid fields
        if type(tempCC) is not None and tempCC != "" and str(tempCC) != "None":
            tempStr = geo_data[tempCC]

            continent = tempStr[5]
            sub_region = tempStr[6]
            intermediate_region = tempStr[7]

            item['continent'] = continent
            item['sub_region'] = sub_region
            item['intermediate_region'] = intermediate_region

            newList.append(item)
    newDict['objects'] = newList

    json.dump(newDict, outz)
    outz.close()
        # gzip it
    with open(probeFile, 'rb') as f_in, gzip.open(probeFile+'.gz', 'wb') as f_out:
        f_out.writelines(f_in)
    os.remove(probeFile)






    """def timestamped_url(arg):
    sys.argv[1] = arg
    now = datetime.now().strftime('%Y-%m')
    day = int(datetime.now().strftime('%d'))
    day_before = day - 1
    hour = int(datetime.now().strftime('%H'))
    minute = int(datetime.now().strftime('%M'))
    minute = int(minute / 10) * 10

    if minute == 50:
        minute_after_ten = 00
        if hour == 23:
            hour_after_ten = 00
        else:
            hour_after_ten = hour + 1
    else:
        minute_after_ten = int(minute) + 10
        hour_after_ten = hour

    # the same time as now but yesterday, minute is dropped to the closest tens
    time = now + '-' + str(day_before) + ' ' + str(hour) + ':' + str(minute)
    time2 = now + '-' + str(day_before) + ' ' + str(hour_after_ten) + ':' + str(minute_after_ten)

    time_formated = pd.to_datetime(time, format='%Y-%m-%d %H:%M')
    time_formated2 = pd.to_datetime(time2, format='%Y-%m-%d %H:%M')
    timestamp = str(int(datetime.timestamp(time_formated)))
    timestamp2 = str(int(datetime.timestamp(time_formated2)))

    end = '/results/?format=json&start=' + timestamp + '&stop=' + timestamp2
    beginning = 'https://atlas.ripe.net/api/v2/measurements/'
    # middle = the measurement id from the argument based on string indexing
    middle = sys.argv[1][43:51]
    middle = middle.strip('/')

    url = beginning + middle + end
    return url"""