import sys
import paths
import os, errno
import ntpath
from lxml import etree
from io import StringIO

#Channel configurations
Confs = [
    {'comType' : 'custom',
     'phits'   : '3',
     'channels' : [
         { 'from':'(0,0)', 'to':'(1,1)', 'bandwidth':'10'},
         { 'from':'(1,1)', 'to':'(0,1)', 'bandwidth':'10'},
         { 'from':'(0,1)', 'to':'(0,0)', 'bandwidth':'10'}
     ]},
    {'comType'  : 'all2all',
     'phits'    : '5',
     'reconfig' : '(0,0)'
    }
]
#Platform NoC configuration
NoC = {'width'       : '2',
       'height'      : '2',
       'topoType'    : 'bitorus',
       'routerDepth' : '3',
       'linkDepth'   : '0',
       'routerType'  : 'sync',
       'configurations' : Confs
}




# Create the root element and new document tree
nocsched = etree.Element('nocsched', version='0.1', nsmap={'xi': 'http://www.w3.org/2001/XInclude'})
doc = etree.ElementTree(nocsched)
# Description
desc = etree.SubElement(nocsched, 'description')
desc.text = 'NoC TDM scheduling'
#platform & topology
platform = etree.SubElement(nocsched, 'platform', width=NoC['width'], height=NoC['height'])
topology = etree.SubElement(platform, 'topology', topoType=NoC['topoType'],
                            routerDepth=NoC['routerDepth'], linkDepth=NoC['linkDepth'],
                            routerType=NoC['routerType'])
#application & configurations
configurations = etree.SubElement(etree.SubElement(nocsched, 'application'), 'configurations')
for commun in Confs:
    #iterate through keys (except "channels")
    communDict = {}
    communKeys = commun.keys()
    for key in communKeys:
        if(key != 'channels'):
            communDict[key] = commun[key]
    communication = etree.SubElement(configurations, 'communication', communDict)
    #add channels, if there are
    if 'channels' in communKeys:
        for channel in commun['channels']:
            channel = etree.SubElement(communication, 'channel', channel)

# Save to XML file
doc.write('output.xml', xml_declaration=True, encoding='utf-8')
