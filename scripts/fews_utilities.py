# -*- coding: utf-8 -*-

__title__ = 'fews_utilities'
__description__ = 'to read a Deltares-FEWS config into Python'
__version__ = '0.1'
__author__ = 'Daniel Tollenaar'
__author_email__ = 'daniel@d2hydro.nl'
__license__ =  'MIT License'


from collections import defaultdict
import os
#import xml.etree.ElementTree as ET
from lxml import etree as ET
import geopandas as gpd
from shapely.geometry import Point

geo_datum = {'Rijks Driehoekstelsel':'epsg:28992'}

def xml_to_etree(xml_file):
    ''' parses an xml-file to an etree. ETree can be used in function etree_to_dict '''
    
    t = ET.parse(xml_file).getroot()
    
    return t

def etree_to_dict(t,section_start=None,section_end=None):
    ''' converts an etree to a dictionary '''
    
    if not isinstance(t,ET._Comment):
        
        d = {t.tag.rpartition('}')[-1]: {} if t.attrib else None}
        children = list(t)
        
        #get a section only
        if (not section_start == None) | (not section_end == None):
            if section_start:
                start = [idx for idx, child in enumerate(children) 
                               if isinstance(child,ET._Comment) 
                               if ET.tostring(child).decode("utf-8").strip() 
                               == section_start][0]
            else: start = 0
            if section_end:
                end = [idx for idx, child in enumerate(children) 
                           if isinstance(child,ET._Comment) 
                           if ET.tostring(child).decode("utf-8").strip() 
                           == section_end][0]
                if start < end:
                    children = children[start:end]
            else: children = children[start:]

        
        children = [child for child in children if not isinstance(child,ET._Comment)]
        
        if children:
            dd = defaultdict(list)
            #for dc in map(etree_to_dict, children):
            for dc in [etree_to_dict(child) for child in children]:
                for k, v in dc.items():
                    dd[k].append(v)
            
            d = {t.tag.rpartition('}')[-1]: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
        if t.attrib:
            d[t.tag.rpartition('}')[-1]].update((k, v) for k, v in t.attrib.items())
        if t.text:
            text = t.text.strip()
            if children or t.attrib:
                if text:
                  d[t.tag.rpartition('}')[-1]]['#text'] = text
            else:
                d[t.tag.rpartition('}')[-1]] = text
            
        return d

def xml_to_dict(xml_file,section_start=None,section_end=None):
    ''' converts an xml-file to a dictionary '''
    
    t = xml_to_etree(xml_file)
    d = etree_to_dict(t,section_start=section_start,section_end=section_end)
    
    return d

class Config:
    
    def _populate_files(self):
        '''build-in for loading all xml-files'''
        for (dirpath, dirnames, filenames) in os.walk(self.path):
            if not dirpath == self.path:
                prop = next((key for key in self.__dict__.keys() if key in dirpath),None)
                if not prop == None:
                    self.__dict__[prop].update({os.path.splitext(file_name)[0]:os.path.join(dirpath,file_name) for file_name in filenames})
    
    def _get_location_sets(self):
        '''build-in method to extract a dict of locationsets'''

        location_sets = xml_to_dict(self.RegionConfigFiles['LocationSets'])['locationSets']['locationSet']
        
        self.locationSets = {location_set['id']:{key:value for key, value in location_set.items() if not key == 'id'} 
                    for location_set in location_sets}
    
    def __init__(self,path):
        self.path = path
        
        #FEWS config dir-structure
        self.CoefficientSetsFiles = dict()
        self.DisplayConfigFiles = dict()
        self.FlagConversionsFiles = dict()
        self.IconFiles = dict()
        self.IdMapFiles = dict()
        self.MapLayerFiles = dict()
        self.ModuleConfigFiles = dict()
        self.ModuleDatasetFiles = dict()
        self.PiClientConfigFiles = dict()
        self.RegionConfigFiles = dict()
        self.ReportTemplateFiles = dict()
        self.RootConfigFiles = dict()
        self.SystemConfigFiles = dict()
        self.UnitConversionsFiles = dict()
        self.WorkflowFiles = dict()
        
        #populate config dir-structure
        self._populate_files()
        
        #get locationSets
        self._get_location_sets()

    def get_parameters(self,  dict_keys = 'groups'):
        '''method to extract a dictionary of parameter(groups) from a FEWS-config
        ToDo:
            - include parameters from CSV-files (support parametersCsvFile)
        '''
        parameters = xml_to_dict(self.RegionConfigFiles['Parameters'])['parameters']
        
        if dict_keys == 'groups':
            return {group['id']:{key:value for key, value in group.items() if not key == 'id'} 
                    for group in parameters['parameterGroups']['parameterGroup']}
        
        elif dict_keys == 'parameters':
            result = {}
            for group in parameters['parameterGroups']['parameterGroup']:
                if type(group['parameter']) == dict:
                    group['parameter'] = [group['parameter']]
                for parameter in group['parameter']:
                    result.update({parameter['id']:{}})
                    result[parameter['id']] = {key:value for key, value in parameter.items() 
                                               if not key == 'id'}
                    result[parameter['id']].update({key:value for key, value in group.items() if not key == 'parameter'})
                    result[parameter['id']]['groupId'] = result[parameter['id']].pop('id')
            return result
                

    def get_locations(self, location_set):
        '''method to extract a data-frame of locations from a fews locationSet
        
        parameters:
            location_set: (string) id of location-set to extract the locations rom
            
        ToDo:
        - support other than csvFile type locationSets
        - concatenate attribute-files
        - rename to internal attribute names
        
        '''
        if location_set in self.locationSets.keys():
            location_set = self.locationSets[location_set]
            if 'csvFile' in location_set.keys():
                file = location_set['csvFile']['file']
                if os.path.splitext(file)[1] == '':
                    file = '{}.csv'.format(file)
                file = os.path.join(self.path,'MapLayerFiles',file)
                x_attrib = location_set['csvFile']['x'].replace('%','')
                y_attrib = location_set['csvFile']['y'].replace('%','')
                if 'z' in location_set['csvFile'].keys():
                    z_attrib = location_set['csvFile']['y'].replace('%','')
                else: z_attrib = None
                
                gdf = gpd.read_file(file)
                
                if z_attrib:
                    gdf['geometry'] = gdf.apply((lambda x: Point(float(x[x_attrib]),
                                                                 float(x[y_attrib]),
                                                                 float(x[z_attrib]))),
                                                                    axis=1)
                else:
                    gdf['geometry'] = gdf.apply((lambda x: Point(float(x[x_attrib]),
                                                                 float(x[y_attrib]))),
                                                                    axis=1)
                crs = None
                if location_set['csvFile']['geoDatum'] in geo_datum.keys():
                    crs = geo_datum[location_set['csvFile']['geoDatum']]
                if not crs == None: gdf.crs = crs
                return gdf