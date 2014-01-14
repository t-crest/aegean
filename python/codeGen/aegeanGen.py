#
# Copyright Technical University of Denmark. All rights reserved.
# This file is part of the T-CREST project.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN
# NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of the copyright holder.
#
###############################################################################
# Authors:
#    Rasmus Bo Soerensen (rasmus@rbscloud.dk)
#
###############################################################################

from lxml import etree
import paths
import subprocess
import util
from codeGen import aegeanCode
from codeGen import topCode
from codeGen.Component import Component
import re

class AegeanGen(object):
    '''
    The AegeanGen class handles the generation of the Aegean hardware platform
    '''
    def __init__(self,p,platform):
        self.p = p
        self.platform = platform
        self.nodes = util.findTag(self.platform,'nodes')
        self.memory = util.findTag(self.platform,'memory')
        self.board = util.findTag(self.platform,'board')
        self.IOPorts = []
        self.IPCores = dict({})
        self.Devs = dict({})
        self.genIPCores = dict({})
        self.genComps = dict({})
        self.SPMSizes = []

    def parseDevs(self):
        Devs = list(util.findTag(self.platform,'Devs'))
        for i in range(0,len(Devs)):
            Dev = Devs[i]
            name = Dev.get('DevType')
            self.Devs[name] = Dev

    def parseIPCores(self):
        IPCores = list(util.findTag(self.platform,'IPCores'))
        for i in range(0,len(IPCores)):
            IPCore = IPCores[i]
            name = IPCore.get('IPType')
            r = util.findTag(IPCore,'patmos')
            if str(r) == 'None': # The IPCore is not a patmos processor
                self.IPCores[name] = IPCore
            else: # The IPCore is a patmos processor
                self.IPCores[name] = r

    def parseSize(self,s):
        m = re.split('(\d+)([KMG]?)',s.upper())
        while '' in m:
            m.remove('')
        suffixMult = (1 << 0)
        if m[1]=='K':
            suffixMult = (1 << 10)
        elif m[1]=='M':
            suffixMult = (1 << 20)
        elif m[1]=='G':
            suffixMult = (1 << 30)
        return int(m[0])*suffixMult

    def generateNodes(self):
        nodes = list(self.nodes)
        for i in range(0,len(nodes)):
            node = nodes[i]
            IPTypeRef = node.get('IPTypeRef')
            SPMSize = node.get('SPMSize')
            self.SPMSizes.append(self.parseSize(SPMSize))
            if IPTypeRef not in self.genIPCores:
                IPCore = self.IPCores[IPTypeRef]
                b = util.findTag(IPCore,'bootrom')
                if str(b) == 'None':
                    if IPCore.tag == 'patmos':
                        raise SystemExit(' Error: Patmos specified with no bootapp: ' + IPTypeRef)
                    else:
                        continue
                bootapp = b.get('app')

                # Remove the bootapp tag from the patmos config
                IPCore.remove(b)

                # Add the Devs to the patmos configuration file
                IOsT = util.findTag(IPCore,'IOs')
                if str(IOsT) != 'None':
                    IOs = list(IOsT)
                    Devs = etree.Element('Devs')
                    for j in range(0,len(IOs)):
                        DevTypeRef = IOs[j].get('DevTypeRef')
                        Devs.append(self.Devs[DevTypeRef])
                    IPCore.append(Devs)

                # Write the patmos configration file
                et = etree.ElementTree(IPCore)
                et.write(self.p.TMP_BUILD_PATH + '/' + IPTypeRef + '.xml')

                # Generate the patmos file
                self.patmosGen(IPTypeRef,bootapp,self.p.TMP_BUILD_PATH + '/' + IPTypeRef + '.xml')
                self.genIPCores[IPTypeRef] = IPCore

    def generateMemory(self):
        if str(self.memory) == 'None':
            return
        DevTypeRef = self.memory.get('DevTypeRef')
        ID = self.memory.get('id')
        memory = self.Devs[DevTypeRef]
        entity = memory.get('entity')
        params = util.findTag(memory,'params')
        for i in range(0,len(list(params))):
            if params[i].get('name') == 'addr_width':
                addrWidth = params[i].get('value')
                break
        self.ssramGen(entity,addrWidth)
        self.arbiterGen(len(self.nodes),addrWidth,32,4)

    def addDeviceToQSF(self):
        boardName = self.board.get('name')
        family = self.board.get('family')
        device = self.board.get('device')
        SedString = 's|' + 'set_global_assignment -name FAMILY$' + '|'
        SedString+= 'set_global_assignment -name FAMILY "'+ family + '"|'
        Sed = ['sed','-i']
        Sed+= [SedString]
        Sed+= [self.p.QUARTUS_FILE_QSF]
        subprocess.call(Sed)

        SedString = 's|' + 'set_global_assignment -name DEVICE$' + '|'
        SedString+= 'set_global_assignment -name DEVICE '+ device + '|'
        Sed = ['sed','-i']
        Sed+= [SedString]
        Sed+= [self.p.QUARTUS_FILE_QSF]
        subprocess.call(Sed)

    def addGeneratedFilesToQSF(self):
        SedString = 's|' + 'set_global_assignment -name VERILOG_FILE ../PatmosCore.v' + '|'
        for IPType in self.genIPCores.keys():
            SedString+= 'set_global_assignment -name VERILOG_FILE ../'+IPType+'PatmosCore.v'
            SedString+='\\\n'

        f = open(self.p.BUILD_PATH+'/.argo_src','r')
        paths = f.readline().split(' ')
        for path in paths:
            if path != '':
                SedString+= 'set_global_assignment -name VHDL_FILE '+path
                SedString+='\\\n'

        SedString+= '|'
        Sed = ['sed','-i']
        Sed+= [SedString]
        Sed+= [self.p.QUARTUS_FILE_QSF]
        subprocess.call(Sed)

    def addPinsToQSF(self):
        SedString = 's|' + 'set_location_assignment PIN_XXX -to XXX' + '|'
        ports = list(util.findTag(self.board,'IOPorts'))
        for i in range(0,len(ports)): # For each port
            topSig = ports[i].get('name')
            signals = list(ports[i])
            for j in range(0,len(signals)): # For each signal
                signal = signals[j]
                # Find direction of port
                if signal.tag == 'out':
                    prefix='o'
                elif signal.tag == 'in':
                    prefix='i'
                elif signal.tag == 'inout':
                    prefix=''

                #node = signals[j].get('node')
                sig = signals[j].get('name')
                pins = signals[j].get('pin').split(',')
                pins.reverse()
                IOPort = [topSig,prefix+topSig+'_'+sig,signal.tag,len(pins)]
                self.IOPorts.append(IOPort)
                for k in reversed(range(0,len(pins))):
                    PinName = 'PIN_'+pins[k]
                    SignalName = prefix+topSig+'_'+sig
                    if len(pins) > 1:
                        SignalName += '['+str(k)+']'
                    SedString+='set_location_assignment '+ PinName + ' -to ' + SignalName + '\\\n'

        SedString+= '|'
        Sed = ['sed','-i']
        Sed+= [SedString]
        Sed+= [self.p.QUARTUS_FILE_QSF]
        subprocess.call(Sed)

    def generateTopLevel(self,aegean):
        top = topCode.getTop()

         # One Port for each signal in for loop
        for i in range(0,len(self.IOPorts)):
            IOPort = self.IOPorts[i]
            portType = 'std_logic'
            if IOPort[3] > 1:
                portType = 'std_logic_vector'
            top.entity.addPort(IOPort[1],IOPort[2],portType,IOPort[3])


        top.arch.declConstant('pll_mult','natural',1,'8')
        top.arch.declConstant('pll_div','natural',1,'5')
        top.arch.declSignal('clk_int','std_logic')

        top.arch.declSignal('int_res','std_logic')
        top.arch.declSignal('res_reg1,res_reg2','std_logic')
        top.arch.declSignal('res_cnt','unsigned',3,'"000"')

        top.arch.declSignal('sram_burst_m','ocp_burst_m')
        top.arch.declSignal('sram_burst_s','ocp_burst_s')

        # Declaration of the Tri state signals
        # One tri state for the sram possibly in a for loop for more tri states
        for IOPort in self.IOPorts:
            if IOPort[2] == 'inout':
                topCode.writeTriStateSig(top,IOPort[0],IOPort[3])

        topCode.attr(top)
        topCode.pll_reset(top)

         # The tristate logic and registers
        for IOPort in self.IOPorts:
            if IOPort[2] == 'inout':
                topCode.writeTriState(top,IOPort[0],IOPort[1])

        sram = topCode.getSram()
        top.arch.declComp(sram)

        topCode.bindAegean(aegean)
        top.arch.instComp(aegean,'cmp',True)
        topCode.bindSram(sram)
        top.arch.instComp(sram,'ssram')
        top.writeComp(self.p.TopFile)


    def generate(self,noc):
        self.parseDevs()
        self.parseIPCores()
        self.generateNodes()
        self.generateMemory()
        vendor = self.board.get('vendor')
        if vendor == 'Altera':
            self.addPinsToQSF()
            self.addDeviceToQSF()
            self.addGeneratedFilesToQSF()
        elif vendor == 'Xilinx':
            raise SystemExit(' Error: Unsupported vendor: ' + vendor)
        else:
            raise SystemExit(' Error: Unsupported vendor: ' + vendor)



        aegean = aegeanCode.getAegean()
        # add IO pins
        aegean.entity.addPort('led','out','std_logic_vector',9)
        aegean.entity.addPort('txd','out')
        aegean.entity.addPort('rxd','in')

        arbiter = aegeanCode.getArbiter(len(self.nodes))
        aegean.arch.declComp(arbiter)


        for IPType in self.genIPCores.keys():
            ledPort = None
            uartPort = None
            IPCore = self.genIPCores[IPType]
            IOs = util.findTag(IPCore,'IOs')
            for IO in list(IOs):
                DevTypeRef = IO.get('DevTypeRef')
                if DevTypeRef == 'Leds':
                    ledPort = True
                elif DevTypeRef == 'Uart':
                    uartPort = True
            patmos = aegeanCode.getPatmos(IPType,ledPort,uartPort)
            aegean.arch.declComp(patmos)
            self.genComps[IPType] = patmos

        aegeanCode.declareSignals(aegean)
        aegeanCode.setSPMSize(aegean,self.SPMSizes)

        for p in range(0,len(self.nodes)):
            patmos = self.nodes[p]
            label = patmos.get('id')
            IPType = patmos.get('IPTypeRef')

            ledPort = None
            txdPort = None
            rxdPort = None
            # TODO: this assumes that core 0 handles all I/O
            IOs = util.findTag(self.genIPCores[IPType],'IOs')
            for IO in list(IOs):
                DevTypeRef = IO.get('DevTypeRef')
                if p == 0:
                    if DevTypeRef == 'Leds':
                        ledPort = 'led'
                    elif DevTypeRef == 'Uart':
                        txdPort = 'txd'
                        rxdPort = 'rxd'
                elif DevTypeRef == 'Leds':
                    ledPort = 'open'
                elif DevTypeRef == 'Uart':
                    txdPort = 'open'
                    rxdPort = "'1'"
            comp = self.genComps[IPType]
            aegeanCode.bindPatmos(comp,p,ledPort,txdPort,rxdPort)
            aegean.arch.instComp(comp,label)

        aegean.arch.addToBody(aegeanCode.addSPM())
        aegeanCode.bindNoc(noc)
        aegean.arch.instComp(noc,'noc',True)
        aegeanCode.bindArbiter(arbiter,len(self.nodes))
        aegean.arch.instComp(arbiter,'arbit')

        aegean.writeComp(self.p.AegeanFile)

        self.generateTopLevel(aegean)
        return aegean

    def patmosGen(self,IPType,bootapp,configfile):
        Patmos = ['make','-C',self.p.PATMOSHW_PATH]
        Patmos+= ['BOOTAPP='+bootapp]
        Patmos+= ['BOOTBUILDDIR='+self.p.BUILD_PATH]
        Patmos+= ['HWBUILDDIR='+self.p.BUILD_PATH]
        Patmos+= ['HWMODULEPREFIX='+IPType]
        Patmos+= ['CONFIGFILE='+configfile]
        Patmos+= [self.p.BUILD_PATH+'/'+IPType+'PatmosCore.v']
        subprocess.call(Patmos)

    def ssramGen(self,entity,addr):
        Ssram = ['make','-C',self.p.PATMOSHW_PATH]
        Ssram+= ['HWBUILDDIR='+self.p.BUILD_PATH]
        Ssram+= ['MEMCTRL_ADDR_WIDTH='+str(addr)]
        Ssram+= [self.p.BUILD_PATH+'/'+entity+'.v']
        subprocess.call(Ssram)

    def arbiterGen(self,cnt,addr,data,burstLength):
        Arbiter = ['make','-C',self.p.PATMOSHW_PATH]
        Arbiter+= ['HWBUILDDIR='+self.p.BUILD_PATH]
        Arbiter+= ['ARBITER_CNT='+str(cnt)]
        Arbiter+= ['ARBITER_ADDR_WIDTH='+str(addr)]
        Arbiter+= ['ARBITER_DATA_WIDTH='+str(data)]
        Arbiter+= ['ARBITER_BURST_LENGTH='+str(burstLength)]
        Arbiter+= [self.p.BUILD_PATH+'/Arbiter.v']
        subprocess.call(Arbiter)
