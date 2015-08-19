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
import matplotlib.pyplot as plt
import seaborn as sb

# See all available variables with series code listed
acs_var = pd.read_csv(r'G:\Data Center\Scripts\ACSvariables.csv')
auth_key = #

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
        
        df.reset_index(drop=True)
        
        dataframes.append(df)
        
    df = dataframes[0]
    for d in dataframes[1:]:
        pd.merge(df, d, on=geo_dict[geo])
        
    df.reset_index(drop=True)
    
    return df
    
# Example: df = getACSData(['DP02_0065PE'], 'msa', 2013, 5)