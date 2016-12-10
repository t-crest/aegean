import sys
import paths
import os, errno
import ntpath
from paths import Paths
from lxml import etree
from io import StringIO

import json


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
    FXList = []
    fx_id = 0
    core = 0
    chan_id = 0
    Latency = 0
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
    NoCConfs = [
        {'comType' : 'custom',
         'phits'   : '3',
         'channels' : [] }
    ]
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
        for chain in self.audioApp['chains']:
            #iterate FX
            for fxname in chain['FX']:
                if self.core == self.CORE_AMOUNT:
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
                        print('ERROR: EFFECT ' + fxname + ' DOES NOT EXIST')
                        return 1
                #store object
                fxObj = { 'fx_id'   : self.fx_id,
                          'core'    : self.coreOrder[self.core]['id'],
                          'fx_type' : fx_type,
                          'xb_size' : S,
                          'yb_size' : S,
                          'S'       : S
                }
                self.FXList.append(fxObj)
                self.fx_id += 1
                self.core += 1
        #add final effect: dry
        self.FXList.append( { 'fx_id'   : len(self.FXList),
                              'core'    : 0,
                              'fx_type' : 0,
                              'xb_size' : 1,
                              'yb_size' : 1,
                              'S'       : 1 })
        return 0

    #function to create connections
    def connectFX(self):
        for i in range(0,len(self.FXList)):
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
            if i == (len(self.FXList)-1):
                out_type = 0
                to_id = -1

            fxAdd = { 'in_type'  : in_type,
                      'out_type' : out_type,
                      'from_id'  : from_id,
                      'to_id'    : to_id
            }
            #add fxAdd to dict
            self.FXList[i].update(fxAdd)
            #increment chan_id
            self.chan_id += 1

    #function to change buffer sizes
    def setBufSizes(self):
        for i in range(0,len(self.FXList)):
            #xb_size: only for non-first
            if i != 0:
                prev_yb_size = self.FXList[i-1]['yb_size']
                if prev_yb_size > self.FXList[i]['xb_size']:
                    self.FXList[i]['xb_size'] = prev_yb_size
            #yb_size: only for non-last
            if i != (len(self.FXList)-1):
                next_xb_size = self.FXList[i+1]['xb_size']
                if next_xb_size > self.FXList[i]['yb_size']:
                    self.FXList[i]['yb_size'] = next_xb_size

    #function to set first and last FX to XeY
    def makeEdgesXeY(self):
        maxBuf = 0
        #first find max from x/y in/out
        for i in range(0,len(self.FXList)):
            if (i==0) or (i==(len(self.FXList)-1)):
                maxTemp = max(self.FXList[i]['xb_size'], self.FXList[i]['yb_size'])
                maxBuf = max(maxBuf, maxTemp)
        #then set values
        for i in range(0,len(self.FXList)):
            if (i==0) or (i==(len(self.FXList)-1)):
                self.FXList[i]['xb_size'] = maxBuf
                self.FXList[i]['yb_size'] = maxBuf

    #function to calculate the latency in samples from input to output
    def calcLatency(self):
        coresDone = []
        for fx in self.FXList:
            #check that latency of this core has not jet been considered
            if fx['core'] not in coresDone:
                coresDone.append(fx['core'])
                self.Latency += fx['yb_size']

    #function to extract NoC channels info
    def extNoCChannels(self):
        #first, create list with channel IDs
        chanIDs = []
        for fx in self.FXList:
            if (fx['in_type'] == 1) and (fx['from_id'] not in chanIDs):
                chanIDs.append(fx['from_id'])
            if (fx['out_type'] == 1) and (fx['to_id'] not in chanIDs):
                chanIDs.append(fx['to_id'])
        #then, extract info
        for ci in chanIDs:
            chanObj = { 'chan_id'    : ci,
                        'buf_amount' : 8 #fixed for now
            }
            for fx in self.FXList:
                if (fx['from_id'] == ci) and (fx['in_type'] == 1):
                    chanObj['to_core'] = fx['core']
                if (fx['to_id'] == ci) and (fx['out_type'] == 1):
                    chanObj['from_core'] = fx['core']
            self.NoCChannels.append(chanObj)

    #function to fill in the NoCConfs array
    def confNoC(self):
        for chan in self.NoCChannels:
            for core in self.coreOrder:
                if chan['from_core'] == core['id']:
                    from_p = core['pos']
                if chan['to_core'] == core['id']:
                    to_p = core['pos']
            chanObj = { 'from' : from_p,
                        'to'   : to_p,
                        'bandwidth' : '10' #fixed for now
            }
            #create reverted channel (for ACK)
            chanObjRev = { 'from' : to_p,
                           'to'   : from_p,
                           'bandwidth' : '10' #fixed for now
            }
            self.NoCConfs[0]['channels'].append(chanObj)
            self.NoCConfs[0]['channels'].append(chanObjRev)

    #function to create header file
    def createHeader(self):
        FX_H = '''
        //how many cores take part in the audio system
        const int AUDIO_CORES = ''' + str(self.core)
        FX_H += ''';
        //how many effects are on the system in total
        const int FX_AMOUNT = ''' + str(len(self.FXList))
        FX_H += ''';
        // FX_ID | CORE | FX_TYPE | XB_SIZE | YB_SIZE | P (S) | IN_TYPE | OUT_TYPE | FROM_ID | TO_ID //
        const int FX_SCHED[FX_AMOUNT][10] = {'''
        #add files
        for fx in self.FXList:
            FX_H += '''
            { ''' + str(fx['fx_id']) + ', ' + str(fx['core']) + ', ' + str(fx['fx_type']) + ', ' + \
                str(fx['xb_size']) + ', ' + str(fx['yb_size']) + ', ' + str(fx['S']) + ', ' + \
                str(fx['in_type']) + ', ' + str(fx['out_type']) + ', ' + str(fx['from_id']) + ', ' + \
                str(fx['to_id']) + ' },'
        FX_H += '''
        };'''
        FX_H += '''
        //amount of NoC channels
        const int CHAN_AMOUNT = ''' + str(self.chan_id-1)
        FX_H += ''';
        //amount of buffers on each NoC channel ID
        const int CHAN_BUF_AMOUNT[CHAN_AMOUNT] = [ '''
        for chan in self.NoCChannels:
            FX_H += str(chan['buf_amount']) + ', '
        FX_H += '''];
        //latency from input to output in samples (without considering NoC)
        const int LATENCY = ''' + str(self.Latency) + ';'
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
