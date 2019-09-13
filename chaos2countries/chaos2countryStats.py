'''
giovane.moura@sidn.nl
Wed Dec 12 09:49:12 UTC 2018
single file that does it all


1. Downlaod Atlas Measurements (CHAOS DNS QUERIES)
2. Parsers it
3. Download Probe Atlas IDs
4. Download country code info
5. Enrich Atlas results with geo info from step 4
6. Spits out parsed csvs
7. Produce aggregate JSON and CSV files for easy plotting


'''

import sys
import requests
import json
import csv
import bz2
import json
import sys
import requests
import gzip
import base64
import dns.message
import traceback
import numpy as np

def read_iso_countries_list():

    url="https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv"
    r=requests.get(url)
    print("Download regions code list from :\n" + url)
    cr = csv.reader(r.content.decode("utf-8").split("\n") )
    countryCode_info=dict()

    for row in cr:
        if len(row)>2:
            countryCode_info[row[1]]=row
            #print(row)
    return countryCode_info



def read_ripe_probe_list(date,probeFile):

    url="https://ftp.ripe.net/ripe/atlas/probes/archive"
    year=date[0:4]
    month=date[4:6]
    day=date[6:8]
    day=str(int(day)-1)
    date=year+month+day
    url=url+"/"+year+"/"+month+"/" + date+".json.bz2"
    print("Downloading ripe database from " +url)
    r = requests.get(url)
    decompressed= bz2.decompress(r.content)

    decompressed=decompressed.decode("utf-8")

    j= json.loads(decompressed)
    outz=open(probeFile,'w')

    tempList=j['objects']
    newDict=j
    #reset objects
    newDict['objects'] =[]
    newList=[]
    for item in tempList:


        tempCC=item['country_code']
        #print(tempCC)

        #some handling of valid fieldds
        if type(tempCC) is not None and tempCC!=""  and str(tempCC)!="None":
            #print(tempCC)
            tempStr=geo_data[tempCC]

            continent=tempStr[5]
            sub_region=tempStr[6]
            intermediate_region=tempStr[7]

            item['continent']=continent
            item['sub_region']=sub_region
            item['intermediate_region']=intermediate_region

            #update json

            newList.append(item)
        #update item
    newDict['objects']=newList

    json.dump(newDict,outz)
    outz.close()
    #gzip it
    with open(probeFile, 'rb') as f_in, gzip.open(probeFile+'.gz', 'wb') as f_out:
        f_out.writelines(f_in)

def json_parser(f):
    answers = []

    try:
        measurements = json.loads(f)

        for m in measurements:

            try:
                fw = m["fw"]

                typeMeasurement = m["type"]

                if (int(str(fw)) >= 4570 and str(typeMeasurement == "dns")):
                    x = f4570above(m)

                    temp = x.answers

                    # print(len(temp))
                    targetServer = ""
                    for k in temp:
                        targetServer = k.RDATA

                    answers.append(

                        str(x.From) + "," + str(x.dst_addr) + "," + str(x.proto) + "," + str(targetServer) + "," + str(
                            x.rt) + "," + str(x.prb_id) + "," + str(x.timestamp) + "," + str(x.rcode)+  "," + str(x.fw))


            except:
                print("ERROR: EMPTY measurement")
                answers=[]
                answers.append("ERROR: EMPTY measurement")
                #return answers
        #if everything goes well
       # return answers
    except:
        print("ERROR parsing json")
        print("Unexpected error:", sys.exc_info())
        answers=[]
        answers.append("ERROR parsing json")


    return answers

class response4570():

    def __init__(self, k):

        self.MNAME = ""
        self.NAME = ""
        self.RDATA = ""
        self.RNAME = ""
        self.SERIAL = ""
        self.TTL = ""
        self.TYPE = ""

        try:
            self.MNAME = k['MNAME']
            ##(print self.MNAME)
            pass
        except KeyError:
            # (print"Measurement nas no MNAME")
            pass

        try:
            self.NAME = k['NAME']
            ##(printself.NAME)

        except KeyError:
            # (print"Measurement nas no NAME")
            pass

        try:
            self.RDATA = k['RDATA']
            ##(print self.RDATA)
        except KeyError:
            # (print"Measurement nas no RDATA")
            pass
        try:
            self.RNAME = k['RNAME']
            ##(printself.RNAME)
        except KeyError:
            # (print"Measurement nas no RNAME")
            pass

        try:
            self.SERIAL = k['SERIAL']
            ##(printself.SERIAL)
        except KeyError:
            # (print"Measurement nas no SERIAL")
            pass
        try:
            self.TTL = k['TTL']
            ##(printself.TTL)
        except KeyError:
            # (print"Measurement nas no TTL")
            pass

        try:
            self.TYPE = k['TYPE']
            ##(printself.TYPE)
        except KeyError:
            # (print"Measurement nas no TYPE")
            pass




