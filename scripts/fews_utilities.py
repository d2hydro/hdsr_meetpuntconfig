# -*- coding: utf-8 -*-

__title__ = 'fews_utilities'
__description__ = 'to read a Deltares-FEWS config into Python'
__version__ = '0.1'
__author__ = 'Daniel Tollenaar'
__author_email__ = 'daniel@d2hydro.nl'
__license__ =  'MIT License'


from collections import defaultdict
import os
import xml.etree.ElementTree as ET


def xml_to_etree(xml_file):
    ''' parses an xml-file to an etree. ETree can be used in function etree_to_dict '''
    
    t = ET.parse(xml_file).getroot()
    
    return t

def etree_to_dict(t):
    ''' converts an etree to a dictionary '''
    
    d = {t.tag.rpartition('}')[-1]: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
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

def xml_to_dict(xml_file):
    ''' converts an xml-file to a dictionary '''
    
    t = xml_to_etree(xml_file)
    d = etree_to_dict(t)
    
    return d

class Config:
    
    def _populate_files(self):
        for (dirpath, dirnames, filenames) in os.walk(self.path):
            if not dirpath == self.path:
                prop = next((key for key in self.__dict__.keys() if key in dirpath),None)
                if not prop == None:
                    self.__dict__[prop].update({os.path.splitext(file_name)[0]:os.path.join(dirpath,file_name) for file_name in filenames})
    
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
