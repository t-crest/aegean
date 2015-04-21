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
from codeGen import ocp
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
        self.IOSignals = []
        self.IPCores = dict({})
        self.Devs = dict({})
        self.genIPCores = dict({})
        self.genComps = dict({})
        self.genFiles = []
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

    def parseIOPorts(self):
        clock = util.findTag(self.board,'clock')
        self.IOSignals.append(['clock',clock.get('name'),'in',1,[clock.get('pin')]])
        for port in util.findTag(self.board,'IOPorts'): # For each port
            portName = port.get('name')
            for signal in port: # For each signal
                # Find direction of signal
                if signal.tag == 'out':
                    prefix='o'
                elif signal.tag == 'in':
                    prefix='i'
                elif signal.tag == 'inout':
                    prefix=''

                sigName = signal.get('name')
                pins = signal.get('pin').split(',')
                pins.reverse()
                signalName = prefix+portName+'_'+sigName
                IOSignal = [portName,signalName,signal.tag,len(pins),pins]
                self.IOSignals.append(IOSignal)

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

            BootApp = node.get('BootApp')
            IPTypeID = IPTypeRef
            if str(BootApp) != 'None':
                IPTypeID = (IPTypeRef + '-' + BootApp).replace('-','_')
            if IPTypeID not in self.genIPCores: # IPTypeRef -> IPTypeID
                IPCore = self.IPCores[IPTypeRef] 
                b = util.findTag(IPCore,'bootrom')
                if str(b) == 'None' and str(BootApp) == 'None':
                    if IPCore.tag == 'patmos':
                        raise SystemExit(__file__ +': Error: Patmos specified with no bootapp: ' + IPTypeRef)
                    else:
                        continue
                if str(BootApp) == 'None':
                    BootApp = b.get('app')
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
                et.write(self.p.TMP_BUILD_PATH + '/' + IPTypeID.replace('-','_') + '.xml') # IPTypeRef ->IPTypeRef + IPTypeID

                # Generate the patmos file
                self.patmosGen(IPTypeID.replace('-','_'),BootApp,self.p.TMP_BUILD_PATH + '/' + IPTypeID.replace('-','_') + '.xml') # IPTypeRef -> IPTypeID
                self.genIPCores[IPTypeID.replace('-','_')] = IPCore # IPTypeRef -> IPTypeID

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
                self.ocpBurstAddrWidth = params[i].get('value')
                break
        self.ssramGen(entity,self.ocpBurstAddrWidth)
        self.arbiterGen(len(self.nodes),self.ocpBurstAddrWidth,32,4)

        aegeanCode.writeConfig(self.p.OcpConfFile,self.ocpBurstAddrWidth)

    def addDeviceToQSF(self):
        boardName = self.board.get('name')
        family = self.board.get('family')
        device = self.board.get('device')
        sedString = 's|' + 'set_global_assignment -name FAMILY$' + '|'
        sedString+= 'set_global_assignment -name FAMILY "'+ family + '"|'
        Sed = ['sed','-i','']
        Sed+= [sedString]
        Sed+= [self.p.QUARTUS_FILE_QSF]
        ret = subprocess.call(Sed)
        if ret != 0:
            raise SystemExit(__file__ +': Error: sed: return value: ' + str(ret))

        sedString = 's|' + 'set_global_assignment -name DEVICE$' + '|'
        sedString+= 'set_global_assignment -name DEVICE '+ device + '|'
        Sed = ['sed','-i','']
        Sed+= [sedString]
        Sed+= [self.p.QUARTUS_FILE_QSF]
        ret = subprocess.call(Sed)
        if ret != 0:
            raise SystemExit(__file__ +': Error: sed: return value: ' + str(ret))

    def addDeviceToCDF(self):
        device = self.board.get('device')
        sedString = 's|' + 'Device PartName(DEVICE) Path("build/PROJECTNAME/quartus/output_files/") File("PROJECTNAME_top.sof")$' + '|'
        sedString+= 'Device PartName('+ device + ') Path("build/'+ self.p.projectname + '/quartus/output_files/") File("'+ self.p.projectname + '_top.sof")|'
        Sed = ['sed','-i','']
        Sed+= [sedString]
        Sed+= [self.p.QUARTUS_FILE_CDF]
        ret = subprocess.call(Sed)
        if ret != 0:
            raise SystemExit(__file__ +': Error: sed: return value: ' + str(ret))

    def addGeneratedFilesToQSF(self):
        sedString = 's|' + 'set_global_assignment -name VERILOG_FILE GENERATED' + '|'
        for genFile in self.genFiles:
            sedString+= 'set_global_assignment -name VERILOG_FILE '+genFile
            sedString+='\\\n'

        f = open(self.p.BUILD_PATH+'/.argo_src','r')
        paths = f.readline().split(' ')
        for path in paths:
            if path != '':
                sedString+= 'set_global_assignment -name VHDL_FILE '+path
                sedString+='\\\n'

        sedString+= '|'
        Sed = ['sed','-i','']
        Sed+= [sedString]
        Sed+= [self.p.QUARTUS_FILE_QSF]
        ret = subprocess.call(Sed)
        if ret != 0:
            raise SystemExit(__file__ +': Error: sed: return value: ' + str(ret))

    def addPinsToQSF(self):
        sedString = 's|' + 'set_location_assignment PIN_XXX -to XXX' + '|'
        for IOSignal in self.IOSignals: # For each signal
            pins = IOSignal[4]
            for k in reversed(range(0,len(pins))):
                PinName = 'PIN_'+pins[k]
                signalName = IOSignal[1]
                if IOSignal[3] > 1:
                    signalName += '['+str(k)+']'
                sedString+='set_location_assignment '+ PinName + ' -to ' + signalName + '\\\n'

        sedString+= '|'
        Sed = ['sed','-i','']
        Sed+= [sedString]
        Sed+= [self.p.QUARTUS_FILE_QSF]
        ret = subprocess.call(Sed)
        if ret != 0:
            raise SystemExit(__file__ +': Error: sed: return value: ' + str(ret))

    def generateTopLevel(self,aegean):
        vendor = self.board.get('vendor')
        if vendor == 'Altera':
            self.addPinsToQSF()
            self.addDeviceToQSF()
            self.addDeviceToCDF()
            self.addGeneratedFilesToQSF()
        elif vendor == 'Xilinx':
            #raise SystemExit(__file__ +': Error: Unsupported vendor: ' + vendor)
            print("Project files not generated!!")
        else:
            raise SystemExit(__file__ +': Error: Unsupported vendor: ' + vendor)

        top = topCode.getTop()

        # One Port for each signal in for loop
        for IOSignal in self.IOSignals:
            portType = 'std_logic'
            if IOSignal[3] > 1:
                portType = 'std_logic_vector'
            top.entity.addPort(IOSignal[1],IOSignal[2],portType,IOSignal[3]) # (name,direction,portType,len(pins))


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
        for IOSignal in self.IOSignals:
            if IOSignal[2] == 'inout':
                topCode.writeTriStateSig(top,IOSignal[0],IOSignal[3])

        topCode.attr(top)
        topCode.reset(top)

        sramType = self.memory.get('DevTypeRef')
        sramDev = self.Devs[sramType]
        sramPorts = util.findTag(sramDev,'ports')
        if sramPorts != None:
            sramPorts = list(sramPorts)
        sramParams = list(util.findTag(sramDev,'params'))
        if sramParams != None:
            sramParams = list(sramParams)
        sramEntity = sramDev.get('entity')
        sramIFace = sramDev.get('iface')

        # The tristate logic and registers
        for IOSignal in self.IOSignals:
            if IOSignal[2] == 'inout':
                topCode.writeTriState(top,IOSignal[0],sramEntity,IOSignal[1])

        sram = Component(sramEntity)
        sram.entity.addPort('clk')
        sram.entity.addPort('reset')
        for param in sramParams:
            if param.get('addr_width') != 'None':
                addrWidth = param.get('value')
        ocp.addSlavePort(sram,sramIFace,addrWidth)
        if sramPorts != None:
            for port in sramPorts:
                width = port.get('width')
                if port.tag == 'outport':
                    if width != None:
                        sram.entity.addPort(port.get('name'),'out','std_logic_vector',int(width))
                    else:
                        sram.entity.addPort(port.get('name'),'out')
                elif port.tag == 'inport':
                    if width != None:
                        sram.entity.addPort(port.get('name'),'in','std_logic_vector',int(width))
                    else:
                        sram.entity.addPort(port.get('name'),'in')

        clkPin = 'open'
        if sramEntity == 'SSRam32Ctrl':
            clkPin = 'oSRAM_CLK'
        topCode.pll(top,vendor,clkPin)
        top.arch.declComp(sram)

        topCode.bindAegean(aegean,len(self.nodes))
        top.arch.instComp(aegean,'cmp',True)
        topCode.bindSram(sram,sramEntity,'sram_burst_m','sram_burst_s')
        top.arch.instComp(sram,'ssram')
        top.writeComp(self.p.TopFile)

        return top


    def generate(self,noc):
        self.parseDevs()
        self.parseIPCores()
        self.parseIOPorts()
        self.generateNodes()
        self.generateMemory()

        vlog_src = open(self.p.BUILD_PATH+'/.vlog_src','w')
        for f in self.genFiles:
            if f.endswith('.v'):
                vlog_src.write(self.p.BUILD_PATH + f[2:] + ' ')
        

        aegean = aegeanCode.getAegean()
        # add IO pins
        aegean.entity.addPort('led','out','std_logic_vector',9)
        #aegean.entity.addPort('txd','out')
        #aegean.entity.addPort('rxd','in')

        arbiter = aegeanCode.getArbiter(len(self.nodes),self.ocpBurstAddrWidth)
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
                    ledWidth = 9 # TODO: extract from XML
                if DevTypeRef == 'Led':
                    ledPort = True
                    ledWidth = 1
                elif DevTypeRef == 'Uart':
                    uartPort = True
            patmos = aegeanCode.getPatmos(IPType,ledPort,ledWidth,uartPort,self.ocpBurstAddrWidth)
            aegean.arch.declComp(patmos)
            self.genComps[IPType] = patmos

        aegeanCode.declareSignals(aegean)
        aegeanCode.setSPMSize(aegean,self.SPMSizes)

        for p in range(0,len(self.nodes)):
            patmos = self.nodes[p]
            label = patmos.get('id')
            IPType = patmos.get('IPTypeRef')
            BootApp = patmos.get('BootApp')
            if str(BootApp) != 'None':
                IPType = (IPType + '-' + BootApp).replace('-','_')

            ledPort = None
            txdPort = None
            rxdPort = None
            # TODO: this assumes that core 0 handles all I/O
            IOs = util.findTag(self.genIPCores[IPType],'IOs')
            for IO in list(IOs):
                DevTypeRef = IO.get('DevTypeRef')
                
                if DevTypeRef == 'Leds':
                    ledPort = 'leds' + str(p) 
                    ledWidth = 9
                    aegean.entity.addPort('leds' + str(p),'out','std_logic_vector',9)
                elif DevTypeRef == 'Led':
                    ledPort = 'led' + str(p)
                    aegean.entity.addPort('led' + str(p),'out','std_logic')
                    ledWidth = 1
                elif DevTypeRef == 'Uart':
                    txdPort = 'txd' + str(p)
                    rxdPort = 'rxd' + str(p)
                    aegean.entity.addPort('txd' + str(p),'out')
                    aegean.entity.addPort('rxd' + str(p),'in')
            comp = self.genComps[IPType]
            aegeanCode.bindPatmos(comp,len(self.nodes),p,ledPort,txdPort,rxdPort)
            aegean.arch.instComp(comp,label)

        aegean.arch.addToBody(aegeanCode.addSPM())
        aegeanCode.bindNoc(noc)
        aegean.arch.instComp(noc,'noc',True)
        aegeanCode.bindArbiter(arbiter,len(self.nodes))
        aegean.arch.instComp(arbiter,'arbit')

        aegean.writeComp(self.p.AegeanFile)

        return aegean

    def patmosGen(self,IPType,bootapp,configfile):
        Patmos = ['make','-C',self.p.PATMOSHW_PATH]
        Patmos+= ['BOOTAPP='+bootapp]
        Patmos+= ['BOOTBUILDDIR='+self.p.BUILD_PATH]
        Patmos+= ['HWBUILDDIR='+self.p.BUILD_PATH]
        Patmos+= ['HWMODULEPREFIX='+IPType]
        Patmos+= ['CONFIGFILE='+configfile]
        Patmos+= [self.p.BUILD_PATH+'/'+IPType+'PatmosCore.v']
        ret = subprocess.call(Patmos)
        if ret != 0:
            raise SystemExit(__file__ +': Error: Generation of Patmos: return value: ' + str(ret))

        self.genFiles.append('../'+IPType+'PatmosCore.v')

    def ssramGen(self,entity,addr):
        Ssram = ['make','-C',self.p.PATMOSHW_PATH]
        Ssram+= ['HWBUILDDIR='+self.p.BUILD_PATH]
        Ssram+= ['MEMCTRL_ADDR_WIDTH='+str(addr)]
        Ssram+= [self.p.BUILD_PATH+'/'+entity+'.v']
        ret = subprocess.call(Ssram)
        if ret != 0:
            raise SystemExit(__file__ +': Error: Generation of Sram controller: return value: ' + str(ret))

        self.genFiles.append('../'+entity+'.v')

    def arbiterGen(self,cnt,addr,data,burstLength):
        Arbiter = ['make','-C',self.p.PATMOSHW_PATH]
        Arbiter+= ['HWBUILDDIR='+self.p.BUILD_PATH]
        Arbiter+= ['ARBITER_CNT='+str(cnt)]
        Arbiter+= ['ARBITER_ADDR_WIDTH='+str(addr)]
        Arbiter+= ['ARBITER_DATA_WIDTH='+str(data)]
        Arbiter+= ['ARBITER_BURST_LENGTH='+str(burstLength)]
        Arbiter+= [self.p.BUILD_PATH+'/TdmArbiterWrapper.v']
        ret = subprocess.call(Arbiter)
        if ret != 0:
            raise SystemExit(__file__ +': Error: Generation of memory arbiter: return value: ' + str(ret))

        self.genFiles.append('../TdmArbiterWrapper.v')
