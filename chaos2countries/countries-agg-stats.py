
import sys
import numpy as np
import json




if __name__ == "__main__":


    if len(sys.argv)!=2:
        print("Wrong number of parameters\n")
        print(str(len(sys.argv)))
        print( "Usage:  python run.py $ATLAS_JSON_URL")
        print("example: python3 ../chaos2countries/run.py  'https://atlas.ripe.net/api/v2/measurements/10310/results/?start=1544572800&stop=1544573100&format=json'")



    ccDict = dict()
    with open(sys.argv[1], 'r') as f:
        lines = f.readlines()

        for l in lines:

            sp = l.split(",")
            # if matches rcode and if the column value matches
            if len(sp) == 13:
                # filtering rcode 0
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

    # output stats.csv
    jsonDict = dict()

    statsCSV = sys.argv[1] + "-stats-country.csv"
    statsJSON =sys.argv[1] + "-stats-country.json"

    print("Writing statistics per country in csv format into: " + statsCSV)
    with open(statsCSV, "w") as f:
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

            #   +","+  str(np.max(values)) + "," + str(np.percentile(values,90)) )

    print("Writing statistics per country in JSON format into: " + statsJSON)

    # create json format
    with open(statsJSON, "w") as f:
        json.dump(jsonDict, f)