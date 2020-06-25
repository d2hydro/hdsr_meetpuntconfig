# -*- coding: utf-8 -*-
__title__ = 'histTags2mpt'
__description__ = 'to evaluate a HDSR FEWS-config with a csv with CAW histTags'
__version__ = '0.1'
__author__ = 'Daniel Tollenaar'
__author_email__ = 'daniel@d2hydro.nl'
__license__ = 'MIT License'
 
from fews_utilities import Config, xml_to_dict
import numpy as np
import pandas as pd
import logging
from openpyxl import load_workbook
import sys
import shutil

consistency_in = r'..\data\consistency.xlsx' #vorig resultaat-bestand
consistency_out = r'..\data\consistency_uit.xlsx' #pad naar nieuw resultaat-bestand
hist_tags_csv = r'..\data\get_series_startenddate_CAW_summary_total_sorted_20200405.csv' #csv met histTags
config_path = r'd:\FEWS\HDSR_WIS\CAW\config' #pad naar FEWS-config

#mpt_csv = r'd:\projecten\D2001.MeetpuntConfiguratie\01.data\HistTags\mpt_startenddate_total_pixml_transferdb_DT20200405.csv'
hist_tags_no_match_csv = r'd:\projecten\D2001.MeetpuntConfiguratie\01.data\HistTags\mpt_startenddate_total_pixml_transferdb_nomatch_DT20200405.csv'

#%% functies
def idmap2tags(row):
    '''functie voor het toevoegen van fews-locatie-ids aan de hist_tags data-frame'''
     
    exloc, expar = row['serie'].split('_',1)
    fews_locs = [col['internalLocation'] 
                   for col in id_total 
                   if col['externalLocation'] == exloc 
                   and col['externalParameter'] == expar]
    
    if len(fews_locs) == 0:
        fews_locs = np.NaN   
    elif len(fews_locs) > 1:
        logging.warning(('externe locatie/parameter: {exloc}/{expar}'
                         ' gekoppeld aan >1 fews locaties: {fews_locs}').format(
                             exloc = exloc , expar = expar , fews_locs = fews_locs))
    return fews_locs

#%% inlezen config-excel
try:
    shutil.copyfile(consistency_in, consistency_out)
except Exception as e: 
    logging.error(e) 
    sys.exit()

config_df = pd.read_excel(consistency_in,sheet_name=None)
if not 'histTag_ignore' in config_df.keys():
    logging.error('werkblad "histTag_ignore" mist in {}'.format(consistency_in))
    sys.exit()
    
# weggooien van alle output-sheets
config_df = {key:value for key,value in config_df.items() if key in ['inhoudsopgave','histTag_ignore']}

#%% inlezen idmap
config = Config(config_path)
id_total = []
for idmap in ['IdOPVLWATER',
              'IdOPVLWATER_HYMOS',
              'IdHDSR_NSC',
              'IdOPVLWATER_WQ',
              'IdGrondwaterCAW']:
    id_total += xml_to_dict(config.IdMapFiles[idmap])['idMap']['map'] 

#%% inlezen hist tags & ignore lijst
hist_tags_df = pd.read_csv(hist_tags_csv,
                           parse_dates = ['total_min_start_dt', 'total_max_end_dt'],
                           sep = ';')


#filteren hist_tags op alles wat niet in ignored staat
hist_tags_df = hist_tags_df[~hist_tags_df['serie'].isin(config_df['histTag_ignore']['UNKNOWN_SERIE'])]

#%% toevoegen lijsten met fews_locids aan his_tags_df        
hist_tags_df['fews_locid'] = hist_tags_df.apply(idmap2tags, axis=1)

#%% wegschrijven his-tags die niet zijn gematched
hist_tags_no_match_df = hist_tags_df[hist_tags_df['fews_locid'].isna()]
hist_tags_no_match_df = hist_tags_no_match_df.drop('fews_locid',axis=1)
hist_tags_no_match_df.columns = ['UNKNOWN_SERIE','STARTDATE','ENDDATE']
hist_tags_no_match_df = hist_tags_no_match_df.set_index('UNKNOWN_SERIE')
config_df['histTags_noMatch'] = hist_tags_no_match_df

#%% aanmaken van mpt_df vanuit de fews_locid lijsten in hist_tags_df
hist_tags_df = hist_tags_df[hist_tags_df['fews_locid'].notna()]
mpt_hist_tags_df = hist_tags_df.explode('fews_locid').reset_index(drop=True)

#%% bepalen minimale start en maximale eindtijd per fews_locid. 
mpt_df = pd.concat([mpt_hist_tags_df.groupby(['fews_locid'], sort=False)['total_min_start_dt'].min(),
                    mpt_hist_tags_df.groupby(['fews_locid'], sort=False)['total_max_end_dt'].max()],
                   axis=1)

mpt_df = mpt_df.sort_index(axis=0)
mpt_df.columns = ['STARTDATE','ENDDATE']
mpt_df.index.name = 'LOC_ID'

#%% alle hoofdlocaties waar geen histag op binnekomt toevoegen
kw_locs = list(mpt_df[mpt_df.index.str.contains('KW', regex=False)].index)
h_locs = np.unique(['{}0'.format(loc[0:-1]) for loc in kw_locs])
h_locs_missing = [loc for loc in h_locs if not loc in list(mpt_df.index)]
h_locs_df = pd.DataFrame(data={'LOC_ID' : h_locs_missing,
                               'STARTDATE' : [pd.NaT]*len(h_locs_missing),
                               'ENDDATE' :  [pd.NaT]*len(h_locs_missing)})
h_locs_df = h_locs_df.set_index('LOC_ID')

mpt_df = pd.concat([mpt_df,h_locs_df],axis=0)
#%% de start en eindtijd op de hoofdlocatie updaten met de min/max van de sublocatie
def update_hlocs(row):
    loc_id = row.name
    start_date = row['STARTDATE']
    end_date = row['ENDDATE']
    
    if loc_id in h_locs:
        start_date = mpt_df[mpt_df.index.str.contains(loc_id[0:-1])]['STARTDATE'].dropna().min()
        end_date = mpt_df[mpt_df.index.str.contains(loc_id[0:-1])]['ENDDATE'].dropna().max()
    
    return start_date, end_date 

mpt_df[['STARTDATE','ENDDATE']] = mpt_df.apply(update_hlocs,axis=1,result_type="expand")

mpt_df = mpt_df.sort_index()
config_df['mpt'] = mpt_df

#%% wegschrijven naar excel

book = load_workbook(consistency_out)
for worksheet in book.worksheets:
    if not worksheet.title in ['histTag_ignore','inhoudsopgave']:
        book.remove_sheet(worksheet)

xls_writer = pd.ExcelWriter(consistency_out, engine='openpyxl')
xls_writer.book = book

for sheet_name, df in config_df.items():
        if not sheet_name in ['histTag_ignore','inhoudsopgave']:
            df.to_excel(xls_writer, sheet_name=sheet_name, index=True)
            worksheet = xls_writer.sheets[sheet_name]
            for col in ['A','B','C']:
                worksheet.column_dimensions[col].width=20
                worksheet.auto_filter.ref = worksheet.dimensions
                
xls_writer.save()