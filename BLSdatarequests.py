# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 10:10:02 2015

@author: pdougherty

This script automates the collection of unemployment rate and employment data for the 25 largest US metros.

The BLS limits API users to request 25 series per query when using the unregistered API v1.0. Registration allows for querying 50 series. Other limits are shown here:
Service			Version 2.0	Version 1.0
			(Registered)	(Unregistered)
Daily query limit		500		25
Series per query limit		50		25
Years per query limit		20		10
Net/Percent Changes		Yes		No
Optional annual averages	Yes		No
Series description
information (catalog)		Yes		No
"""

import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import seaborn as sb

def getBLSData(geography, statistic, first_year, last_year, series = []):
    if geography == 'Top 25 Metros':
        if statistic == 'Unemployment Rate':
            series = ['LAUMT043806000000003','LAUMT063108000000003','LAUMT064014000000003',
                      'LAUMT064174000000003','LAUMT064186000000003','LAUMT081974000000003',
                      'LAUMT114790000000003','LAUMT123310000000003','LAUMT124530000000003',
                      'LAUMT131206000000003','LAUMT171698000000003','LAUMT241258000000003',
                      'LAUMT257165000000003','LAUMT261982000000003','LAUMT273346000000003',
                      'LAUMT294118000000003','LAUMT363562000000003','LAUMT371674000000003',
                      'LAUMT413890000000003','LAUMT423798000000003','LAUMT423830000000003',
                      'LAUMT481910000000003','LAUMT482642000000003','LAUMT484170000000003',
                      'LAUMT534266000000003','LNU04000000']
            series_dict = {'LAUMT043806000000003':'Phoenix','LAUMT063108000000003':'Los Angeles','LAUMT064014000000003':'Riverside',
                           'LAUMT064174000000003':'San Diego','LAUMT064186000000003':'San Francisco','LAUMT081974000000003':'Denver',
                           'LAUMT114790000000003':'Washington, DC','LAUMT123310000000003':'Miami','LAUMT124530000000003':'Tampa',
                           'LAUMT131206000000003':'Atlanta','LAUMT171698000000003':'Chicago','LAUMT241258000000003':'Baltimore',
                           'LAUMT257165000000003':'Boston','LAUMT261982000000003':'Detroit','LAUMT273346000000003':'Minneapolis',
                           'LAUMT294118000000003':'St. Louis','LAUMT363562000000003':'New York','LAUMT371674000000003':'Charlotte',
                           'LAUMT413890000000003':'Portland','LAUMT423798000000003':'Philadelphia','LAUMT423830000000003':'Pittsburgh',
                           'LAUMT481910000000003':'Dallas','LAUMT482642000000003':'Houston','LAUMT484170000000003':'San Antonio',
                           'LAUMT534266000000003':'Seattle','LNU04000000':'US'}
        elif statistic == 'Employment':
            series = []
            series_dict = {'':'', '':''}
    elif geography == 'All States':
        if statistic == 'Unemployment Rate':
            series = []
            series_dict = {'':'', '':''}
        elif statistic == 'Employment':
            series = []
            series_dict = {'':'', '':''}
    elif geography == 'All Metros':
        if statistic == 'Unemployment Rate':
            series = []
            series_dict = {'':'', '':''}
        elif statistic == 'Employment':
            series = []
            series_dict = {'':'', '':''}
    
    headers = {'Content-type': 'application/json'}
    data = json.dumps({"seriesid": series, "startyear":str(first_year), "endyear":str(last_year)})
    # If you have a registration key from the BLS, pass it through above as 'registrationKey':''
    # Request a registration key to use the BLS API v2.0 here: http://data.bls.gov/registrationEngine/
    p = requests.post('http://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
    json_data = json.loads(p.text)

    dataframes = []
    for i in range(0, len(json_data['Results']['series'])):
        df = pd.DataFrame(json_data['Results']['series'][i]['data'])
        df['location'] = series_dict[json_data['Results']['series'][i]['seriesID']]
        # Create datetime field
        df['day'] = 01
        df['date'] = pd.to_datetime(df.year.astype(int)*10000 + df.period.str[1:3].astype(int)*100 + df.day, format='%Y%m%d')
        # Convert values to float
        df.value = df.value.astype(float)
        dataframes.append(df)

    # Append all dataframes onto first dataframe
    df = dataframes[0]
    for i in dataframes[1:]:
        df = df.append(i)
        
    return df

# Example: dataframes = getBLSData('Top 25 Metros', 'Unemployment Rate', 2012, 2015)

# Add code to plot data from BLS request
