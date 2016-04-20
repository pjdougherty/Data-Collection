# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 15:10:20 2015

@author: pdougherty

Retrieves American Community Survey Data for states, MSAs, the US, CSAs, and counties.
Data is available for 1-year and 5-year surveys. 1-year survey is released earlier. Series
requests may be passed as a list, so that the data parameter accepts ['series1', 'series2', ...].

Commonly used data series are:
Description                                                                  | ACS series code (2014) | ACS series code (2010)
-----------------------------------------------------------------------------+------------------------+------------------------
Educational Attainment of Population 25+, Graduate or Professional Degree, % | DP02_0065PE	      | 
Educational Attainment of Population 25+, Bachelor's or Higher, %            | DP02_0067PE	      | 
Median Household Income in the Past 12 Months                                | DP03_0062E	      | B19013_001E
Median Age of the Total Population                                           | DP05_0017E	      | B01002_001E
Total Population Aged 25 to 34 Years                                         | DP05_0009E	      | 
Total Population, All Ages						     | DP05_0001E	      | B01003_001E

"""

import requests
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb

# See all available variables with series code listed
acs_var = pd.read_csv(r'G:\Data Center\Scripts\ACSvariables.csv')
auth_key = ''
top25 = [12060, 12580, 14460, 16740, 16980, 19100, 19740, 19820, 26420, 31080, # 31080 = LA # Other lists have LA as 31100
        33100, 33460, 35620, 37980, 38060, 38300, 38900, 40140, 41700, 41740,
        41860, 41180, 42660, 45300, 47900]

def getACSData(data, geo, year, acs_year_period=5, a_key=auth_key, place='*', state='*', zipcode='*', county='*'):
    '''
    parameters:
        - data: list of data series for which to request information
        - geo: geography of data requested. 
        - year: ACS survey year
        - acs_year_period: 1-year or 5-year survey
        - a_key: ACS authorization key
        - place: optional parameter to call information for specific place
            If a place is specified, a state must be specified along with it.
        - state: optional parameter to call information for specific state, or for places, counties, and MSAs within a state
        - zipcode: optional parameter to call information for a specific ZIP code
        - county: optional parameter to call information for specific county
            County code must be passed as string to maintain placeholder 0s.
    '''
    if type(county) != str:
        print 'County parameter must be passed as string to maintain placeholder 0s.'
    else:
        pass
    
    acs_dict = {1:'acs1', 5:'acs5'}
    geo_dict = {'state':'state:{}'.format(state), 'msa':'metropolitan statistical area/micropolitan statistical area:*',
                'us':'us:*', 'csa':'combined statistical area:*', 'county':'county:{}'.format(county),
                'place':'place:{}'.format(place), 'zipcode':str(zipcode)}
    if geo not in ['zipcode', 'us']:
        area = geo_dict[geo]+'&in=state:{}'.format(state)
    else:
        area = geo_dict[geo]
        
    dataframes = []           
    for s in data:
        p = requests.get('http://api.census.gov/data/'+str(year)+'/'+str(acs_dict[acs_year_period])+'/profile?get=NAME,'+s+'&for='+area+'&key='+a_key)
        json_data = json.loads(p.text)
    
        df = pd.DataFrame(json_data)
        df.rename(columns={0:df[0].loc[0], 1:df[1].loc[0], 2:geo}, inplace=True)
        df.drop(0, inplace=True)
        
        df['{}'.format(s)] = df['{}'.format(s)]#.astype(float)
        df[geo] = df[geo].astype(int)
        
        df = df.reset_index(drop=True)
        
        dataframes.append(df)
            
    df = dataframes[0]
    for d in dataframes[1:]:
        df = pd.merge(df, d, on='NAME', how='left', suffixes=['', '_r'])
        #df.drop('NAME_r', inplace=True, axis=1)
        
    df = df.reset_index(drop=True)
    ix = np.in1d(np.array(df[geo]).ravel(), top25).reshape(df[geo].shape)
    df['top25'] = np.where(ix, 1, 0)
    
    return df
    
def getACSData10(data, geo, year, acs_year_period=5, a_key=auth_key, place='*', state='*', zipcode='*', county='*'):
    '''
    parameters:
        - data: list of data series for which to request information
        - geo: geography of data requested. 
        - year: ACS survey year
        - acs_year_period: 1-year or 5-year survey
        - a_key: ACS authorization key
        - place: optional parameter to call information for specific place
            If a place is specified, a state must be specified along with it.
        - state: optional parameter to call information for specific state, or for places, counties, and MSAs within a state
        - zipcode: optional parameter to call information for a specific ZIP code
        - county: optional parameter to call information for specific county
            County code must be passed as string to maintain placeholder 0s.
    '''
    if type(county) != str:
        print 'County parameter must be passed as string to maintain placeholder 0s.'
    else:
        pass
    
    acs_dict = {1:'acs1', 5:'acs5'}
    geo_dict = {'state':'state:{}'.format(state), 'msa':'metropolitan statistical area/micropolitan statistical area:*',
                'us':'us:*', 'csa':'combined statistical area:*', 'county':'county:{}'.format(county),
                'place':'place:{}'.format(place), 'zipcode':str(zipcode)}
    if geo not in ['zipcode', 'us']:
        area = geo_dict[geo]+'&in=state:{}'.format(state)
    else:
        area = geo_dict[geo]
        
    dataframes = []           
    for s in data:
        p = requests.get('http://api.census.gov/data/'+str(year)+'/'+str(acs_dict[acs_year_period])+'?key={key}&get={s},NAME&for={area}'.format(key=auth_key, s=s, area=area))
        json_data = json.loads(p.text)
    
        df = pd.DataFrame(json_data)
        df.rename(columns={0:df[0].loc[0], 1:df[1].loc[0], 2:geo}, inplace=True)
        df.drop(0, inplace=True)
        
        df['{}'.format(s)] = df['{}'.format(s)]#.astype(float)
        df[geo] = df[geo].astype(int)
        
        df = df.reset_index(drop=True)
        
        dataframes.append(df)
            
    df = dataframes[0]
    for d in dataframes[1:]:
        df = pd.merge(df, d, on='NAME', how='left', suffixes=['', '_r'])
        #df.drop('NAME_r', inplace=True, axis=1)
        
    df = df.reset_index(drop=True)
    ix = np.in1d(np.array(df[geo]).ravel(), top25).reshape(df[geo].shape)
    df['top25'] = np.where(ix, 1, 0)
    
    return df
    
# Example: df = getACSData(['DP02_0065PE'], 'msa', 2013, 5)

''' For rapid EAGB use '''

def getEdAttainRank(year, year_series):
    df = getACSData(['DP02_0065PE', 'DP02_0067PE'], 'msa', year, year_series)
    top25 = [12060, 12580, 14460, 16740, 16980, 19100, 19740, 19820, 26420, 31080, # 31080 = LA # Other lists have LA as 31100
             33100, 33460, 35620, 37980, 38060, 38300, 38900, 40140, 41700, 41740,
             41860, 41180, 42660, 45300, 47900]
    ix = np.in1d(np.array(df.msa).ravel(), top25).reshape(df.msa.shape)
    df['top25'] = np.where(ix, 1, 0)
        
    # Get US average too
    df_us = getACSData(['DP02_0065PE', 'DP02_0067PE'], 'us', year, year_series)
    df_us.rename(columns={'us':'msa'}, inplace=True)
    df_us['top25'] = 1
    
    # Append US to MSAs
    df = df.append(df_us)
    
    df = df[df.top25==1]
    df = df.sort('DP02_0065PE')
    df = df.reset_index(drop=True) # Sorted by % with grad or professional degree
    
    return df
    
def getMHHI(year, year_series):
    df = getACSData(['DP03_0062E'], 'msa', year, year_series)
    top25 = [12060, 12580, 14460, 16740, 16980, 19100, 19740, 19820, 26420, 31080, # 31080 = LA # Other lists have LA as 31100
             33100, 33460, 35620, 37980, 38060, 38300, 38900, 40140, 41700, 41740,
             41860, 41180, 42660, 45300, 47900]
    ix = np.in1d(np.array(df.msa).ravel(), top25).reshape(df.msa.shape)
    df['top25'] = np.where(ix, 1, 0)
        
    # Get US average too
    df_us = getACSData(['DP03_0062E'], 'us', year, year_series)
    df_us.rename(columns={'us':'msa'}, inplace=True)
    df_us['top25'] = 1
    
    # Append US to MSAs
    df = df.append(df_us)
    
    df = df[df.top25==1]
    df = df.sort('DP03_0062E')
    df = df.reset_index(drop=True) # Sorted by % with grad or professional degree
    
    return df
    
def getMedianAge(year, year_series):
    df = getACSData(['DP05_0017E'], 'msa', year, year_series)
    top25 = [12060, 12580, 14460, 16740, 16980, 19100, 19740, 19820, 26420, 31080, # 31080 = LA # Other lists have LA as 31100
             33100, 33460, 35620, 37980, 38060, 38300, 38900, 40140, 41700, 41740,
             41860, 41180, 42660, 45300, 47900]
    ix = np.in1d(np.array(df.msa).ravel(), top25).reshape(df.msa.shape)
    df['top25'] = np.where(ix, 1, 0)
        
    # Get US average too
    df_us = getACSData(['DP05_0017E'], 'us', year, year_series)
    df_us.rename(columns={'us':'msa'}, inplace=True)
    df_us['top25'] = 1
    
    # Append US to MSAs
    df = df.append(df_us)
    
    df = df[df.top25==1]
    df = df.sort('DP05_0017E')
    df = df.reset_index(drop=True) # Sorted by % with grad or professional degree
    
    return df