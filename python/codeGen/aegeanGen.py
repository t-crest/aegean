from lxml import etree
import paths
import subprocess
import util
from codeGen import aegeanCode
from codeGen import topCode
from codeGen.Component import Component

class AegeanGen(object):
    '''
    The AegeanGen class handles the generation of the Aegean hardware platform
    '''
    def __init__(self,p,platform):
        self.p = p
        self.platform = platform
        self.nodes = util.findTag(self.platform,'nodes')
        self.memory = util.findTag(self.platform,'memory')
        self.IOPorts = []
        self.IPCores = dict({})
        self.IODevs = dict({})
        self.genIPCores = dict({})
        self.genComps = dict({})

    def parseIODevs(self):
        IODevs = list(util.findTag(self.platform,'IODevs'))
        for i in range(0,len(IODevs)):
            IODev = IODevs[i]
            name = IODev.get('IODevType')
            self.IODevs[name] = IODev

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


    def generateNodes(self):
        nodes = list(self.nodes)
        for i in range(0,len(nodes)):
            node = nodes[i]
            IPTypeRef = node.get('IPTypeRef')
            if IPTypeRef not in self.genIPCores:
                IPCore = self.IPCores[IPTypeRef]
                b = util.findTag(IPCore,'bootrom')
                if str(b) == 'None':
                    if IPCore.tag == 'patmos':
                        raise SystemExit(' error: Patmos specified with no bootapp: ' + IPTypeRef)
                    else:
                        continue
                bootapp = b.get('app')

                # Remove the bootapp tag from the patmos config
                IPCore.remove(b)

                # Add the IODevs to the patmos configuration file
                IOsT = util.findTag(IPCore,'IOs')
                if str(IOsT) != 'None':
                    IOs = list(IOsT)
                    IODevs = etree.Element('IODevs')
                    for j in range(0,len(IOs)):
                        IODevTypeRef = IOs[j].get('IODevTypeRef')
                        IODevs.append(self.IODevs[IODevTypeRef])
                    IPCore.append(IODevs)

                # Write the patmos configration file
                et = etree.ElementTree(IPCore)
                et.write(self.p.TMP_BUILD_PATH + '/' + IPTypeRef + '.xml')

                # Generate the patmos file
                self.patmosGen(IPTypeRef,bootapp,self.p.TMP_BUILD_PATH + '/' + IPTypeRef + '.xml')
                self.genIPCores[IPTypeRef] = IPCore

        self.addGeneratedFiles()

    def addGeneratedFiles(self):
        SedString = 's|' + 'set_global_assignment -name VERILOG_FILE ../PatmosCore.v' + '|'
        index = 0
        for IPType in self.genIPCores.keys():
            SedString+= 'set_global_assignment -name VERILOG_FILE ../'+IPType+'PatmosCore.v'
            if index < len(self.genIPCores.keys())-1:
                SedString+='\\\n'
            index=index+1

        SedString+= '|'
        Sed = ['sed','-i']
        Sed+= [SedString]
        Sed+= [self.p.QUARTUS_FILE]
        subprocess.call(Sed)

    def generateMemory(self):
        if str(self.memory) == 'None':
            return
        IODevTypeRef = self.memory.get('IODevTypeRef')
        ID = self.memory.get('id')
        memory = self.IODevs[IODevTypeRef]
        params = util.findTag(memory,'params')
        for i in range(0,len(list(params))):
            if params[i].get('name') == 'addr_width':
                addrWidth = params[i].get('value')
                break
        self.ssramGen(addrWidth)
        self.arbiterGen(len(self.nodes),addrWidth,32,4)

    def addPinsToQPF(self):
        SedString = 's|' + 'set_location_assignment PIN_XXX -to XXX' + '|'
        ports = list(util.findTag(self.platform,'IOPorts'))
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
        Sed+= [self.p.QUARTUS_FILE]
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

        topCode.bindAegean(aegean)
        top.arch.instComp(aegean,'cmp',True)
        top.writeComp(self.p.TopFile)


    def generate(self,noc):
        self.parseIODevs()
        self.parseIPCores()
        self.generateNodes()
        self.generateMemory()
        self.addPinsToQPF()

        aegean = aegeanCode.getAegean()
        # add IO pins
        aegean.entity.addPort('led','out','std_logic_vector',9)
        aegean.entity.addPort('txd','out')
        aegean.entity.addPort('rxd','in')

        sram = aegeanCode.getSram()
        aegean.arch.declComp(sram)
        arbiter = aegeanCode.getArbiter(len(self.nodes))
        aegean.arch.declComp(arbiter)


        for IPType in self.genIPCores.keys():
            ledPort = None
            uartPort = None
            IPCore = self.genIPCores[IPType]
            IOs = util.findTag(IPCore,'IOs')
            for IO in list(IOs):
                IODevTypeRef = IO.get('IODevTypeRef')
                if IODevTypeRef == 'Leds':
                    ledPort = True
                elif IODevTypeRef == 'Uart':
                    uartPort = True
            patmos = aegeanCode.getPatmos(IPType,ledPort,uartPort)
            aegean.arch.declComp(patmos)
            self.genComps[IPType] = patmos

        aegeanCode.declareSignals(aegean)

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
                IODevTypeRef = IO.get('IODevTypeRef')
                if p == 0:
                    if IODevTypeRef == 'Leds':
                        ledPort = 'led'
                    elif IODevTypeRef == 'Uart':
                        txdPort = 'txd'
                        rxdPort = 'rxd'
                elif IODevTypeRef == 'Leds':
                    ledPort = 'open'
                elif IODevTypeRef == 'Uart':
                    txdPort = 'open'
                    rxdPort = "'1'"
            comp = self.genComps[IPType]
            aegeanCode.bindPatmos(comp,p,ledPort,txdPort,rxdPort)
            aegean.arch.instComp(comp,label)

        aegean.arch.addToBody(aegeanCode.addSPM())
        aegeanCode.bindNoc(noc)
        aegean.arch.instComp(noc,'noc',True)
        aegeanCode.bindSram(sram)
        aegean.arch.instComp(sram,'ssram')
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

    def ssramGen(self,addr):
        Ssram = ['make','-C',self.p.PATMOSHW_PATH]
        Ssram+= ['HWBUILDDIR='+self.p.BUILD_PATH]
        Ssram+= ['MEMCTRL_ADDR_WIDTH='+str(addr)]
        Ssram+= [self.p.BUILD_PATH+'/SsramBurstRW.v']
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