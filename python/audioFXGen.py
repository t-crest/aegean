import sys
import paths
import os, errno
import ntpath
from paths import Paths
from lxml import etree
from io import StringIO

import json
import math

#Possible channel configuration example
'''
NoCConfs = [
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
'''

class AudioMain:
    #################### FX ######################
    #Amount of available cores in the platform
    CORE_AMOUNT = 4
    #Core order for minimal NoC channel usage
    coreOrder = [
        { 'id'  : 0,
          'pos' : '(0,0)' },
        { 'id'  : 1,
          'pos' : '(1,0)' },
        { 'id'  : 3,
          'pos' : '(1,1)' },
        { 'id'  : 2,
          'pos' : '(0,1)' }
    ]
    #List of available effects: S: samples processed per execution
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
    #loaded JSON object
    audioApp = {}
    #List describing the used effects (used to create header)
    ModesList = []
    chan_id = 0
    LatencyList = []
    #################### NoC ######################
    #Platform NoC description
    NoC = {'width'       : '2',
           'height'      : '2',
           'topoType'    : 'bitorus',
           'routerDepth' : '3',
           'linkDepth'   : '0',
           'routerType'  : 'sync',
           'configurations' : []
    }
    #List of NoC channels needed
    NoCChannels = []
    #Describer of the scheduler XML
    NoCConfs = []
    #setup project name and paths
    projectname = sys.argv[2]
    projectname = os.path.splitext(projectname)[0]
    print("PROJECT NAME: " + projectname)
    p = Paths(projectname)

    def __init__ (self):
        #Read Audio APP JSON
        print("READING AUDIO APP FILE: " + sys.argv[1])
        with open (sys.argv[1]) as audioApp_json:
            self.audioApp = json.load(audioApp_json)

    #function to add chains form audioApp into the FX List
    def addFX(self):
        for mode in self.audioApp['modes']:
            FXList = []
            fx_id = 0
            core = 0
            for chain in mode['chains']:
                #iterate FX
                for fxname in chain:
                    if core >= self.CORE_AMOUNT:
                        print('ERROR: TOO MANY EFFECTS, DONT FIT IN ' \
                              + str(CORE_AMOUNT) + ' CORES')
                        return 1
                    for fxi in range(0,len(self.FX)):
                        #get fx_type and S
                        if self.FX[fxi]['name'] == fxname:
                            fx_type = fxi
                            S = self.FX[fxi]['S']
                            break
                            if fxi == (len(self.FX)-1):
                                print('ERROR: EFFECT ' \
                                      + fxname + ' DOES NOT EXIST')
                                return 1
                    #store object
                    fxObj = { 'fx_id'   : fx_id,
                              'core'    : self.coreOrder[core]['id'],
                              'fx_type' : fx_type,
                              'xb_size' : S,
                              'yb_size' : S,
                              'S'       : S
                    }
                    FXList.append(fxObj)
                    fx_id += 1
                    core += 1
            #add final effect: dry
            FXList.append( { 'fx_id'   : len(FXList),
                                  'core'    : 0,
                                  'fx_type' : 0,
                                  'xb_size' : 1,
                                  'yb_size' : 1,
                                  'S'       : 1 })
            #add mode to modes list
            self.ModesList.append(FXList)
        return 0

    #function to create connections
    def connectFX(self):
        for FXList in self.ModesList:
            for i in range(0,len(FXList)):
                #in_type: 0 only for 1st
                #out_type: 0 only for last
                #from_id, to_id: -1 for 1st and last, chan_id for others
                in_type  = 1
                out_type = 1
                from_id  = self.chan_id - 1
                to_id    = self.chan_id
                if i == 0:
                    in_type = 0
                    from_id = -1
                if i == (len(FXList)-1):
                    out_type = 0
                    to_id = -1

                fxAdd = { 'in_type'  : in_type,
                          'out_type' : out_type,
                          'from_id'  : from_id,
                          'to_id'    : to_id
                      }
                #add fxAdd to dict
                FXList[i].update(fxAdd)
                #increment chan_id
                if out_type == 1:
                    self.chan_id += 1

    #function to change buffer sizes
    def setBufSizes(self):
        for FXList in self.ModesList:
            for i in range(0,len(FXList)):
                #xb_size: only for non-first
                if i != 0:
                    prev_yb_size = FXList[i-1]['yb_size']
                    if prev_yb_size > FXList[i]['xb_size']:
                        FXList[i]['xb_size'] = prev_yb_size
                #yb_size: only for non-last
                if i != (len(FXList)-1):
                    next_xb_size = FXList[i+1]['xb_size']
                    if next_xb_size > FXList[i]['yb_size']:
                        FXList[i]['yb_size'] = next_xb_size

    #function to set first and last FX to XeY
    def makeEdgesXeY(self):
        maxBuf = 0
        for FXList in self.ModesList:
            #first find max from x/y in/out
            for i in range(0,len(FXList)):
                if (i==0) or (i==(len(FXList)-1)):
                    maxTemp = max(FXList[i]['xb_size'], FXList[i]['yb_size'])
                    maxBuf = max(maxBuf, maxTemp)
            #then set values
            for i in range(0,len(FXList)):
                if (i==0) or (i==(len(FXList)-1)):
                    FXList[i]['xb_size'] = maxBuf
                    FXList[i]['yb_size'] = maxBuf

    #function to calculate the latency in RUNS (not in samples from input to output
    def calcLatency(self):
        for FXList in self.ModesList:
            coresDone = []
            Latency = 0
            #first, latency for the 1st sample to arrive
            for fx in FXList:
                #check that latency of this core has not jet been considered
                if fx['core'] not in coresDone:
                    coresDone.append(fx['core'])
                    Latency += fx['yb_size']
            #then, add xb_size of LAST
            last_xb_size = FXList[len(FXList)-1]['xb_size']
            Latency += last_xb_size
            #finally, divide by xb_size of LAST and ceil
            Latency = math.ceil(Latency / last_xb_size)
            #add to latencies list
            self.LatencyList.append(Latency)

    #function to extract NoC channels info
    def extNoCChannels(self):
        #first, create list with channel IDs
        chanIDs = []
        for FXList in self.ModesList:
            for fx in FXList:
                if (fx['in_type'] == 1) and (fx['from_id'] not in chanIDs):
                    chanIDs.append(fx['from_id'])
                if (fx['out_type'] == 1) and (fx['to_id'] not in chanIDs):
                    chanIDs.append(fx['to_id'])
        #then, extract info
        for ci in chanIDs:
            chanObj = { 'chan_id'    : ci,
                        'buf_amount' : 8 #fixed for now
            }
            for mode_i in range(0, len(self.ModesList)):
                for fx in self.ModesList[mode_i]:
                    if (fx['from_id'] == ci) and (fx['in_type'] == 1):
                        chanObj['to_core'] = fx['core']
                        chanObj['mode'] = mode_i
                    if (fx['to_id'] == ci) and (fx['out_type'] == 1):
                        chanObj['from_core'] = fx['core']
                        chanObj['mode'] = mode_i
            self.NoCChannels.append(chanObj)

    #function to fill in the NoCConfs array
    def confNoC(self):
        minBufSizes = [] # min buffer size for each mode
        for FXList in self.ModesList:
            #first, find out minimum buffer size:
            minBufSize = 16 #(start from a maximum of 16)
            for fx in FXList:
                if fx['xb_size'] < minBufSize:
                    minBufSize = fx['xb_size']
            minBufSizes.append(minBufSize)
        #no need to check for repeated channels (between same cores):
        #they have different IDs on the object
        #(i.e. are different channels)
        for mode in range(0,len(minBufSizes)):
            NoCConf = {'comType' : 'custom',
                       #phits: words per packet.
                       #Stereo audio: 2 shorts = 1 word
                       #including header and flag: phits=3
                       #(minimum data is 1 word for ack channels)
                       'phits'   : '3',
                       'channels' : [] }
            for chan in self.NoCChannels:
                if chan['mode'] == mode:
                    for core in self.coreOrder:
                        if chan['from_core'] == core['id']:
                            from_p = core['pos']
                        if chan['to_core'] == core['id']:
                            to_p = core['pos']
                    chanObj = { 'from' : from_p,
                                'to'   : to_p,
                                'bandwidth' : str(minBufSizes[mode])
                                #packets per TDM period:
                                #each packet is a sample in this case.
                            }
                    #create reverted channel (for ACK)
                    chanObjRev = { 'from' : to_p,
                                   'to'   : from_p,
                                   'bandwidth' : '1' #only 1 needed for ack
                               }
                    NoCConf['channels'].append(chanObj)
                    NoCConf['channels'].append(chanObjRev)
            self.NoCConfs.append(NoCConf)

    #function to create header file
    def createHeader(self):
        #find info needed for audioinit.h
        audioCoresList = []
        FXAmountList = []
        allCores = 0
        maxFX = 0
        modes = 0
        for FXList in self.ModesList:
            coresUsed = []
            FXidsUsed = []
            modes += 1
            for fx in FXList:
                if fx['core'] not in coresUsed:
                    coresUsed.append(fx['core'])
                if fx['fx_id'] not in FXidsUsed:
                    FXidsUsed.append(fx['fx_id'])
            audioCoresList.append(len(coresUsed))
            FXAmountList.append(len(FXidsUsed))
            if len(coresUsed) > allCores:
                allCores = len(coresUsed)
            if len(FXidsUsed) > maxFX:
                maxFX = len(FXidsUsed)
        FX_H = '''
        #ifndef _AUDIOINIT_H_
        #define _AUDIOINIT_H_


        //max amount of cores (from all modes)
        const int ALL_CORES = ''' + str(allCores) + ''';
        //configuration modes
        const int MODES = ''' + str(modes) + ''';
        //how many cores take part in each mode
        const int AUDIO_CORES[MODES] = {'''
        for audioCores in audioCoresList:
            FX_H += str(audioCores) + ', '
        FX_H += '''};
        //how many effects are on each mode in total
        const int FX_AMOUNT[MODES] = {'''
        for FXAmount in FXAmountList:
            FX_H += str(FXAmount) + ', '
        FX_H += '''};
        //maximum FX_AMOUNT
        const int MAX_FX = ''' + str(maxFX) + ''';
        // FX_ID | CORE | FX_TYPE | XB_SIZE | YB_SIZE | P (S) | IN_TYPE | OUT_TYPE | FROM_ID | TO_ID //'''
        for mode in range(0,modes):
            FX_H += '''
        const int FX_SCHED_''' + str(mode) + '''[''' \
            + str(FXAmountList[mode]) + '''][10] = {'''
            #add files
            for fx in self.ModesList[mode]:
                FX_H += '''
            { ''' + str(fx['fx_id']) + ', ' + str(fx['core']) + ', ' \
                + str(fx['fx_type']) + ', ' + str(fx['xb_size']) + ', ' \
                + str(fx['yb_size']) + ', ' + str(fx['S']) + ', ' \
                + str(fx['in_type']) + ', ' + str(fx['out_type']) \
                + ', ' + str(fx['from_id']) + ', ' + str(fx['to_id']) \
                + ' },'
            FX_H += '''
        };'''
        FX_H += '''
        const int *FX_SCHED_PNT[MODES] = {'''
        for mode in range(0,modes):
            FX_H += '''
            (const int *)FX_SCHED_''' + str(mode) + ','
        FX_H += '''
        };
        //amount of NoC channels
        const int CHAN_AMOUNT = ''' + str(self.chan_id) + ''';
        //amount of buffers on each NoC channel ID
        const int CHAN_BUF_AMOUNT[CHAN_AMOUNT] = { '''
        for chan in self.NoCChannels:
            FX_H += str(chan['buf_amount']) + ', '
        FX_H += '''};
        //latency from input to output in samples (without considering NoC)
        //for each mode:
        const int LATENCY[MODES] = {'''
        for Latency in self.LatencyList:
            FX_H += str(Latency) + ', '
        FX_H += '''};

        #endif /* _AUDIOINIT_H_ */'''
        #write file
        file = open(self.p.AudioInitFile, "w")
        file.write(FX_H)
        file.close()

    # Create the root element and new document tree
    def genNoCSchedule(self):
        nocsched = etree.Element('nocsched', version='0.1',
                                 nsmap={'xi': 'http://www.w3.org/2001/XInclude'})
        doc = etree.ElementTree(nocsched)
        # Description
        desc = etree.SubElement(nocsched, 'description')
        desc.text = 'NoC TDM scheduling'
        #platform & topology
        platform = etree.SubElement(nocsched, 'platform',
                                    width=self.NoC['width'],
                                    height=self.NoC['height'])
        topology = etree.SubElement(platform, 'topology',
                                    topoType=self.NoC['topoType'],
                                    routerDepth=self.NoC['routerDepth'],
                                    linkDepth=self.NoC['linkDepth'],
                                    routerType=self.NoC['routerType'])
        #application & configurations
        configurations = etree.SubElement(etree.SubElement(nocsched, 'application'), 'configurations')
        for commun in self.NoCConfs:
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
        print("GENERATING NoC TDM SCHEDULING XML FILE: " + sys.argv[2])
        doc.write(sys.argv[2], xml_declaration=True, encoding='utf-8')


#create class
myAudio=AudioMain()

#FX stuff
if myAudio.addFX():
    print('EXITING...')
    exit(1)
myAudio.connectFX()
myAudio.setBufSizes()
myAudio.makeEdgesXeY()
#need to run again to connections on edges
myAudio.setBufSizes()
#latency from input to output in samples
myAudio.calcLatency()
myAudio.extNoCChannels()
myAudio.createHeader()

#NoC stuff
myAudio.confNoC()
myAudio.genNoCSchedule()

print('EXIT SUCCESSFULLY')