class f4570above():

    def __init__(self, m):

        # parse it here

        # https://atlas.ripe.net/docs/data_struct/#v4570
        self.fw = m["fw"]  # firmware version
        self.af = -1

        # "af" -- [optional] IP version: "4" or "6" (int)
        try:
            self.af = m["af"]
            ##print( str(af))
        # break
        except KeyError:
            ##print( "Measurement does not have af")
            pass

        self.dst_addr = ""

        # dst_addr=m["dst_addr"]# -- [optional] IP address of the destination (string)
        try:
            self.dst_addr = m["dst_addr"]
            ##print( str(dst_addr))
        except KeyError:
            ##print( "Measurement does not have dst_addr")
            pass

        self.dst_name = ""

        # dst_name=m["dst_name"]# -- [optional] IP address of the destination (string)
        try:
            self.dst_name = m["dst_name"]
            ##print( str(dst_name))
        # break
        except KeyError:
            ##print( "Measurement does not have dst_name")
            pass

        # "error" -- [optional] error message (associative array)
        self.error = {}
        self.timeout = -1
        self.getaddrinfo = ""
        ##print( "gothere")
        try:
            self.error = m["error"]
            #	"timeout" -- query timeout (int)
            # "getaddrinfo" -- error message (string)

            ##print( self.error)
            if len(self.error) > 0:

                self.timeout = str(self.error['timeout'])

                try:
                    self.getaddrinfo = str(self.error['getaddrinfo'])
                except KeyError:
                    ##print( "Measurement has error, but no getaddrinfo ")
                    pass
                ##print( str("whatever"))
        # break
        except KeyError:
            ##print( "Measurement does not have error")
            pass

        ##"from" -- [optional] IP address of the source (string)

        self.From = ''
        try:
            self.From = m["from"]
            ##print( str(self.From))
        # break
        except KeyError:
            ##print( "Measurement does not have from")
            pass

        # "msm_id" -- measurement identifier (int)

        self.msm_id = ''
        try:
            self.msm_id = m["msm_id"]
            ##print( str(self.msm_id))
        # break
        except KeyError:
            ##print( "Measurement does not have msm_id")
            pass

        # "prb_id" -- source probe ID (int)

        self.prb_id = ''
        try:
            self.prb_id = m["prb_id"]
            ##print( str(self.prb_id))
        # break
        except KeyError:
            ##print( "Measurement does not have prb_id")
            pass

        # "proto" -- "TCP" or "UDP" (string)
        self.proto = ''
        try:
            self.proto = m["proto"]
            ##print( str(self.proto))
        # break
        except KeyError:
            ##print( "Measurement does not have proto")
            pass

        # "qbuf" -- [optional] query payload buffer which was sent to the server, UU encoded (string)
        self.qbuf = ''
        try:
            self.qbuf = m["qbuf"]
            ##print( str(self.qbuf))
        # break
        except KeyError:
            ##print( "Measurement does not have qbuf")
            pass

        self.timestamp = m["timestamp"]
        self.typeM = m["type"]
        self.retry = -1

        try:
            self.retry = m["retry"]
            ##print( str(self.retry))
        # break
        except KeyError:
            # print( "Measurement does not have retry")
            pass

        # here we start to parse the response
        # if there's no answer, all the values are negative, and they're printed as it

        self.result = {}
        self.ANCOUNT = -1
        self.ARCOUNT = -1
        self.ID = -1
        self.NSCOUNT = -1
        self.QDCOUNT = -1
        self.abuf = ""

        self.answers = []

        self.rt = -1
        self.size = -1
        self.src_addr = ""
        self.subid = ""
        self.submax = -1
        self.rcode = -1

        ##print( "gothere")
        try:
            self.result = m["result"]
            if len(self.result) > 0:

                ##print( self.result)
                self.ANCOUNT = self.result['ANCOUNT']
                self.ARCOUNT = self.result['ARCOUNT']
                self.ID = self.result['ID']
                self.NSCOUNT = self.result['NSCOUNT']
                self.QDCOUNT = self.result['QDCOUNT']
                self.abuf = self.result['abuf']

                # now we have to parse this BS abuf to get the RCODE field
                try:
                    str_answer = (str(self.abuf))
                    dnsmsg = dns.message.from_wire(base64.b64decode(str_answer))
                except:
                    print("Unexpected error parsing base64 info:", sys.exc_info()[0])
                    print(traceback.print_exc())
                self.rcode = dnsmsg.rcode()

                # self.timeout=self.result['timeout']
                # self.timeout=self.result['timeout']

                # answers" -- first two records from the response decoded by the probe, if they are TXT or SOA; other RR can be decoded from "abuf" (array)

                # we create an object with answers , then we have to pull it out later on
                try:
                    tempz = self.result['answers']
                    ###print( tempz)
                    ##print( "the number of answers is: " + str(len(tempz)))

                    for k in tempz:
                        ##print( k)
                        self.answers.append(response4570(k))

                except KeyError:
                    #print("Measurement has result, but no answer ")
                    pass

                try:
                    self.rt = self.result['rt']

                except KeyError:
                    # print( "Measurement has result, but no rt ")
                    pass

                try:
                    self.size = self.result['size']

                except KeyError:
                    # print( "Measurement has result, but no size ")
                    pass

                try:
                    self.src_addr = self.result['src_addr']

                except KeyError:
                    # print( "Measurement has result, but no src_addr ")
                    pass

                try:
                    self.subid = self.result['subid']

                except KeyError:
                    # print( "Measurement has result, but no subid ")
                    pass

                try:
                    self.submask = self.result['submask']

                except KeyError:
                    # print( "Measurement has result, but no submask ")
                    pass

                ##print( str("whatever"))
        # break
        except KeyError:
            # print( "Measurement does not have result")
            pass
        ##"from" -- [optional] IP address of the source (string)

        # See example code for decoding the value
        # "result" -- [optional] response from the DNS server (associative array)
        # "ANCOUNT" -- answer count, RFC 1035 4.1.1 (int)
        # "ARCOUNT" -- additional record count, RFC 1035, 4.1.1 (int)
        # "ID" -- query ID, RFC 1035 4.1.1 (int)
        # "NSCOUNT" -- name server count (int)
        # "QDCOUNT" -- number of queries (int)
        # "abuf" -- answer payload buffer from the server, UU encoded (string)
        # See example code for decoding the value
        # "answers" -- first two records from the response decoded by the probe, if they are TXT or SOA; other RR can be decoded from "abuf" (array)
        # Each element is an associative array consisting of:
        # "MNAME" -- domain name, RFC 1035, 3.1.13 (string)
        # "NAME" -- domain name. (string)
        # "RDATA" -- [type TXT] txt value, (string)
        # "RNAME" -- [if type SOA] mailbox, RFC 1035 3.3.13 (string)
        # "SERIAL" -- [type SOA] zone serial number, RFC 1035 3.3.13 (string)
        # "TTL" -- [type SOA] time to live, RFC 1035 4.1.3 (int)
        # "TYPE" -- RR "SOA" or "TXT" (string), RFC 1035
        # "rt" -- [optional] response time in milli seconds (float)
        # "size" -- [optional] response size (int)
        # "src_addr" -- [optional] the source IP address added by the probe (string).
        # "subid" -- [optional] sequence number of this result within a group of results, available if the resolution is done by the probe's local resolver
        # "submax" -- [optional] total number of results within a group (int)
        # "retry" -- [optional] retry count (int)
        # "timestamp" -- start time, in Unix timestamp (int)
        # "type" -- "dns" (string)


