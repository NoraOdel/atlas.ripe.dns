import pandas as pd
import os


list_of_files = os.listdir('/Users/nora.odelius/pycharmprojects/atlas-dns-chaos-2-rtt-countries/tests')
substring = '-stats-country.csv'
for file in list_of_files:
    if substring in file:
        df = pd.read_csv(file)
        print(df)