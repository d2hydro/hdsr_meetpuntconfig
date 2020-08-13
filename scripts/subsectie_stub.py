# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 12:01:01 2020

@author: danie
"""

from lxml import etree as ET
from fews_utilities import etree_to_dict

xml_file = r'd:\\FEWS\\HDSR_WIS\\CAW\\config\\IdMapFiles\\IdOPVLWATER.xml'

result = {'MSW':[],
           'KUNSTWERK':[]}

t = ET.parse(xml_file).getroot()

#%%
for child in t:
    if isinstance(child,ET._Comment):
        comment = ET.tostring(child)
        if '<!--MSW' in comment.decode("utf-8"):
            section = 'MSW'
        elif '<!--KUNSTWERK' in comment.decode("utf-8"):
            section = 'KUNSTWERK'
    else:
        result[section].append(child)

#%%
for key, value in result.items():
    for child in t:
        t.remove(child)
    for child in result[key]:
        t.append(child)
    result[key] = etree_to_dict(t)