def read_probe_data(f):
    f = gzip.open(f, 'rb')
    metadata = f.read()
    metadata=metadata.decode("utf-8")
    f.close()

    appendDict=dict()

    items=json.loads(metadata)

    for k in items['objects']:
        prid=k['id']
        version="-1"
        #analyze the tags

        for i in k['tags']:
            if 'system-v1' in i:
                version="system-v1"
            elif 'system-v2' in i:
                version = "system-v2"
            elif 'system-v3' in i:
                version = "system-v3"
            elif 'system-v4' in i:
                version = "system-v4"
        trailler=k['country_code']+","+k['continent']+","+k['sub_region']+","+version
        appendDict[str(prid)]=trailler

    return appendDict


#start

print("chaos2countryStats.py")
print("WARNING: CHOOSE CAREFULLY TIME RANGE -- DO NOT OVERLOAD ATLAS")
print("Usage:  python3 chaos2countryStats.py $ATLAS_JSON_RAW_FILE  $DATE(YYYYMMDD) $OUTPUT_CSV $COUNTRIES-stats_JSON $COUNTRIES-stats_CSV")


if len(sys.argv)!=3:
    print("Wrong number of parameters\n")
    print(str(len(sys.argv)))
    print(  "Usage:  python chaos2countryStats.py $ATLAS_JSON_RAW_FILE  $DATE(YYYYMMDD) ")
