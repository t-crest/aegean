import sys
import paths
import os, errno
import ntpath
from lxml import etree
from io import StringIO

import json

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





''' ----------------------- MAPPING FX TO CORES ------------------------'''

#List of effects: S: samples processed per execution
FX = [
    { 'name' : 'DRY',          'S' : 1 },
    { 'name' : 'DRY_8SAMPLES', 'S' : 8 },
    { 'name' : 'DELAY',        'S' : 1 },
    { 'name' : 'OVERDRIVE',    'S' : 1 },
    { 'name' : 'WAHWAH',       'S' : 1 },
    { 'name' : 'CHORUS',       'S' : 1 },
    { 'name' : 'DISTORTION',   'S' : 1 },
    { 'name' : 'HP',           'S' : 1 },
    { 'name' : 'LP',           'S' : 1 },
    { 'name' : 'BP',           'S' : 1 },
    { 'name' : 'BR',           'S' : 1 },
    { 'name' : 'VIBRATO',      'S' : 1 },
    { 'name' : 'TREMOLO',      'S' : 1 },
]

#Read Audio APP JSON
with open ('audioApp.json') as audioApp_json:
    audioApp = json.load(audioApp_json)

#iterate chains
fx_id = 0
core  = 0
for chain in audioApp['chains']:
    #iterate FX
    chainFxList = []
    for fxname in chain['FX']:
        for fxi in range(1,len(FX)):
            #get fx_type and S
            if FX[fxi]['name'] == fxname:
                fx_type = fxi
                S = FX[fxi]['S']
                break
            print('FXI is ' + str(fxi))
            if fxi == len(FX):
                print('ERROR: EFFECT ' + fxname + ' DOES NOT EXIST')

        #store object
        fxObj = { 'fx_id' : fx_id,
                  'core'  : core,
                  'fx_type' : fx_type,
                  'xb_size' : S,
                  'yb_size' : S,
                  'S'       : S
        }
        chainFxList.append(fxObj)
        fx_id += 1
        core += 1


#Create FX_H file
FX_H = '''
//how many cores take part in the audio system
const int AUDIO_CORES = ''' + str(core)
FX_H += ''';
//how many effects are on the system in total
const int FX_AMOUNT = ''' + str(fx_id)
FX_H += ''';
// FX_ID | CORE | FX_TYPE | XB_SIZE | YB_SIZE | P (S) | IN_TYPE | OUT_TYPE | FROM_ID | TO_ID //
FX_SCHED[FX_AMOUNT][10] = {'''
#add files
for fx in chainFxList:
    FX_H += '''
    { ''' + str(fx['fx_id']) + ', ' + str(fx['core']) + ', ' + str(fx['fx_type']) + ', ' + \
    str(fx['xb_size']) + ', ' + str(fx['yb_size']) + ', ' + str(fx['S']) + ' },'
FX_H += '''
};'''


file = open("newfile.c", "w")
file.write(FX_H)
file.close()
