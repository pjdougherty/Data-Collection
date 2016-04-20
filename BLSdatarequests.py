# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 10:10:02 2015

@author: pdougherty

This script automates the collection of unemployment rate and employment data for the 25 largest US metros.

The BLS limits API users to request 25 series per query when using the unregistered API v1.0. Registration allows for querying 50 series. Other limits are shown here:
+-------------------------+--------------+--------------+
| Service		  | Version 2.0  | Version 1.0  |
|     			  | (Registered) |(Unregistered)|
+-------------------------+--------------+--------------+
| Daily query limits      |         500	 |          25  |
| Series per query limit  |	     50	 |	    25  |
| Years per query limit   |	     20	 |          10  |
| Net/Percent Changes	  |         Yes  |	    No  |
| Optional annual averages|         Yes	 |          No  |
| Series description      |              |              |
| information (catalog)	  |	    Yes  |          No  |
+-------------------------+--------------+--------------+
"""

import requests
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import seaborn as sb
import calendar

BLS_key=''

def getBLSData(geography, statistic, first_year, last_year, series_dict = {}, ann_avg='false'):
    '''
        The primary means for requesting data from the BLS API.
        parameters:
            - geography: Used for built-in series. 'Other' if a unique API call is needed.
            - statistic: used for built-in series. 'Other' if a unique API call is needed.
            - first_year: First year for which data is to be requested.
            - last_year: Last year for which data is to be requested.
            - series_dict: If unique call to the BLS is needed, pass a dictionary with this structure: {BLS series code: Geography name}
            - ann_avg: String argument for whether to include annual averages.
    ''''
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
            series = ['SMU04380600000000001','SMU06310800000000001','SMU06401400000000001',
                      'SMU06417400000000001','SMU06418600000000001','SMU08197400000000001',
                      'SMU11479000000000001','SMU12331000000000001','SMU12453000000000001',
                      'SMU13120600000000001','SMU17169800000000001','SMU24125800000000001',
                      'SMU25716500000000001','SMU26198200000000001','SMU27334600000000001',
                      'SMU29411800000000001','SMU36356200000000001','SMU37167400000000001',
                      'SMU41389000000000001','SMU42379800000000001','SMU42383000000000001',
                      'SMU48191000000000001','SMU48264200000000001','SMU48417000000000001',
                      'SMU53426600000000001','CEU0000000001']
            series_dict = {'SMU04380600000000001':'Phoenix','SMU06310800000000001':'Los Angeles','SMU06401400000000001':'Riverside',
                           'SMU06417400000000001':'San Diego','SMU06418600000000001':'San Francisco','SMU08197400000000001':'Denver',
                           'SMU11479000000000001':'Washington, DC','SMU12331000000000001':'Miami','SMU12453000000000001':'Tampa',
                           'SMU13120600000000001':'Atlanta','SMU17169800000000001':'Chicago','SMU24125800000000001':'Baltimore',
                           'SMU25716500000000001':'Boston','SMU26198200000000001':'Detroit','SMU27334600000000001':'Minneapolis',
                           'SMU29411800000000001':'St. Louis','SMU36356200000000001':'New York','SMU37167400000000001':'Charlotte',
                           'SMU41389000000000001':'Portland','SMU42379800000000001':'Philadelphia','SMU42383000000000001':'Pittsburgh',
                           'SMU48191000000000001':'Dallas','SMU48264200000000001':'Houston','SMU48417000000000001':'San Antonio',
                           'SMU53426600000000001':'Seattle', 'CEU0000000001':'US'}
        elif statistic =='Private Employment':
            series = ['SMU04380600500000001', 'SMU06310800500000001', 'SMU06401400500000001',
                      'SMU06417400500000001', 'SMU06418600500000001', 'SMU08197400500000001',
                      'SMU11479000500000001', 'SMU12331000500000001', 'SMU12453000500000001',
                      'SMU13120600500000001', 'SMU17169800500000001', 'SMU24125800500000001',
                      'SMU25716500500000001', 'SMU26198200500000001', 'SMU27334600500000001',
                      'SMU29411800500000001', 'SMU36356200500000001', 'SMU37167400500000001',
                      'SMU41389000500000001', 'SMU42379800500000001', 'SMU42383000500000001',
                      'SMU48191000500000001', 'SMU48264200500000001', 'SMU48417000500000001',
                      'SMU53426600500000001', 'CEU0500000001']
            series_dict = {'SMU04380600500000001':'Phoenix', 'SMU06310800500000001':'Los Angeles', 'SMU06401400500000001':'Riverside',
                      'SMU06417400500000001':'San Diego', 'SMU06418600500000001':'San Francisco', 'SMU08197400500000001':'Denver',
                      'SMU11479000500000001':'Washington, DC', 'SMU12331000500000001':'Miami', 'SMU12453000500000001':'Tampa',
                      'SMU13120600500000001':'Atlanta', 'SMU17169800500000001':'Chicago', 'SMU24125800500000001':'Baltimore',
                      'SMU25716500500000001':'Boston', 'SMU26198200500000001':'Detroit', 'SMU27334600500000001':'Minneapolis',
                      'SMU29411800500000001':'St. Louis', 'SMU36356200500000001':'New York', 'SMU37167400500000001':'Charlotte',
                      'SMU41389000500000001':'Portland', 'SMU42379800500000001':'Philadelphia', 'SMU42383000500000001':'Pittsburgh',
                      'SMU48191000500000001':'Dallas', 'SMU48264200500000001':'Houston', 'SMU48417000500000001':'San Antonio',
                      'SMU53426600500000001':'Seattle', 'CEU0500000001':'US'}
        elif statistic == 'CPI':
            series = ['CUUR0000SA0', 'CUURA101SA0', 'CUURA102SA0',
                      'CUURA103SA0', 'CUURA104SA0', 'CUURA207SA0',
                      'CUURA208SA0', 'CUURA209SA0', 'CUURA211SA0',
                      'CUURA311SA0', 'CUURA316SA0', 'CUURA318SA0',
                      'CUURA319SA0', 'CUURA320SA0', 'CUURA421SA0',
                      'CUURA422SA0', 'CUURA423SA0', 'CUURA424SA0',
                      'CUURA425SA0', 'CUURA433SA0',]
            series_dict = {'CUUR0000SA0':'US City Average', 'CUURA101SA0':'New York', 'CUURA102SA0':'Philadelphia',
                           'CUURA103SA0':'Boston', 'CUURA104SA0':'Pittsburgh', 'CUURA207SA0':'Chicago',
                           'CUURA208SA0':'Detroit', 'CUURA209SA0':'St. Louis', 'CUURA211SA0':'Minneapolis',
                           'CUURA311SA0':'Baltimore-Washington', 'CUURA316SA0':'Dallas', 'CUURA318SA0':'Houston',
                           'CUURA319SA0':'Atlanta', 'CUURA320SA0':'Miami', 'CUURA421SA0':'Los Angeles',
                           'CUURA422SA0':'San Francisco', 'CUURA423SA0':'Seattle', 'CUURA424SA0':'San Diego',
                           'CUURA425SA0':'Portland', 'CUURA433SA0':'Denver',}
    elif geography == 'All States':
        if statistic == 'Unemployment Rate':
            series = ['LAUST010000000000003','LAUST020000000000003','LAUST040000000000003', 'LAUST050000000000003','LAUST060000000000003',
                      'LAUST080000000000003','LAUST090000000000003', 'LAUST100000000000003', 'LAUST110000000000003', 'LAUST120000000000003',
                      'LAUST130000000000003', 'LAUST150000000000003', 'LAUST160000000000003', 'LAUST170000000000003', 'LAUST180000000000003',
                      'LAUST190000000000003', 'LAUST200000000000003', 'LAUST210000000000003', 'LAUST220000000000003', 'LAUST230000000000003',
                      'LAUST240000000000003', 'LAUST250000000000003', 'LAUST260000000000003', 'LAUST270000000000003', 'LAUST280000000000003',
                      'LAUST290000000000003', 'LAUST300000000000003','LAUST310000000000003','LAUST320000000000003','LAUST330000000000003',
                      'LAUST340000000000003', 'LAUST350000000000003', 'LAUST360000000000003', 'LAUST370000000000003', 'LAUST380000000000003',
                      'LAUST390000000000003','LAUST400000000000003','LAUST410000000000003','LAUST420000000000003','LAUST440000000000003',
                      'LAUST450000000000003','LAUST460000000000003','LAUST470000000000003','LAUST480000000000003','LAUST490000000000003',
                      'LAUST500000000000003','LAUST510000000000003','LAUST530000000000003','LAUST540000000000003','LAUST550000000000003',
                      'LAUST560000000000003','LAUST720000000000003']
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
    else:
        series_dict = series_dict
    
    headers = {'Content-type': 'application/json'}
    data = json.dumps({"seriesid": series_dict.keys(), "startyear":str(first_year), "endyear":str(last_year), 'registrationKey':BLS_key, 'annualaverage':'{}'.format(ann_avg)})
    # If you have a registration key from the BLS, pass it through above as 'registrationKey':''
    # Request a registration key to use the BLS API v2.0 here: http://data.bls.gov/registrationEngine/
    p = requests.post('http://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
    json_data = json.loads(p.text)
       
    dataframes = []
    for i in range(0, len(json_data['Results']['series'])):
        df = pd.DataFrame(json_data['Results']['series'][i]['data'])
        if len(df) > 0:
            try:
                df['location'] = series_dict[json_data['Results']['series'][i]['seriesID']]
            except:
                df['code'] = json_data['Results']['series'][i]['seriesID']
            # Create datetime field
            df['day'] = 01
            df['date'] = pd.to_datetime(df['year'].astype(int)*10000 + np.where(df.period!='M13', df.period.str[1:3].astype(int)*100, 100) + df.day, format='%Y%m%d')
            # Convert values to float
            df.value = df.value.astype(float)
            dataframes.append(df)

    # Add code to combine dataframes by appending all dataframes onto first dataframe
    df = pd.concat(dataframes)
    
    return df
    
def updateUnemploymentRate(month, year1, year2):
    '''
        Returns a dataframe with the unemployment rate for a given month in two years. Typically used for year t and t-1, to update the EAGB Data Center
        parameters:
            - month: Takes an integer value for month (1-2) or full name for a month as a string ('January')
            - year1: Takes an integer value for the year on which to sort the resulting dataframe. Typically the current or most recent year for which data is available.
            - year2: Takes an integer value for the year of comparison. Typically the year prior to the current or most recent year. 
    '''
    if month < 1 or month > 12:
        print 'This function only accepts month values 1-2 or full month names.'
    
    month_dict = {v:k for k,v in enumerate(calendar.month_name)}
    month = month_dict[month] if type(month)==str else month
    
    df = getBLSData('Top 25 Metros', 'Unemployment Rate', year1, year2)
    
    df = pd.merge(df[df.date=='{year1}-{month}-01'.format(year1=year1, month=month)][['location', 'value']],
                  df[df.date=='{year2}-{month}-01'.format(year2=year2, month=month)][['location', 'value']],
                  on='location', how='inner')
                  
    for i in ['_x', '_y']:
        df['value{}'.format(i)] = df['value{}'.format(i)]/100
        
    df['rank'] = df['value_x'].rank().astype(int)
    
    df.rename(columns={'value_x':'{}'.format(year1), 'value_y':'{}'.format(year2)}, inplace=True)
    
    return df

def updateEmploymentGrowth(year1, year2):
    df = getBLSData('Top 25 Metros', 'Employment', year1, year2, ann_avg='true')
    # Use only Annual Averages
    df = df[df.periodName=='Annual']

    # Match data years    
    ten_year = df[df.year==str(year1)].merge(df[df.year==str(year2)], on='location', suffixes=['_'+str(year1)[2:4], '_'+str(year2)[2:4]])
    one_year = df[df.year==str(year2-1)].merge(df[df.year==str(year2)], on='location', suffixes=['_'+str(year2-1)[2:4], '_'+str(year2)[2:4]])
    # Calculate percent change and rank it
    ten_year['percent_change'] = (ten_year['value_'+str(year2)[2:4]]-ten_year['value_'+str(year1)[2:4]])/ten_year['value_'+str(year1)[2:4]]
    ten_year['rank'] = ten_year.percent_change.rank(ascending=False)
    one_year['percent_change'] = (one_year['value_'+str(year2)[2:4]]-one_year['value_'+str(year2-1)[2:4]])/one_year['value_'+str(year2-1)[2:4]]
    one_year['rank'] = one_year.percent_change.rank(ascending=False)
    
    return ten_year, one_year

# Example: df = getBLSData('Top 25 Metros', 'Unemployment Rate', 2015, 2015)

# Add code to plot data from BLS request
def plotBLSData(geography, statistic, first_year, last_year, series = [], save=False):
    data = getBLSData(geography, statistic, first_year, last_year, series)
    
    fig, ax = plt.subplots()
    for loc in data[data.location!='US City Average'].location.unique():
        ax.plot(data[data.location==loc].date, data[data.location==loc].value, label=loc)
    ax.plot(data[data.location=='US City Average'].date, data[data.location=='US City Average'].value,
            c='#363737', alpha= 0.3, label='US City Average')
    # Manage titles
    plt.title(statistic+' Among '+geography+'\n'+str(first_year)+' - '+str(last_year-1))
    ax.set_ylabel(statistic)
    # Manage labels
    labels = ax.get_yticks().tolist()
    label_treatments = {'Unemployment Rate':[format(l).split('.')[0]+'%' for l in labels],
                        'Employment':[format(int(l)*1000, ',').split('.')[0] for l in labels],
                        'CPI':[format(l, ',').split('.')[0] for l in labels],
                        }
    labels = label_treatments[statistic]
    ax.set_yticklabels(labels)
    # Manage legend
    leg1 = ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    
    if save==True:
        plt.savefig(r'G:\Publications\Annual Regional Report\2015\{stat}_{geo}.png'.format(stat=statistic, geo=geography), bbox_inches='tight', dpi=600, alpha=True)
        plt.savefig(r'G:\Publications\Annual Regional Report\2015\{stat}_{geo}.eps'.format(stat=statistic, geo=geography), bbox_inches='tight', dpi=600, alpha=True)
        
    return