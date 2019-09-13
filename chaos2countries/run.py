import sys
sys.path.append('../')
import requests
from chaos2countries.norasversion import timestamped_url, json_parser, read_probe_data, read_ripe_probe_list, \
    read_iso_countries_list
from visualization.render import rendermain
import numpy as np
from datetime import datetime
import os.path
import os
import webbrowser


def main():
    with open(sys.argv[1], 'r') as file:
        list_argument = file.readlines()
    # goes through every measurementID as sys.argv[1]
    for line in list_argument:

        print('Initializing render on map for a .se DNS')
        sys.argv[1] = line

        # creating timestamp for which measurements are wanted
        url = timestamped_url(sys.argv[1])
        sys.argv[1] = url

        tempUrl = sys.argv[1]
        sp = (tempUrl.split("?")[1]).split("&")
        start = sp[1].replace("start=", "")
        stop = sp[2].replace("stop=", "")

        measurementID = sys.argv[1].split('/')[6]

        print('Checking for previously rendered html file')
        htmlfile = measurementID + '-' + start + '-' + stop + '.html'
        list_of_files = os.listdir('/Users/nora.odelius/pycharmprojects/atlas-dns-chaos-2-rtt-countries/tests')
        if os.path.exists(htmlfile):
            webbrowser.open('file://' + os.path.realpath(htmlfile))
            print('html already exists')
            print('Opening file in webbrowser\n')
        else:
            substring_html = '.html'
            for item in list_of_files:
                if substring_html in item and measurementID in item:
                    os.remove(item)

            print('Html file did not exist')

            # convert start and stop to date
            print("\nMeasurement starts: " + str(datetime.utcfromtimestamp(float(start)).strftime('%Y-%m-%d %H:%M:%S')))
            print("Measurement end: " + str(datetime.utcfromtimestamp(float(stop)).strftime('%Y-%m-%d %H:%M:%S')))
            print("Measurement duration: " + str(int(stop) - int(start)) + " seconds, or  " +
                  str((int(stop) - int(start)) / 60) + " minutes\n")

            date = str(datetime.utcfromtimestamp(float(start)).strftime('%Y%m%d'))
            probeFile = date + "-probemetadata.json"


            print('Checking if probemetadata file for wanted day already exists')
            file_gz = date + '-probemetadata.json.gz'
            if os.path.exists(file_gz):
                print('Probemetadata already exists')


            else:
                print('Probemetadata did not exist\n')
                print("Reading probe metadata info for Ripe's FTP archive:")
                substring = 'probemetadata.json.gz'
                # removing already rendered statsCSV files form tests/
                for item in list_of_files:
                    if substring in item:
                        os.remove(item)
                geo_data = read_iso_countries_list()
                read_ripe_probe_list(date, probeFile, geo_data)

            url = sys.argv[1]
            atlas_results = measurementID + "-" + date + "-" + start + "-" + stop + "-atlas-results.csv"
            statsCSV = measurementID + "-" + date + "-" + start + "-" + stop + "-stats-country.csv"
            print('Checking if statsCSV and atlas_results already exists ')
            if os.path.exists(statsCSV):
                print('statsCSV file already exists')

                if os.path.exists(atlas_results):
                    print('Atlas_results file already exists')
                    print('Using files to render map')
                    rendermain(statsCSV)

                else:
                    print('Error: if a statsCSV file exists an atlas_results file should to! Check under tests/ folder')

            else:
                print('Wanted files did not exist')
                print('If WARNING occurs some measurements were empty. Do not panic')
                print("\nDownloading Ripe Atlas CHAOS Measurements and parsing it")

                list_of_files = os.listdir('/Users/nora.odelius/pycharmprojects/atlas-dns-chaos-2-rtt-countries/tests')
                substring_atlas = '-atlas-results.csv'
                substring_stats = '-stats-country.csv'

                # removing already rendered atlas_results files form tests/, not up-to-date measurements
                for item in list_of_files:
                    if substring_stats in item and measurementID in item:
                        os.remove(item)

                    if substring_atlas in item and measurementID in item:
                        os.remove(item)


                r = requests.get(url)
                measurements = json_parser(r.content.decode("utf-8"))
                probeDict = read_probe_data(probeFile + ".gz")

                csvFileFromAtlas = open(atlas_results, 'w')
                csvFileFromAtlas.write(
                    "ip_src,ip_dst,proto,hostnameBind,rtt,probeID,rcode,atlas_firmware,country,continent,subregion,probe_version\n")

                probes_not_found = 0
                for k in measurements:
                    # print("w")
                    probeID = k.split(",")[4]

                    trailler = "NA,NA"
                    try:
                        trailler = probeDict[probeID.strip()]
                    except:
                        # if trailler is empty the measurement had no data and the probe can't be found
                        probes_not_found += 1
                    csvFileFromAtlas.write(k + "," + trailler + "\n")
                print('Probes not found because of empty measurements:', probes_not_found)

                csvFileFromAtlas.close()
                print("DONE parsing results;\n")
                # list with measurements + trailler

                print("Generating statistics per country from ONLY FOR RCODE=0 (valid queries)")
                ccDict = dict()

                with open(atlas_results, 'r') as f:
                    lines = f.readlines()
                    for l in lines:

                        sp = l.split(",")
                    # if matches rcode and if the column value matches
                        if len(sp) == 10:
                        # could change if i want to
                        # filtering rcode 0
                        # varför måste rcode vara 0, vad är ens rcode
                            if sp[5].strip() == "0":
                                tempCountry = sp[7].strip()
                                tempRTT = float(sp[3].strip())

                                if tempCountry not in ccDict:
                                    tempArray = []
                                    tempArray.append(tempRTT)
                                    ccDict[tempCountry] = tempArray

                                else:
                                    tempArray = ccDict[tempCountry]
                                    tempArray.append(tempRTT)
                                    ccDict[tempCountry] = tempArray

                jsonDict = dict()
                print("Writing statistics per country in csv format into: " + statsCSV)
                with open(statsCSV, "w") as f:

                    f.write(
                        "country, nMesurements,meanRTT,percentile25RTT,medianRTT,percentile75RTT,percentile90RTT,maxRTT\n")
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
                            + "," + str(np.max(values)) + "\n")

                        tempDict = dict()

                        tempDict['nMeasurements'] = len(values)
                        tempDict['meanRTT'] = np.mean(values)
                        tempDict['percentile25RTT'] = np.percentile(values, 25)
                        tempDict['medianRTT'] = np.percentile(values, 50)
                        tempDict['percentile75RTT'] = np.percentile(values, 75)
                        tempDict['percentile90RTT'] = np.percentile(values, 95)
                        tempDict['maxRTT'] = np.max(values)

                        jsonDict[country] = tempDict
                print('Rendering map with parsed results from statsCSV file\n')
                rendermain(statsCSV)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Wrong number of parameters\n")
        print(str(len(sys.argv)))
        print("Usage:  python run.py $ATLAS_JSON_URL")
        print(
            "example: python3 ../chaos2countries/run.py  'https://atlas.ripe.net/api/v2/measurements/10310/results/?start=1544572800&stop=1544573100&format=json'")
    else:
        main()

    print('END')

