# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import requests
import json
import pandas as pd
import time
import matplotlib.pyplot as plt

states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID',
          'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO',
          'MT', 'NE', 'NV', 'NJ', 'NH', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA',
          'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']                           

def getVC_all_states(year1, year2, industry):
    '''
        Fetches PricewaterhouseCoopers MoneyTree venture capital historical data for a PWC-defined industry over a period of time. Data is collected for Q1 to Q4 of the years passed as arguments.
        Parameters:
            - year1: The first year of interest
            - year2: The last year of interest
            - industry: Industry name as recognized by PricewaterhouseCoopers MoneyTree
        
        Accepted industry arguments are: All Industries, Biotechnology, Business Products and Services, Computers and Peripherals, Consumer Products and Services, Electronics/Instrumentation, Financial Services, Healthcare Services, Industrial/Energy, IT Services, Media and Entertainment, Medical Devices and Equipment, Networking and Equipment, Other, Retailing/Distribition, Semiconductors, Software, and Telecommunications.
    '''
    month_lookup = pd.DataFrame({1:2, 2:5, 3:8, 4:11},index=[0]).T.reset_index().rename(columns={'index':'quarter', 0:'month'})
    industry_lookup={'All Industries':'', 'Biotechnology':'4000', 'Business Products and Services':'9300', 'Computers and Peripherals':'2200',
                     'Consumer Products and Services':'7400', 'Electronics/Instrumentation':'3400', 'Financial Services':'9200',
                     'Healthcare Services':'5400', 'Industrial/Energy':'6000', 'IT Services':'2600', 'Media and Entertainment':'7100',
                     'Medical Devices and Equipment':'5100', 'Networking and Equipment':'1500', 'Other':'9900', 'Retailing/Distribition':'7200',
                     'Semiconductors':'3300', 'Software':'2700', 'Telecommunications':'1200'}
    
    states_dfs = []
    
    for state in states:
        response = requests.post('https://www.pwcmoneytree.com/HistoricTrends/GetJSONHistTrendWithParams',
                                 headers={},
                            data={'Qtr2':'{}-4'.format(year2), 'Qtr1':'{}-1'.format(year1), 'CompanyIndustry':'{}'.format(industry_lookup[industry]), 
                                  'CompanyState':'{}'.format(state), 'DrillDownSequence':'Qtr:'})
                                  
        if len(response.json())>0:
            try:
                state_df = pd.DataFrame(response.json())
                state_df.rename(columns={'XAxisTic':'period', 'YBar':'dollars', 'YLine':'deals'}, inplace=True)
                state_df['state'] = state
                # Add year
                state_df['year'] = state_df.period.str.split('-').str.get(0).astype(int)
                # Add month
                state_df['quarter'] = state_df.period.str.split('-').str.get(1).astype(int)
                
                '''
                state_df = pd.merge(state_df, month_lookup, on='quarter', how='left')
                # Add datetime
                print state_df.head(1)
                state_df['date'] = pd.to_datetime((state_df.year*10000)+(state_df.month*100)+01, format='%Y%m%d')
                '''
                
                states_dfs.append(state_df)
            except:
                print 'No dataframe created for {}'.format(state)
                
        time.sleep(0.25)
        
    vc = pd.concat(states_dfs)
    
    vc = pd.merge(vc, month_lookup, on='quarter', how='inner')
    vc['date'] = pd.to_datetime(vc.year*10000+vc.month*100+01, format='%Y%m%d')
    
    vc['industry'] = industry
    
    vc[['date', 'state', 'dollars', 'deals', 'year', 'quarter', 'industry',]]
    
    return vc
    
def compare_states(df, plot=False):
    '''
        Takes a dataframe of venture capital investment in a single industry and compares the total investment and deals over the time period covered by the dataframe among all states. Optionally produces a bar plot with two subplots showing the top 5 states for dollars and deals in this industry.
        Parameters:
            - df: dataframe of venture capital information. Set up to work smoothly with dataframes returned by getVC_allstates()
            - plot: optional argument for producing a plot of the top 5 states for venture capital
    '''
    if len(df.industry.unique()) > 1:
        print 'Dataframe must be limited to a single industry.'
    
    comp = df.groupby(['state']).sum().reset_index()
    
    comp['dollars_rank'] = comp.dollars.rank(ascending=False)
    comp['deals_rank'] = comp.deals.rank(ascending=False)
    
    if plot==True:
        fig, (ax1, ax2) = plt.subplots(1,2, figsize=(9,5))
        # top 5 states for vc investment
        ax1.bar(range(0,5), comp.sort('dollars', ascending=False).dollars.values[0:5],
                linewidth=0, align='center', zorder=2)
        ax1.set_xticks([i+1 for i in ax1.get_xticks().tolist()])
        ax1.set_xticklabels(comp.sort('dollars',ascending=False).state.values[0:5], ha='center')
        ax1.set_yticklabels(['$'+format(l/1000000, ',').split('.')[0] for l in ax1.get_yticks().tolist()])
        ax1.set_ylabel('Millions of Dollars')
        ax1.set_title('Top 5 States for\n{industry} Venture Capital Investment\n{year1}-{year2}'.format(industry=df.industry.unique()[0], year1=min(df.year.unique()), year2=max(df.year.unique())),
                      fontsize=10)
        ax1.set_xlim(-1,5)
        ax1.grid(True, which='major', axis='y', zorder=-1)
        # top 5 states for deals
        ax2.bar(range(0,5), comp.sort('deals', ascending=False).deals.values[0:5],
                linewidth=0, align='center', zorder=2)
        ax2.set_xticks([i+1 for i in ax2.get_xticks().tolist()])
        ax2.set_xticklabels(comp.sort('deals',ascending=False).state.values[0:5], ha='center')
        ax2.set_yticklabels([format(l, ',').split('.')[0] for l in ax2.get_yticks().tolist()])
        ax2.set_ylabel('Number of Deals')
        ax2.set_title('Top 5 States for\n{industry} Venture Capital Deals\n{year1}-{year2}'.format(industry=df.industry.unique()[0], year1=min(df.year.unique()), year2=max(df.year.unique())),
                      fontsize=10)
        ax2.set_xlim(-1,5)
        ax2.grid(True, which='major', axis='y', zorder=-1)
        # make it pretty automatically
        plt.tight_layout()
    else:
        fig = None
    
    return comp, fig