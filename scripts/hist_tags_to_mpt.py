# -*- coding: utf-8 -*-
"""
Created on Fri May 29 09:06:59 2020

@author: danie
"""
from fews_utilities import Config, xml_to_dict
import numpy as np
import pandas as pd
import logging

hist_tags_csv = r'd:\projecten\D2001.MeetpuntConfiguratie\01.data\HistTags\get_series_startenddate_CAW_summary_total_sorted_20200405.csv'
config_path = r'd:\FEWS\HDSR_WIS\CAW\config'
mpt_csv = r'd:\projecten\D2001.MeetpuntConfiguratie\01.data\HistTags\mpt_startenddate_total_pixml_transferdb_DT20200405.csv'
hist_tags_no_match_csv = r'd:\projecten\D2001.MeetpuntConfiguratie\01.data\HistTags\mpt_startenddate_total_pixml_transferdb_nomatch_DT20200405.csv'
hist_tags_ignore_csv = r'd:\projecten\D2001.MeetpuntConfiguratie\01.data\HistTags\mpt_referentie\mpt_startenddate_total_pixml_transferdb_ignore_DT.csv'


#%% functies
def idmap2tags(row):
    '''functie voor het toevoegen van fews-locatie-ids aan de hist_tags data-frame'''
    
    
    exloc, expar = row['serie'].split('_',1)
    fews_locs = [col['internalLocation'] 
                   for col in id_opvlwater 
                   if col['externalLocation'] == exloc 
                   and col['externalParameter'] == expar]
    
    if len(fews_locs) == 0:
        fews_locs = np.NaN   
    elif len(fews_locs) > 1:
        logging.warning(('externe locatie/parameter: {exloc}/{expar}'
                         ' gekoppeld aan >1 fews locaties: {fews_locs}').format(
                             exloc = exloc , expar = expar , fews_locs = fews_locs))
    
    return fews_locs

#%% inlezen idmap
config = Config(config_path)
id_opvlwater = xml_to_dict(config.IdMapFiles['IdOPVLWATER'])['idMap']['map']

#%% inlezen hist tags & ignore lijst
hist_tags_df = pd.read_csv(hist_tags_csv,
                           parse_dates = ['total_min_start_dt', 'total_max_end_dt'],
                           sep = ';')

hist_tags_ignore_df = pd.read_csv(hist_tags_ignore_csv,
                           sep = ';')

#filteren hist_tags op alles wat niet in ignored staat
hist_tags_df = hist_tags_df[~hist_tags_df['serie'].isin(hist_tags_ignore_df['UNKNOWN_SERIE'])]

#%% toevoegen lijsten met fews_locids aan his_tags_df        
hist_tags_df['fews_locid'] = hist_tags_df.apply(idmap2tags, axis=1)

#%% wegschrijven his-tags die niet zijn gematched
hist_tags_no_match_df = hist_tags_df[hist_tags_df['fews_locid'].isna()]
hist_tags_no_match_df = hist_tags_no_match_df.drop('fews_locid',axis=1)
hist_tags_no_match_df.columns = ['UNKNOWN_SERIE','STARTDATE','ENDDATE']
hist_tags_no_match_df = hist_tags_no_match_df.set_index('UNKNOWN_SERIE')
hist_tags_no_match_df.to_csv(hist_tags_no_match_csv,sep=';')

#%% aanmaken van mpt_df vanuit de fews_locid lijsten in hist_tags_df
hist_tags_df = hist_tags_df[hist_tags_df['fews_locid'].notna()]
mpt_hist_tags_df = hist_tags_df.explode('fews_locid').reset_index(drop=True)

#%% bepalen minimale start en maximale eindtijd per fews_locid. Deze series samenvoegen en wegschrijven
mpt_df = pd.concat([mpt_hist_tags_df.groupby(['fews_locid'], sort=False)['total_min_start_dt'].min(),
                    mpt_hist_tags_df.groupby(['fews_locid'], sort=False)['total_max_end_dt'].max()],
                   axis=1)
mpt_df.index.name = 'LOC_ID'
mpt_df = mpt_df.sort_index(axis=0)
mpt_df.columns = ['STARTDATE','ENDDATE']
mpt_df.to_csv(mpt_csv,sep=';')