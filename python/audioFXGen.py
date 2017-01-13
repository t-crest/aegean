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
        { 'id'  : 2,
          'pos' : '(0,1)' },
        { 'id'  : 3,
          'pos' : '(1,1)' }
    ]
    #List of available effects:
    #   -S: samples processed per execution
    #   -OH_req: overhead required ratio between minimum buffer size and S
    #   -occup: occupation ratio: processing time per sample relative to sampling period
    FX = [
        { 'name' : 'DRY',          'S' : 1 ,  'OH_req' : 1 , 'occup' : 0.5 },
        { 'name' : 'DRY_8SAMPLES', 'S' : 8 ,  'OH_req' : 2 , 'occup' : 0.5 },
        { 'name' : 'DELAY',        'S' : 1 ,  'OH_req' : 2 , 'occup' : 0.5 },
        { 'name' : 'OVERDRIVE',    'S' : 1 ,  'OH_req' : 4 , 'occup' :   1 },
        { 'name' : 'WAHWAH',       'S' : 1 ,  'OH_req' : 4 , 'occup' :   1 },
        { 'name' : 'CHORUS',       'S' : 1 ,  'OH_req' : 4 , 'occup' :   1 },
        { 'name' : 'DISTORTION',   'S' : 1 ,  'OH_req' : 4 , 'occup' :   1 },
        { 'name' : 'HP',           'S' : 1 ,  'OH_req' : 2 , 'occup' :   1 },
        { 'name' : 'LP',           'S' : 1 ,  'OH_req' : 2 , 'occup' :   1 },
        { 'name' : 'BP',           'S' : 1 ,  'OH_req' : 2 , 'occup' :   1 },
        { 'name' : 'BR',           'S' : 1 ,  'OH_req' : 2 , 'occup' :   1 },
        { 'name' : 'VIBRATO',      'S' : 1 ,  'OH_req' : 2 , 'occup' : 0.5 },
        { 'name' : 'TREMOLO',      'S' : 1 ,  'OH_req' : 2 , 'occup' : 0.5 },
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

    #function used by addFX to add 1 FX
    def addThisFX(self, thisFX, fx_id, core, FXList, CORE_OCCUP, thisChain, prevChain):
        for fxi in range(0,len(self.FX)):
            #get fx_type and S
            if self.FX[fxi]['name'] == thisFX:
                fx_type = fxi
                S = self.FX[fxi]['S']
                OH_req = self.FX[fxi]['OH_req']
                occup = self.FX[fxi]['occup']
                break
            if fxi == (len(self.FX)-1):
                print('ERROR: EFFECT ' \
                      + thisFX + ' DOES NOT EXIST')
                return (1, fx_id, core, FXList, CORE_OCCUP)
        same_core_in = False
        #if chain starts or finishes, must update core
        if thisChain != prevChain:
            core += 1
            #print('chain start or finish')
        else:
            #see if there is enough occupation space on this core for this FX
            if (1-CORE_OCCUP[core]) < occup: #if not enough space
                core += 1
            else:
                #receives from same core: only if it is not 0 and its not empty
                if (core != 0) and (CORE_OCCUP[core] > 0):
                    same_core_in = True
        if core >= self.CORE_AMOUNT:
            print('ERROR: TOO MANY EFFECTS, DONT FIT IN ' \
                  + str(self.CORE_AMOUNT) + ' CORES')
            return (1, fx_id, core, FXList, CORE_OCCUP)
        #update occupation
        CORE_OCCUP[core] += occup
        #store object
        fxObj = { 'fx_id'   : fx_id,
                  'core'    : self.coreOrder[core]['id'],
                  'fx_type' : fx_type,
                  'S'       : S,
                  'xb_size' : (S*OH_req),
                  'yb_size' : (S*OH_req),
                  'chain_id': thisChain
        }
        #check if it is same core in
        if same_core_in:
            FXList[len(FXList)-1]['out_same'] = True
            fxObj['in_same'] = True
        #check if there is fork or join
        if (len(FXList) > 0): #if it is not first FX of this mode
            if (thisChain > 0) and (prevChain == 0):
                FXList[len(FXList)-1]['is_fork'] = True
            if (thisChain == 0) and (prevChain > 0):
                fxObj['is_join'] = True
        FXList.append(fxObj)
        #print(thisFX + ', chain=' + str(thisChain) + ', core ' + str(core) + ': fx_occup=' + str(occup) + ', core_occup='+ str(CORE_OCCUP[core]))
        fx_id += 1
        return (0, fx_id, core, FXList, CORE_OCCUP)

    #function to add chains form audioApp into the FX List
    def addFX(self):
        for mode in self.audioApp['modes']:
            FXList = []
            fx_id = 0
            core = 0
            #Current occupation on each core (between 0 and 1)
            CORE_OCCUP = [0, 0, 0, 0]
            #to check which chain (0 = no chain, 1+ = chain number)
            thisChain = 0
            prevChain = 0
            #if mode starts with chain, create 1st FX with id 0
            if (type(mode[0]) == dict) and ('chains' in mode[0]):
                #add initial effect: dry
                FXList.append( { 'fx_id'   : fx_id,
                                 'core'    : 0,
                                 'fx_type' : 0,
                                 'S'       : 1,
                                 'xb_size' : 1,
                                 'yb_size' : 1,
                                 'chain_id': 0 })
                fx_id += 1
                CORE_OCCUP[0] = 1
            #loop through items in mode
            for item in mode:
                if type(item)  == dict:
                    if 'chains' not in item:
                        print('ERROR: wrong name, ' \
                              + 'only effect names or the "chains" keyword are accepted')
                        return 1
                    else:
                        #iterate chains
                        for chain in item['chains']:
                            thisChain += 1
                            #iterate FX
                            for fxname in chain:
                                result, fx_id, core, FXList, CORE_OCCUP = \
                                    self.addThisFX(fxname, fx_id, core, \
                                                   FXList, CORE_OCCUP, thisChain, prevChain)
                                prevChain = thisChain
                                if result == 1:
                                    return 1
                else:
                    thisChain = 0
                    result, fx_id, core, FXList, CORE_OCCUP = \
                        self.addThisFX(item, fx_id, core, \
                                       FXList, CORE_OCCUP, thisChain, prevChain)
                    prevChain = thisChain
                    if result == 1:
                        return 1

            #add final effect: dry
            fxObj = { 'fx_id'   : len(FXList),
                      'core'    : 0,
                      'fx_type' : 0,
                      'S'       : 1,
                      'xb_size' : 1,
                      'yb_size' : 1,
                      'chain_id': 0 }
            #check if last one is a join
            if prevChain > 0:
                fxObj['is_join'] = True
            FXList.append(fxObj)
            #add mode to modes list
            self.ModesList.append(FXList)
        return 0

    #function to check that the amount of cores in each chain is balanced
    def checkChainBalance(self):
        for mode in self.ModesList:
            chain_amount = 0
            for fx in mode:
                if fx['chain'] > chain_amount:
                    chain_amount = fx['chain']
            print('chain amount is ' + str(chain_amount))

    #function to create connections
    def connectFX(self):
        for FXList in self.ModesList:
            for i in range(0,len(FXList)):
                if i == 0: #first
                    in_con = 0
                else:
                    if 'in_same' in FXList[i]:
                        in_con = 3 #same core
                        FXList[i].pop('in_same')
                    else:
                        in_con = 2 #NoC
                if i == (len(FXList)-1): #last
                    out_con = 1
                else:
                    if 'out_same' in FXList[i]:
                        out_con = 3 #same core
                        FXList[i].pop('out_same')
                    else:
                        out_con = 2 #NoC

                fxAdd = { 'in_con'  : in_con,
                          'out_con' : out_con
                }
                if i > 0: #not first
                    fxAdd['from_id'] = self.chan_id - 1
                if i < (len(FXList) - 1): #not last
                    fxAdd['to_id'] = self.chan_id
                #add fxAdd to dict
                FXList[i].update(fxAdd)
                #increment chan_id
                self.chan_id += 1

        #print all
        for mode in self.ModesList:
            print('''
*******NEW MODE********''')
            for fx in mode:
                print(fx)

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
if myAudio.checkChainBalance():
    print('EXITING...')
    exit(1)
myAudio.connectFX()
#myAudio.setBufSizes()
#myAudio.makeEdgesXeY()
#need to run again to connections on edges
#myAudio.setBufSizes()
#latency from input to output in samples
#myAudio.calcLatency()
#myAudio.extNoCChannels()
#myAudio.createHeader()

#NoC stuff
#myAudio.confNoC()
#myAudio.genNoCSchedule()

print('EXIT SUCCESSFULLY')