else:

    print("reading country code info")
    geo_data=read_iso_countries_list()

    date=sys.argv[2]
    probeFile=date+"-probemetadata.json"

    print("reading probe metadata info")
    ripe_data=read_ripe_probe_list(date,probeFile)

    print("reading Ripe Altas CHAOS Measurements and parsing")
    url=sys.argv[1]

    r = requests.get(url)
    measurements=json_parser(r.content.decode("utf-8"))

    probeDict = read_probe_data(probeFile+".gz")
    atlas_results=date+"-atlas-results.csv"


    #now, with all the data in hands, we gotta for each measurmenet to add the trailler
    csvFileFromAtlas=open(atlas_results, 'w')
    csvFileFromAtlas.write("ip_src,ip_dst,proto,hostnameBind,rtt,probeID,timestamp,rcode,atlas_firmware,country,continent,subregion,probe_version\n")
    for k in measurements:
        #print("w")
        probeID=k.split(",")[5]
        trailler="NA,NA"
        try:
            trailler=probeDict[probeID.strip()]
        except:
            print("Probe not found: " + str(probeID))
        csvFileFromAtlas.write(k+","+trailler+"\n")

    csvFileFromAtlas.close()


    print("starting agg stats per country")
    print("ONLY FOR RCODE=0")

    ccDict = dict()

    with open(atlas_results, 'r') as f:
        lines = f.readlines()

        for l in lines:

            sp = l.split(",")
            # if matches rcode and if the column value matches
            if len(sp) == 13:
                #filtering rcode 0
                if sp[7].strip() == "0":
                    tempCountry = sp[9].strip()
                    tempRTT = float(sp[4].strip())

                    if tempCountry not in ccDict:
                        tempArray = []
                        tempArray.append(tempRTT)
                        ccDict[tempCountry] = tempArray
                    else:
                        tempArray = ccDict[tempCountry]
                        tempArray.append(tempRTT)
                        ccDict[tempCountry] = tempArray

    #output stats.csv
    jsonDict=dict()
    with open(date+"-stats.csv", "w") as f:

        f.write("country, nMesurements,meanRTT,percentile25RTT,medianRTT,percentile75RTT,percentile90RTT,maxRTT\n")
        for k, values in ccDict.items():
            country = k
            f.write(
                country
                + "," +
                str(len(values))
                + "," +
                str(np.mean(values))
                + "," + str(np.percentile(values, 25))
                + "," + str(np.percentile(values, 50))
                + "," + str(np.percentile(values, 75))
                + "," + str(np.percentile(values, 90))
                + "," + str(np.max(values))+"\n")

            tempDict=dict()

            tempDict['nMeasurements']=len(values)
            tempDict['meanRTT']=np.mean(values)
            tempDict['percentile25RTT']=np.percentile(values, 25)
            tempDict['medianRTT']=np.percentile(values, 50)
            tempDict['percentile75RTT']=np.percentile(values, 75)
            tempDict['percentile90RTT']=np.percentile(values, 95)
            tempDict['maxRTT']=np.max(values)

            jsonDict[country]=tempDict


            #   +","+  str(np.max(values)) + "," + str(np.percentile(values,90)) )

    print("writing json output")

    #create json format
    with open(date+"-stats.json", "w") as f:
        json.dump(jsonDict,f)


print('END')



