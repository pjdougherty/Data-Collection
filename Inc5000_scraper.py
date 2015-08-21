# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 08:39:57 2015

@author: pdougherty
"""

import requests
import pandas as pd

def getInc5000(year):
    # Set current_company_id equal to that of the #1 company for the current year's Inc. 5000 List
    # If scraping a previous year, companies that end up on a newer list will cause the scraper
    # to jump up to the newer list.
    year_dict = 22890 # 2014 #1, Fuhu
    
    ''' Sample lists for dataframe headers'''
    '''
    key_list = [u'app_revenues_fouryearsago', u'city_display_name', u'twitter', u'app_employ_fouryearsago', u'rank',
                u'app_revenues_lastyear', u'linkedin', u'ifc_filelocation', u'id', u'app_employ_lastyear',
                u'ifc_twitter_handle', u'industry_id', u'ifc_business_model', u'ifc_url', u'next_id',
                u'description', u'ifc_state', u'ceo', u'metro_id', u'revenue_range', u'facebook', u'next_preview_text',
                u'industry_rank', u'address', u'next_badge_url', u'ifc_city', u'ifi_industry', u'country',
                u'ifc_company', u'state_rank', u'metro_rank', u'current_industry_rank', u'ifc_founded']
    years_list_current = ['ify_state_rank_2014', 'ify_employee_count_2014', 'ify_metro_rank_2014', 'ify_employee_count_previous_2014',
                             'ify_industry_rank_2014', 'ify_revenue_previous_2014', 'ify_year_2014', 'ify_rank_2014', 'ify_revenue_2014']
    years_list_prev = ['ify_state_rank_2013', 'ify_employee_count_2013', 'ify_metro_rank_2013', 'ify_employee_count_previous_2013',
                       'ify_industry_rank_2013', 'ify_revenue_previous_2013', 'ify_year_2013', 'ify_rank_2013', 'ify_revenue_2013']
    '''
    # Create empty lists for eventual pandas column names
    key_list, years_list_current, years_list_prev = [], [], []
    # Create empt list that all company data will be appended to
    all_co_data_list = []
    
    # Loop through the Inc. 5000
    # Company #5000 has no next_id value, so the loop will end
    while current_company_id:
        # Get company data as JSON
        current_company = requests.get('http://www.inc.com/rest/inc5000company/'+str(current_company_id)+'/full_list').json()
        
        # Extract company data to lists
        current_co_data = []
        current_co_years_data = []
        for key in current_company['data']:
            if key != 'years':
                current_co_data.append(current_company['data']['%s' % key])
            elif key == 'years':
                for k in current_company['data']['years'][0]:
                    current_co_years_data.append(current_company['data']['years'][0]['%s' % k])
                if len(current_company['data']['years']) > 1:
                    for k in current_company['data']['years'][1]:
                        current_co_years_data.append(current_company['data']['years'][1]['%s' % k])
                    
        # Set the current_company_id equal to the next id so it actually iterates
        current_company_id = current_company['data']['next_id']
                    
        # Combine lists and add it to the list of lists holding all company data
        company_data = current_co_data + current_co_years_data
        all_co_data_list.append(company_data)
        
    # Makes a list of eventual pandas headers
    key_list = list(current_company['data'].keys())
    key_list.remove('years')
    # Makes a list from nested elements of company data for more pandas headers
    years_list_current = []
    for i in list(current_company['data']['years'][0]):
        years_list_current.append(str(i)+'_current')
    if len(current_company['data']['years']) > 1:
        years_list_prev = []
        for i in current_company['data']['years'][1]:
            years_list_prev.append(str(i)+'_prev')
            
    # Create a dataframe from the long list
    inc5000 = pd.DataFrame(all_co_data_list)
    # Rename columns by simply replacing them with the list of columns created by the last company to loop
    inc5000.columns = [key_list+years_list_current+years_list_prev]
    
    return inc5000
    
# Example: getInc5000(2014)
