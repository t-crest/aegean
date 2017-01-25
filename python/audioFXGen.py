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
    #some parameters:
    OH_MULT_0 = 4
    INOUT_BUF_SIZE = 128
    MAX_NOC_BANDWIDTH = 4
    Fs = 52083
    BUF_AMOUNT = 3
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
    #   -ORF: overhead reducing factor between minimum buffer size and S
    #   -util: utilization ratio: processing time per sample relative to sampling period
    FX = []
    #loaded JSON object
    audioApp = {}
    #List describing the used effects (used to create header)
    ModesList = []
    chan_id = 0
    LatencyList = []
    latenciesDict = {}
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
    projectname = sys.argv[3]
    projectname = os.path.splitext(projectname)[0]
    print("PROJECT NAME: " + projectname)
    p = Paths(projectname)
    #NoC Reconfiguration
    NoCReconfig = False

    def __init__ (self):
        #Read Audio APP JSON
        print("READING AUDIO APP FILE: " + sys.argv[2])
        with open (sys.argv[2]) as audioApp_json:
            self.audioApp = json.load(audioApp_json)
        print('READING FX LIST FILE: ' + sys.argv[1])
        with open (sys.argv[1]) as FX_json:
            jsonFX = json.load(FX_json)
        self.FX = jsonFX['FX_LIST']
        #check if reconfiguration is enabled
        if sys.argv[4] == '1':
            print('NoC RECONFIGURATION ENABLED')
            self.NoCReconfig = True
        else:
            print('NoC RECONFIGURATION DISABLED')

    #function used by addFX to add 1 FX
    def addThisFX(self, thisFX, fx_id, core, FXList, CORE_UTIL, thisChain, prevChain):
        for fxi in range(0,len(self.FX)):
            #get fx_type and S
            if self.FX[fxi]['name'] == thisFX:
                fx_type = fxi
                S = self.FX[fxi]['S']
                ORF = self.FX[fxi]['ORF']
                #for 0: increase ORF
                if fx_id == 0:
                    ORF = ORF * self.OH_MULT_0
                util = self.FX[fxi]['util']
                break
            if fxi == (len(self.FX)-1):
                print('ERROR: EFFECT ' \
                      + thisFX + ' DOES NOT EXIST')
                return (1, fx_id, core, FXList, CORE_UTIL)
        same_core_in = False
        #if chain starts or finishes, must update core
        chainStarts = False
        chainEnds = False
        if thisChain != prevChain:
            core += 1
            if thisChain > 0:
                chainStarts = True
            if thisChain == 0:
                chainEnds = True
            #print('chain start or finish')
        else:
            #see if there is enough utilization space on this core for this FX
            if (1-CORE_UTIL[core]) < util: #if not enough space
                core += 1
            else:
                #receives from same core: only if it is not 1st and its not empty
                if (fx_id != 0) and (CORE_UTIL[core] > 0):
                    same_core_in = True
        if core >= self.CORE_AMOUNT:
            print('ERROR: TOO MANY EFFECTS, DONT FIT IN ' \
                  + str(self.CORE_AMOUNT) + ' CORES')
            return (1, fx_id, core, FXList, CORE_UTIL)
        #update utilization
        CORE_UTIL[core] += util
        bufsize = S*ORF
        #limit: 32
        if bufsize > 32:
            bufsize = 32
        #store object
        fxObj = { 'fx_id'   : fx_id,
                  'core'    : self.coreOrder[core]['id'],
                  'fx_type' : fx_type,
                  'S'       : S,
                  'xb_size' : bufsize,
                  'yb_size' : bufsize,
                  'chain_id': thisChain
        }
        #check if it is same core in
        if same_core_in:
            FXList[len(FXList)-1]['out_same'] = True
            fxObj['in_same'] = True
            #if out same, increase overhead reducer
            fxObj['xb_size'] = fxObj['xb_size']*self.OH_MULT_0
        #check if there is fork or join
        if (len(FXList) > 0): #if it is not first FX of this mode
            if (thisChain > 0) and (prevChain == 0):
                FXList[len(FXList)-1]['is_fork'] = True
            if (thisChain == 0) and (prevChain > 0):
                fxObj['is_join'] = True
        #if it is first or last of chain:
        if chainStarts:
            fxObj['chain_start'] = True
            #check if last one was not fork: if not, it was a chain end
            if 'is_fork' not in FXList[len(FXList)-1]:
                FXList[len(FXList)-1]['chain_end'] = True
        if chainEnds:
            FXList[len(FXList)-1]['chain_end'] = True
        FXList.append(fxObj)
        #print(thisFX + ', chain=' + str(thisChain) + ', core ' + str(core) + ': fx_util=' + str(util) + ', core_util='+ str(CORE_UTIL[core]))
        fx_id += 1
        return (0, fx_id, core, FXList, CORE_UTIL)

    #function to add chains form audioApp into the FX List
    def addFX(self):
        for mode in self.audioApp['modes']:
            FXList = []
            fx_id = 0
            core = 0
            #Current utilization on each core (between 0 and 1)
            CORE_UTIL = [0.5, 0, 0, 0]
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
                                 'xb_size' : self.OH_MULT_0,
                                 'yb_size' : self.OH_MULT_0,
                                 'chain_id': 0 })
                fx_id += 1
                CORE_UTIL[0] = 1
            else:
                #if util of 1st > 0.5, create dry effect as first:
                for fxi in range(0,len(self.FX)):
                    #get fx_type and S
                    if (self.FX[fxi]['name'] == mode[0]) and (self.FX[fxi]['util'] > 0.5):
                        #add initial effect: dry
                        FXList.append( { 'fx_id'   : fx_id,
                                         'core'    : 0,
                                         'fx_type' : 0,
                                         'S'       : 1,
                                         'xb_size' : self.OH_MULT_0,
                                         'yb_size' : self.OH_MULT_0,
                                         'chain_id': 0 })
                        fx_id += 1
                        CORE_UTIL[0] = 1
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
                                result, fx_id, core, FXList, CORE_UTIL = \
                                    self.addThisFX(fxname, fx_id, core, \
                                                   FXList, CORE_UTIL, thisChain, prevChain)
                                prevChain = thisChain
                                if result == 1:
                                    return 1
                else:
                    thisChain = 0
                    result, fx_id, core, FXList, CORE_UTIL = \
                        self.addThisFX(item, fx_id, core, \
                                       FXList, CORE_UTIL, thisChain, prevChain)
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
                FXList[len(FXList)-1]['chain_end'] = True
            FXList.append(fxObj)
            #add mode to modes list
            self.ModesList.append(FXList)
        return 0

    #function to check that the amount of cores in each chain is balanced
    def checkChainBalance(self):
        for mode in self.ModesList:
            chain_amount = 0
            for fx in mode:
                if fx['chain_id'] > chain_amount:
                    chain_amount = fx['chain_id']
            cores_per_chain = [0] * chain_amount
            for i in range(0, len(cores_per_chain)):
                cores_on_chain = []
                for fx in mode:
                    if (fx['chain_id']-1) == i:
                        if fx['core'] not in cores_on_chain:
                            cores_on_chain.append(fx['core'])
                cores_per_chain[i] = len(cores_on_chain)
            #check that all chains have same amount of cores
            if len(cores_per_chain) > 0:
                chain_cores_base = cores_per_chain[0]
                for c in cores_per_chain:
                    if cores_per_chain[c] != chain_cores_base:
                        print('ERROR: chains have different amount of cores, must have the same')
                        return 1
        return 0

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
                #output connections IDs
                if i < (len(FXList) - 1): #not last
                    fxAdd['to_id'] = []
                    if 'is_fork' in FXList[i]:
                        #amount of chains: as many as 'chain_start' amount
                        for fx in range(0, len(FXList)):
                            if 'chain_start' in FXList[fx]:
                                fxAdd['to_id'].append(self.chan_id)
                                self.chan_id += 1
                    else:
                        fxAdd['to_id'].append(self.chan_id)
                        self.chan_id += 1
                #add fxAdd to dict
                FXList[i].update(fxAdd)
            #loop again for input connections IDs
            for i in range(0,len(FXList)):
                if i > 0: #not first
                    fxAdd = {'from_id' : []}
                    if 'is_join' in FXList[i]:
                        #check channels of effects that are 'chain_end'
                        for fx in range(0, len(FXList)):
                            if 'chain_end' in FXList[fx]:
                                fxAdd['from_id'].append(FXList[fx]['to_id'][0])
                    else: #not a join
                        #if its a chain start:
                        if 'chain_start' in FXList[i]:
                            #check channels of effects that are fork
                            for fx in range(0, len(FXList)):
                                if 'is_fork' in FXList[fx]:
                                    #channel index is given by chain_id
                                    fxAdd['from_id'].append \
                                        (FXList[fx]['to_id'][(FXList[i]['chain_id']-1)])
                                    break #there is only one fork
                        else:
                            #receive from previous effect
                            fxAdd['from_id'].append(FXList[i-1]['to_id'][0])
                    #add fxAdd to dict
                    FXList[i].update(fxAdd)

    #function to match buffer sizes on a join effect
    def setJoinSizes(self, jind, FXList):
        #input size: max(<chain_end yb_sizes>, <input>)
        size = FXList[jind]['xb_size']
        #loop 1st time: find maximum
        for channel_in in FXList[jind]['from_id']:
            for fx in range(0, len(FXList)-1):
                if FXList[fx]['to_id'][0] == channel_in:
                    size = max(size, FXList[fx]['yb_size'])
        FXList[jind]['xb_size'] = size
        #print('join ' + str(jind) + ': max size: ' + str(size))
        #loop 2nd time: set value
        for channel_in in FXList[jind]['from_id']:
            for fx in range(0, len(FXList)-1):
                if FXList[fx]['to_id'][0] == channel_in:
                    FXList[fx]['yb_size'] = size
        return FXList

    #function to match buffer sizes on a fork effect
    def setForkSizes(self, find, FXList):
        #output size: max(<chain_start xb_sizes>, <input>)
        size = FXList[find]['yb_size']
        #loop 1st time: find maximum
        for channel_out in FXList[find]['to_id']:
            for fx in range(1, len(FXList)):
                if FXList[fx]['from_id'][0] == channel_out:
                    size = max(size, FXList[fx]['xb_size'])
        FXList[find]['yb_size'] = size
        #print('fork ' + str(find) + ': max size: ' + str(size))
        #loop 2nd time: set value
        for channel_out in FXList[find]['to_id']:
            for fx in range(1, len(FXList)):
                if FXList[fx]['from_id'][0] == channel_out:
                    FXList[fx]['xb_size'] = size
        return FXList

    #function to change buffer sizes
    def setBufSizes(self):
        for FXList in self.ModesList:
            for i in range(0,len(FXList)):
                #xb_size: only for non-first
                if i != 0:
                    if FXList[i]['in_con'] == 3: #same core in
                        #all must have same size: XeY
                        size = max(FXList[i]['xb_size'], FXList[i]['yb_size'], \
                                   FXList[i-1]['xb_size'], FXList[i-1]['yb_size'])
                        FXList[i]['xb_size'] = size
                        FXList[i]['yb_size'] = size
                        FXList[i-1]['xb_size'] = size
                        FXList[i-1]['yb_size'] = size
                    else: #NoC in
                        #is it a join?
                        if 'is_join' in FXList[i]:
                            FXList = self.setJoinSizes(i, FXList)
                        #is it a 'chain_start'?
                        elif 'chain_start' in FXList[i]:
                            chan_id = FXList[i]['from_id'][0]
                            #find the fork
                            for fx in range(0, len(FXList)):
                                if 'is_fork' in FXList[fx]:
                                    #iterate through fork channels
                                    for channel in FXList[fx]['to_id']:
                                        if channel == chan_id: #Found the right fork
                                            FXList = self.setForkSizes(fx, FXList)
                        else: #No join or chain_start
                            chan_id = FXList[i]['from_id'][0]
                            #look for source FX
                            for fx in range(0, len(FXList)-1):
                                if ('is_fork' not in FXList[fx]) and \
                                   ('chain_end' not in FXList[fx]) and \
                                   (FXList[fx]['out_con'] == 2) and \
                                   (FXList[fx]['to_id'][0] == chan_id):
                                    size = max(FXList[i]['xb_size'], FXList[fx]['yb_size'])
                                    FXList[i]['xb_size']  = size
                                    FXList[fx]['yb_size'] = size
                                    break
                #yb_size: only for non-last
                if i != (len(FXList)-1):
                    if FXList[i]['out_con'] == 3: #same core out
                        #all must have same size: XeY
                        size = max(FXList[i]['xb_size'], FXList[i]['yb_size'], \
                                   FXList[i+1]['xb_size'], FXList[i+1]['yb_size'])
                        FXList[i]['xb_size'] = size
                        FXList[i]['yb_size'] = size
                        FXList[i+1]['xb_size'] = size
                        FXList[i+1]['yb_size'] = size
                    else: #NoC out
                        #is it a fork?
                        if 'is_fork' in FXList[i]:
                            FXList = self.setForkSizes(i, FXList)
                        #is it a 'chain_end'?
                        elif 'chain_end' in FXList[i]:
                            chan_id = FXList[i]['to_id'][0]
                            #find the join
                            for fx in range(0, len(FXList)):
                                if 'is_join' in FXList[fx]:
                                    #iterate through join channels
                                    for channel in FXList[fx]['from_id']:
                                        if channel == chan_id: #Found the right join
                                            FXList = self.setJoinSizes(fx, FXList)
                        else: #No fork or chain_end
                            chan_id = FXList[i]['to_id'][0]
                            #look for destination FX
                            for fx in range(1, len(FXList)):
                                if ('is_join' not in FXList[fx]) and \
                                   ('chain_start' not in FXList[fx]) and \
                                   (FXList[fx]['in_con'] == 3) and \
                                   (FXList[fx]['from_id'][0] == chan_id):
                                    size = max(FXList[i]['yb_size'], FXList[fx]['xb_size'])
                                    FXList[i]['yb_size']  = size
                                    FXList[fx]['xb_size'] = size
                                    break

    #function to set first and last FX to XeY
    def makeEdgesXeY(self):
        for FXList in self.ModesList:
            maxBuf = 0
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

    #function to calculate the latency in RUNS OF CORE 0 (not in samples from input to output)
    def calcLatency(self):
        #JSON file containing latency values
        #self.latenciesDict = {}
        #add Fs and IO Buffer Latency
        self.latenciesDict['Fs'] = self.Fs
        self.latenciesDict['L_IO'] = self.INOUT_BUF_SIZE
        #Prepare to add FX Latency of each mode
        self.latenciesDict['modes'] = []
        for FXList in self.ModesList:
            coresDone = []
            Latency = 0
            #List to store channel buffer sizes
            buf_sizes_list = []
            #first, latency for the 1st sample to arrive
            for fx in FXList:
                #check that latency of this core has not jet been considered
                #(because just one FX needs to be considered per core)
                #Also, consider just one chain: only chains 0 and 1 (if it exists)
                if (fx['core'] not in coresDone) and ( (fx['chain_id'] == 0) or (fx['chain_id'] == 1) ):
                    coresDone.append(fx['core'])
                    Latency += fx['yb_size']
                    buf_sizes_list.append(fx['yb_size'])
            #then, add xb_size of LAST
            last_xb_size = FXList[len(FXList)-1]['xb_size'] #YES
            #Latency += last_xb_size #really?
            #object to add to latencies JSON
            latObj = {
                'FX_L' : Latency,
                'LAST_FX_SIZE' : last_xb_size,
                'BUF_S_LIST' : buf_sizes_list
            }
            self.latenciesDict['modes'].append(latObj)
            #finally, divide by xb_size of LAST and ceil
            MasterLatency = math.ceil(Latency / last_xb_size)
            #add to latencies list
            self.LatencyList.append(MasterLatency)

    #function to extract NoC channels info
    def extNoCChannels(self):
        #first, create list with channel IDs
        chanIDs = []
        for FXList in self.ModesList:
            for fx in FXList:
                if ('from_id' in fx) and (fx['in_con'] == 2): #not first and NoC in
                    for chan in fx['from_id']:
                        if chan not in chanIDs:
                            chanIDs.append(chan)
                if ('to_id' in fx) and (fx['out_con'] == 2): #not last and NoC out
                    for chan in fx['to_id']:
                        if chan not in chanIDs:
                            chanIDs.append(chan)
        #then, extract info
        for ci in chanIDs:
            chanObj = { 'chan_id'    : ci,
                        'buf_amount' : self.BUF_AMOUNT
            }
            for mode_i in range(0, len(self.ModesList)):
                for fx in self.ModesList[mode_i]:
                    if 'from_id' in fx: #not first
                        for chan in fx['from_id']:
                            if chan == ci:
                                chanObj['to_core'] = fx['core']
                                chanObj['mode'] = mode_i
                    if 'to_id' in fx: #not last
                        for chan in fx['to_id']:
                            if chan == ci:
                                chanObj['from_core'] = fx['core']
                                chanObj['mode'] = mode_i
            self.NoCChannels.append(chanObj)

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

        maxFXPerCore = [0] * allCores
        for FXList in self.ModesList:
            FXPerCore = [0] * allCores
            for fx in FXList:
                FXPerCore[fx['core']] += 1
            for i in range(0, len(FXPerCore)):
                maxFXPerCore[i] = max(maxFXPerCore[i], FXPerCore[i])


        #Header file
        FX_H = '''
        #ifndef _AUDIOINIT_H_
        #define _AUDIOINIT_H_

        '''
        #if NoC reconfiguration is enabled:
        if self.NoCReconfig:
            FX_H += '''
        //NoC Reconfiguration enabled
        #define NOC_RECONFIG'''
        FX_H += '''
        //input/output buffer sizes
        const unsigned int BUFFER_SIZE = ''' + str(self.INOUT_BUF_SIZE) + ''';
        //amount of configuration modes
        const int MODES = ''' + str(modes) + ''';
        //how many cores take part in the audio system (from all modes)
        const int AUDIO_CORES = ''' + str(allCores) + ''';
        //how many effects are on each mode in total
        const int FX_AMOUNT[MODES] = {'''
        for FXAmount in FXAmountList:
            FX_H += str(FXAmount) + ', '
        FX_H += '''};
        //maximum amount of effects per core
        const int MAX_FX_PER_CORE[AUDIO_CORES] = {'''
        for fxPC in maxFXPerCore:
            FX_H += str(fxPC) + ', '
        FX_H += '''};
        //maximum FX_AMOUNT
        const int MAX_FX = ''' + str(maxFX) + ''';
        // FX_ID | CORE | FX_TYPE | XB_SIZE | YB_SIZE | S | IN_TYPE | OUT_TYPE //'''
        for mode in range(0,modes):
            FX_H += '''
        const int FX_SCHED_''' + str(mode) + '''[''' \
            + str(FXAmountList[mode]) + '''][8] = {'''
            #fill in matrix
            for fx in self.ModesList[mode]:
                FX_H += '''
            { ''' + str(fx['fx_id']) + ', ' + str(fx['core']) + ', ' \
                + str(fx['fx_type']) + ', ' + str(fx['xb_size']) + ', ' \
                + str(fx['yb_size']) + ', ' + str(fx['S']) + ', ' \
                + str(fx['in_con']) + ', ' + str(fx['out_con']) + ' },'
            FX_H += '''
        };'''
        FX_H += '''
        //pointer to schedules
        const int *FX_SCHED_P[MODES] = {'''
        for mode in range(0,modes):
            FX_H += '''
            (const int *)FX_SCHED_''' + str(mode) + ','
        FX_H += '''
        };
        //amount of NoC channels (NoC or same core) on all modes
        const int CHAN_AMOUNT = ''' + str(self.chan_id) + ''';
        //amount of buffers on each NoC channel ID
        const int CHAN_BUF_AMOUNT[CHAN_AMOUNT] = { '''
        for chan in range(0, self.chan_id):
            chanPrinted = False
            for c in self.NoCChannels:
                if chan == c['chan_id']:
                    FX_H += str(c['buf_amount']) + ', '
                    chanPrinted = True
                    break
            if not(chanPrinted):
                FX_H += '1, '
        FX_H += '''};
        // column: FX_ID source   ,   row: CHAN_ID dest'''
        for mode in range(0,modes):
            FX_H += '''
        const int SEND_ARRAY_''' + str(mode) + '''[''' \
            + str(FXAmountList[mode]) + '''][CHAN_AMOUNT] = {'''
            #fill in matrix
            for fx in self.ModesList[mode]:
                FX_H += '''
            {'''
                for chan in range(0, self.chan_id):
                    thisOutCon = False
                    if 'to_id' in fx:
                        for chanTo in fx['to_id']:
                            if chanTo == chan:
                                FX_H += '1, '
                                thisOutCon = True
                    if not(thisOutCon):
                        FX_H += '0, '
                FX_H += '''},'''
            FX_H += '''
        };'''
        FX_H += '''
        //pointer to send arrays
        const int *SEND_ARRAY_P[MODES] = {'''
        for mode in range(0,modes):
            FX_H += '''
            (const int *)SEND_ARRAY_''' + str(mode) + ','
        FX_H += '''
        };
        // column: FX_ID dest   ,   row: CHAN_ID source'''
        for mode in range(0,modes):
            FX_H += '''
        const int RECV_ARRAY_''' + str(mode) + '''[''' \
            + str(FXAmountList[mode]) + '''][CHAN_AMOUNT] = {'''
            #fill in matrix
            for fx in self.ModesList[mode]:
                FX_H += '''
            {'''
                for chan in range(0, self.chan_id):
                    thisInCon = False
                    if 'from_id' in fx:
                        for chanFrom in fx['from_id']:
                            if chanFrom == chan:
                                FX_H += '1, '
                                thisInCon = True
                    if not(thisInCon):
                        FX_H += '0, '
                FX_H += '''},'''
            FX_H += '''
        };'''
        FX_H += '''
        //pointer to receive arrays
        const int *RECV_ARRAY_P[MODES] = {'''
        for mode in range(0,modes):
            FX_H += '''
            (const int *)RECV_ARRAY_''' + str(mode) + ','
        FX_H += '''
        };

        #endif /* _AUDIOINIT_H_ */'''
        #write file
        file = open(self.p.AudioInitFile, "w")
        file.write(FX_H)
        file.close()

    #function to fill in the NoCConfs array
    def confNoC(self):
        minBufSizes = [] # min buffer size for each mode
        for FXList in self.ModesList:
            #first, find out minimum buffer size:
            minBufSize = self.MAX_NOC_BANDWIDTH #(start from maximum)
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
        #add bandwidth values to latencies dict
        modeInd = 0
        for mode in self.latenciesDict['modes']:
            mode['BANDWIDTH'] = minBufSizes[modeInd]
            modeInd += 1
        #Write latencies object
        with open(sys.argv[5], 'w') as latJSON:
            json.dump(self.latenciesDict, latJSON)
        '''
        for NoCConf in self.NoCConfs:
            print('THIS MODE')
            for chan in NoCConf['channels']:
                print(chan)
        '''

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
        print("GENERATING NoC TDM SCHEDULING XML FILE: " + sys.argv[3])
        doc.write(sys.argv[3], xml_declaration=True, encoding='utf-8')


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
#iterative process:
for i in range(0, 10):
    myAudio.setBufSizes()
    myAudio.makeEdgesXeY()
    myAudio.setBufSizes()

'''
#print all
for mode in myAudio.ModesList:
    print(' ''
    *******NEW MODE********' '')
    for fx in mode:
        print(fx)
'''

#latency from input to output in samples
myAudio.calcLatency()
myAudio.extNoCChannels()
myAudio.createHeader()

#NoC stuff
myAudio.confNoC()
myAudio.genNoCSchedule()

print('EXIT SUCCESSFULLY')
