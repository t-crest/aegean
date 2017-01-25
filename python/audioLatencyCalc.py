import sys
import paths
import os, errno
import ntpath
from paths import Paths
from lxml import etree
from io import StringIO

import json
import math

#read json
with open (sys.argv[1]) as lat_json:
    latList = json.load(lat_json)

#see if reconfiguration is enabled
if sys.argv[2] == '1':
    reconfig = True
else:
    reconfig = False

projectname = ntpath.basename(sys.argv[3])
projectname = os.path.splitext(projectname)[0]
p = Paths(projectname)
xml_path = p.TMP_BUILD_PATH
#list of xml objects
xmlList = []
for modeInd in range(0, len(latList['modes'])):
    xmlObj = etree.parse(xml_path + '/sched' + str(modeInd) + '.xml')
    xmlList.append(xmlObj)
    if not(reconfig):
        break #just oneschedule in all2all
#List of worst-case packet latencies (for each mode if there is NoC reconfig):
LPWC_list = []
for xmlSched in xmlList:
    root = xmlSched.getroot()
    LPWC_list.append(str(int(root.attrib['length'])+6))


#IO Latency
LAT_IO = latList['L_IO'] * 1000 / latList['Fs']

#Loop through modes
MasterLatenciesList = []
modeInd = 0


print('********************** LATENCY **********************')

for mode in latList['modes']:
    print('************** MODE ' + str(modeInd) + ' **************')
    FX_latency = mode['FX_L'] # in samples
    FX_latency_ms = FX_latency * 1000 / latList['Fs']

    #worst-case packet latency of this mode:
    if reconfig:
        LPWC = LPWC_list[modeInd]
    else:
        LPWC = LPWC_list[0]
    L_accum_ccs = 0
    for chanBuf in mode['BUF_S_LIST']:
        LC_ccs = int(chanBuf) * int(LPWC) / int(mode['BANDWIDTH'])
        L_accum_ccs += LC_ccs
    L_NoC = math.ceil(L_accum_ccs/1536) # to samples (1535 clock cycles per sample)
    L_NoC_ms = L_NoC * 1000 / latList['Fs']
    print('IO Latency: ' + str('%.2f' % LAT_IO) + ' ms (' + str(latList['L_IO']) + ' samples)' + \
          ', FX Latency: ' + str('%.2f' % FX_latency_ms) + ' ms (' + str(FX_latency) + ' samples)' + \
          ', NoC Latency: ' + str('%.2f' % L_NoC_ms) + ' ms (' + str(L_NoC) + ' samples)')
    MasterLatency = math.ceil( (FX_latency+L_NoC) / mode['LAST_FX_SIZE'])
    tot_lat = MasterLatency * mode['LAST_FX_SIZE']
    tot_lat_ms = tot_lat * 1000 / latList['Fs']
    print('Total Latency of FX and NoC:' + str('%.2f' % tot_lat_ms) + ' ms (' + str(tot_lat) + ' samples)')
    #total latency (FX, NoC, IOs)
    L_TOTAL = tot_lat + latList['L_IO']
    L_TOTAL_ms = L_TOTAL * 1000 / latList['Fs']
    print('TOTAL LATENCY: ' + \
          str('%.2f' % L_TOTAL_ms) + ' ms (' + str(L_TOTAL) + ' samples)')
    MasterLatenciesList.append(MasterLatency)
    modeInd += 1

#Header file
LAT_H = '''
#ifndef _LATENCYINIT_H_
#define _LATENCYINIT_H_

//latency from input to output, measured in iterations
const unsigned int LATENCY[MODES] = {'''
for Latency in MasterLatenciesList:
    LAT_H += str(Latency) + ', '
LAT_H += '''};

#endif /* _LATENCYINIT_H_ */'''

#write file
file = open(p.LatencyInitFile, "w")
file.write(LAT_H)
file.close()
