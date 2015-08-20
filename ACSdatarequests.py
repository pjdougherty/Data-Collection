# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 15:10:20 2015

@author: pdougherty

Retrieves American Community Survey Data for states, MSAs, the US, CSAs, and counties.
Data is available for 1-year and 5-year surveys. 1-year survey is released earlier. Series
requests may be passed as a list, so that the data parameter accepts ['series1', 'series2', ...].

Commonly used data series are:
Educational Attainment of Population 25+, Graduate or Professional Degree, % | DP02_0065PE
Educational Attainment of Population 25+, Bachelor's or Higher, %            | DP02_0067PE
"""

import requests
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb

# See all available variables with series code listed
acs_var = pd.read_csv('https://github.com/pjdougherty/Data-Collection/blob/master/ACSvariables.csv')
auth_key = #
# Register with the Census Bureau to receive an API key that can be used to request data via this API

def getACSData(data, geo, year, acs_year_period, a_key=auth_key):
    acs_dict = {1:'acs1', 5:'acs5'}
    geo_dict = {'state':'state', 'msa':'metropolitan statistical area/micropolitan statistical area',
                'us':'us', 'csa':'combined statistical area', 'county':'county'}
                
    dataframes = []           
    for s in data:
        p = requests.get('http://api.census.gov/data/'+str(year)+'/'+str(acs_dict[acs_year_period])+'/profile?get=NAME,'+s+'&for='+geo_dict[geo]+':*&key='+a_key)
        json_data = json.loads(p.text)
    
        df = pd.DataFrame(json_data)
        df.rename(columns={0:df[0].loc[0], 1:df[1].loc[0], 2:geo}, inplace=True)
        df.drop(0, inplace=True)
        
        df['%s' % s] = df['%s' % s].astype(float)
        df[geo] = df[geo].astype(int)
        
        df = df.reset_index(drop=True)
        
        dataframes.append(df)
            
    df = dataframes[0]
    for d in dataframes[1:]:
        df = pd.merge(df, d, on=geo, how='left', suffixes=['', '_r'])
        df.drop('NAME_r', inplace=True, axis=1)
        
    df = df.reset_index(drop=True)
    
    return df
    
# Example: df = getACSData(['DP02_0065PE'], 'msa', 2013, 5)

''' For rapid ranking of the 25 Largest US metros and the US average '''

def getEdAttainRank():
    df = getACSData(['DP02_0065PE', 'DP02_0067PE'], 'msa', 2013, 5)
    top25 = [12060, 12580, 14460, 16740, 16980, 19100, 19740, 19820, 26420, 31080, # 31080 = LA # Other lists have LA as 31100
             33100, 33460, 35620, 37980, 38060, 38300, 38900, 40140, 41700, 41740,
             41860, 41180, 42660, 45300, 47900]
    ix = np.in1d(np.array(df.msa).ravel(), top25).reshape(df.msa.shape)
    df['top25'] = np.where(ix, 1, 0)
        
    # Get US average too
    df_us = getACSData(['DP02_0065PE', 'DP02_0067PE'], 'us', 2013, 5)
    df_us.rename(columns={'us':'msa'}, inplace=True)
    df_us['top25'] = 1
    
    # Append US to MSAs
    df = df.append(df_us)
    
    df = df[df.top25==1]
    df = df.sort('DP02_0065PE')
    df = df.reset_index(drop=True) # Sorted by % with grad or professional degree
    
    return df
