# Atlas-dns-chaos-2-rtt-countries stats


## Summary 

   * This country does the following:
      1. Download and parses RIPE CHAOS atlas DNS measurements
      1. Produces a CSV file with the results, and enriches the results with:
         * probe's country
         * probe's continent
         * probe's subregion
         * probe's firmware version
         * probe's version (v1--v4)
      1. Generates *ready to use* aggregate stats file for the measurement, per country,
      in both JSON and CSV format, so OPS teams can easily integrate into their dashboards and 
      other graphs tools
      1. Plots a graph a world map with median RTT per country for the chaos measurements, see ``visualizations``.
      
      

## Demo
   * https://gmmoura.github.io/atlas-dns-chaos-2-rtt-countries/visualization/10310-1544572800-1544573100.html
 
 
## How-to for to generate the graph above

 ```bash
 
 #1. Clone the repository
 $ git clone https://github.com/gmmoura/atlas-dns-chaos-2-rtt-countries.git
 
 #go to tests dir
 $ cd atlas-dns-chaos-2-rtt-countries/tests
 
 #let's user a Atlas b-root measurement
 #you can get these from https://atlas.ripe.net/measurements/$MEASUREMENT_ID/#!download
 #WARNING: the variable start and stop below  are in UNI\nX timpestamp
 #and set how much data you want to collect
 #Start with a few minutes only
 
 #here we are having 300s only (stop - start)
 
 url="https://atlas.ripe.net/api/v2/measurements/10310/results/?start=1544572800&stop=1544573100&format=json"
 
 
 #read to run:
 $ python3  ../chaos2countries/run.py  $url
 
 #generate visualization
$ cd visualization/
$ python render.py ../tests/10310-20181212-1544572800-1544573100-stats-country.csv
$ firefox 10310-1544572800-1544573100.html
  ```   
  
### Output files


   * The demo below will produce the following output files on your local dir.
   * Results file will have the same prefix: ``PREFIX=$measuremnetID-dateStart-timestampStart-timestampEnd``
      * For example, for the ``$url`` above, these variables would be:
         *  ``measurementID=10310``
         *  ``dateStart=20181212`` (computed from ``timestampStart``)
         *  ``timestampStart=1544572800``
         *  ``timestampEnd=1544573100``
         
   For the example above, we have:      
   * ``10310-20181212-1544572800-1544573100-atlas-results.csv``: a csv file with the parsed results from Atlas' JSON. 
       * In other words,  a easier version to read from the ``$url`` above
       * enriched with metadata about gelocation and probes.
       * the name format is: `measuremnetID-dateStart-timestampStart-timestampEnd-atlas-results.csv`
       
   * ``10310-20181212-1544572800-1544573100-stats-country.csv``: aggregate RTT statistics,  per country, in CSV
   * ``10310-20181212-1544572800-1544573100-stats-country.json``: same as above, but in JSON


##  What can you do with this?
 
   * Use JSON or CSV output to produce nice World heatmaps or do other analysis
   
##  Generate world maps
   * Go to ``visualization/``
   * See demo https://gmmoura.github.io/atlas-dns-chaos-2-rtt-countries/visualization/10310-1544572800-1544573100.html
   
``` bash
$ cd visualization/
$ python render.py ../tests/10310-20181212-1544572800-1544573100-stats-country.csv
$ firefox 10310-1544572800-1544573100.html
```
