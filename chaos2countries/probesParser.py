
'''
giovane.moura@sidn.nl
Wed Dec 12 09:49:12 UTC 2018


3. Download Probe Atlas IDs
4. Download country code info
5. Enrich Atlas results with geo info from step 4


'''

import csv
import bz2
import json
import requests
import gzip
import os
import sys



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

        # some handling of valid fieldds
        if type(tempCC) is not None and tempCC!=""  and str(tempCC)!="None":
            tempStr = geo_data[tempCC]

            continent = tempStr[5]
            sub_region = tempStr[6]
            intermediate_region = tempStr[7]

            item['continent'] = continent
            item['sub_region'] = sub_region
            item['intermediate_region'] = intermediate_region

             update json

            newList.append(item)
         update item
    newDict['objects'] = newList

    json.dump(newDict, outz)
    outz.close()
    # gzip it
    with open(probeFile, 'rb') as f_in, gzip.open(probeFile+'.gz', 'wb') as f_out:
        f_out.writelines(f_in)
    os.remove(probeFile)


def read_probe_data(f):
    f = gzip.open(f, 'rb')
    metadata = f.read()
    metadata = metadata.decode("utf-8")
    f.close()

    appendDict = dict()

    items = json.loads(metadata)


    for k in items['objects']:
        prid = k['id']
        version = "-1"
        # analyze the tags

        #for i in k['tags']:
         #   if 'system-v1' in i:
          #      version = "system-v1"
           # elif 'system-v2' in i:
            #    version = "system-v2"
            #elif 'system-v3' in i:
             #   version = "system-v3"
            #elif 'system-v4' in i:
             #   version = "system-v4"
        trailler = k['country_code']+","+k['continent']+","+k['sub_region'] # +","+version
        appendDict[str(prid)] = trailler

    return appendDict
