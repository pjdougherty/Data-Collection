# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 11:05:16 2015

@author: pdougherty

This script will pull data from available BEA sources. It returns a dataframe with datetime entries and cleaned region names for easy calling and plotting.
"""

import requests
import json
import pandas as pd
import re

def getBEAData(user_key, dataset, keycode, fmt='json'):
    '''
    params:
        - user_key: BEA-supplied user identification API key
        - dataset: BEA dataset request. Reference: http://bea.gov/API/bea_web_service_api_user_guide.htm
        - keycode: dataset within data parent. May be from short list defined below, or from the list of accepted KeyCodes. Reference: http://bea.gov/API/bea_web_service_api_user_guide.htm
        - fmt: Result format. Defaults to JSON, but also accepts XML.
    '''
    # Define the fan favorites
    keycode_dict = {'GMP':'GDP_MP', 'rGMP':'RGDP_MP', 'per capita rGMP':'PCRGDP_MP',
                    'PCI':'PCPI_MI', 'rPCI':'RPCPI_MI'}
    if keycode in keycode_dict.keys():
        keycode = keycode_dict[keycode]
    
    # Make GET request of BEA API
    p = requests.get('http://bea.gov/api/data/?UserID={user_key}&method=GetData&datasetname={dataset}&KeyCode={keycode}&ResultFormat={fmt}'.format(user_key=user_key, dataset=dataset, keycode=keycode, fmt=fmt))
    p_text = p.json()
    
    # Create dataframe from JSON output
    df = pd.DataFrame(p_text['BEAAPI']['Results']['Data'])
    # Turn BEA time period into datetime format
    df.TimePeriod = pd.to_datetime(df.TimePeriod)
    
    # Clean GeoName to create Region field
    # Named for principal city in MSA area.
    # For example, "Baltimore-Columbia-Towson, MD" is listed as "Baltimore."
    df['Region'] = df.GeoName.str.split('-').str.get(0).str.split(',').str.get(0)
    
    # Clean GeoName to create State field
    # May create combined fields for some cross-border metros
    # For example, "Washington-Arlington-Alexandrea, DC-MD-VA-WV" is listed as "DC-MD-VA-WV."
    df['State'] = df.GeoName.str.split(',').str.get(1).str.split(' ').str.get(1)
    
    return df
    
BEA_key = '' # Enter BEA API ID code

#Example: p = getBEAData(BEA_key, 'RegionalData', 'rGMP')