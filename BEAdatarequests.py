# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 11:05:16 2015

@author: pdougherty
"""

import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

BEA_key = ''

def getBEAData(dataset, keycode=None, table_id=None, freq='A', geo='MSA', first_year=1990, last_year=2014, fmt='json'):
    '''
    params:
        - user_key: BEA-supplied user identification API key
        - dataset: BEA dataset request. Reference: http://bea.gov/API/bea_web_service_api_user_guide.htm
        - keycode: dataset within data parent. May be from short list defined below, or from the list of accepted KeyCodes. Reference: http://bea.gov/API/bea_web_service_api_user_guide.htm
        - table_id: National data only. Standard NIPA table identifier.
        - freq: National data only. {'A':'Annual', 'Q':'Quarterly', 'M':'Monthly}
        - first_year: National data only. First year of data to retrieve
	- last_year: National data only. Last year of data to retrieve
        - fmt: Result format. Defaults to JSON, but also accepts XML.
    '''
    
    # Define the fan favorites
    keycode_dict = {'GMP':'GDP_MP', 'rGMP':'RGDP_MP', 'per capita rGMP':'PCRGDP_MP',
                    'PCI':'PCPI_MI', 'rPCI':'RPCPI_MI'}
    if keycode in keycode_dict.keys():
        keycode = keycode_dict[keycode]
    
    # Make GET request of BEA API
    if dataset=='RegionalData':
        p = requests.get('http://bea.gov/api/data/?UserID={user_key}&method=GetData&datasetname={dataset}&KeyCode={keycode}&GeoFips={geo}&ResultFormat={fmt}'.format(user_key=BEA_key, dataset=dataset, keycode=keycode, fmt=fmt, geo=geo))
    elif dataset=='NIPA':
        p = requests.get('http://www.bea.gov/api/data/?&UserID={user_key}&method=GetData&DataSetName={dataset}&Year={year_list}&tableID={table_id}&Frequency={freq}&&ResultFormat={fmt}'.format(user_key=BEA_key, dataset=dataset, year_list='{}'.format(range(first_year, last_year+1)).replace(' ', '').replace('[', '').replace(']', ''), table_id=table_id, freq=freq, fmt=fmt))
    try:
        p_text = p.json()
    except:
        p_text=p[0].json()
        
    df = pd.DataFrame(p_text['BEAAPI']['Results']['Data'])
    df.TimePeriod = pd.to_datetime(df.TimePeriod)
    
    # Clean GeoName to create Region field
    # Named for principal city in MSA area.
    # For example, "Baltimore-Columbia-Towson, MD" is listed as "Baltimore."
    try:
        df['Region'] = df.GeoName.str.split('-').str.get(0).str.split(',').str.get(0)
    except:
        pass
    
    # Clean GeoName to create State field
    try:
        df['State'] = df.GeoName.str.split(',').str.get(1).str.split(' ').str.get(1)
    except:
        pass
    
    # Change data type to float and int where necessary
    df.DataValue = df.DataValue.astype(float)
    df.GeoFips = df.GeoFips.astype(int)
    df['keycode'] = keycode

    return df
        
def plotBEAData(df, region, title):
    fig, ax = plt.subplots()
    
    for r in region:
        d = df[df.Region==r].sort('TimePeriod')
        plt.plot(d.TimePeriod, d.DataValue, label=r)
    
    # Make a list of y-axis labels
    labels = ax.get_yticks().tolist()
    # Format them with a comma and a dollar sign at the front, and drop any decimal places
    labels = ['$'+format(l, ',').split('.')[0] for l in labels]
    # Set the y-axis to be labeled with the now-formatted labels
    ax.set_yticklabels(labels)
    
    plt.ylabel('{}'.format(df.keycode[0]))
    plt.title('{}'.format(title))  
    plt.legend(loc=0)
    
    plt.tight_layout()
    
    return fig
    
def get5Yeargrowth(keycode):
    df = getBEAData('RegionalData', keycode)

    top25 = ['Atlanta', 'Baltimore', 'Boston', 'Charlotte', 'Chicago', 'Dallas', 'Denver', 'Detroit',
             'Houston', 'Los Angeles', 'Miami', 'Minneapolis', 'New York', 'Philadelphia', 'Phoenix',
             'Pittsburgh', 'Portland', 'Riverside', 'San Antonio', 'San Diego', 'San Francisco', 'St. Louis',
             'Seattle', 'Tampa', 'Washington']
         
    if len(top25)==25:
        ix = np.in1d(df.Region.ravel(), top25).reshape(df.Region.shape)
        df['Top25'] = np.where(ix, 1, 0)
    
    df = df.groupby(['Region', 'TimePeriod'])[['Region', 'DataValue']].sum().reset_index()
    r_pctchange = []
    for r in df.Region.unique():
        r_pctchange.append(df[df.Region==r].DataValue.pct_change(4))
        df = df.join(pd.concat(r_pctchange), rsuffix='_pctchange')
        
    for v in ['DataValue', 'DataValue_pctchange']:
        df = df[df.TimePeriod>'2012-12-31'].join(df[df.TimePeriod>'2012-12-31'][v].rank(ascending=False), rsuffix='_rank')
    
    df.rename(columns={'DataValue':keycode, 'DataValue_rank':keycode+'_rank', 'DataValue_pctchange':keycode+'_5yeargrowth', 'DataValue_pctchange_rank':keycode+'_5yeargrowth_rank'}, inplace=True)
    
    df25 = df[df.Top25==1]
    
    return df, df25