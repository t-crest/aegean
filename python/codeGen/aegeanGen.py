from lxml import etree
import paths
import subprocess
import util
from codeGen import aegeanCode

class AegeanGen(object):
    '''
    The AegeanGen class handles the generation of the Aegean hardware platform
    '''
    def __init__(self,p,platform):
        self.p = p
        self.platform = platform
        self.nodes = util.findTag(self.platform,'nodes')
        self.memory = util.findTag(self.platform,'memory')
        self.IPCores = util.findTag(self.platform,'IPCores')
        self.IODevs = util.findTag(self.platform,'IODevs')
        self.IOPorts = util.findTag(self.platform,'IOPorts')
        self.Devices = dict({})
        self.Cores = dict({})
        self.generated = dict({})

    def parseIODevs(self):
        IODevs = list(self.IODevs)
        for i in range(0,len(IODevs)):
            IODev = IODevs[i]
            name = IODev.get('IODevType')
            self.Devices[name] = IODev

    def parseIPCores(self):
        IPCores = list(self.IPCores)
        for i in range(0,len(IPCores)):
            IPCore = IPCores[i]
            name = IPCore.get('IPType')
            r = util.findTag(IPCore,'patmos')
            if str(r) == 'None': # The IPCore is not a patmos processor
                self.Devices[name] = IPCore
            else: # The IPCore is a patmos processor
                self.Devices[name] = r


    def generateNodes(self):
        nodes = list(self.nodes)
        for i in range(0,len(nodes)):
            node = nodes[i]
            IPTypeRef = node.get('IPTypeRef')
            if IPTypeRef not in self.generated:
                IPCore = self.Devices[IPTypeRef]
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
                    for j in range(0,len(IOs)):
                        IODevTypeRef = IOs[j].get('IODevTypeRef')
                        IPCore.append(self.Devices[IODevTypeRef])

                # Write the patmos configration file
                et = etree.ElementTree(IPCore)
                et.write(self.p.TMP_BUILD_PATH + '/' + IPTypeRef + '.xml')

                # Generate the patmos file
                self.patmosGen(IPTypeRef,bootapp,self.p.TMP_BUILD_PATH + '/' + IPTypeRef + '.xml')
                self.generated[IPTypeRef] = True


    def generateMemory(self):
        IODevTypeRef = self.memory.get('IODevTypeRef')
        ID = self.memory.get('id')
        memory = self.Devices[IODevTypeRef]
        params = util.findTag(memory,'params')
        param = util.findTag(params,'param')
        addrWidth = param.get('addr_width')
        self.ssramGen(addrWidth)
        self.arbiterGen(len(self.nodes),addrWidth,32,4)

    def generateIOPorts(self):
        SedString = 's|' + 'set_location_assignment PIN_XXX -to XXX' + '|'
        ports = list(self.IOPorts)
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

                sig = signals[j].get('name')
                pins = signals[j].get('pin').split(',')
                pins.reverse()

                for k in reversed(range(0,len(pins))):
                    PinName = 'PIN_'+pins[k]
                    SignalName = prefix+topSig+'_'+sig+'['+str(k)+']'
                    SedString+='set_location_assignment '+ PinName + ' -to ' + SignalName + '\\\n'

        SedString+= '|'
        Sed = ['sed','-i']
        Sed+= [SedString]
        Sed+= [self.p.QUARTUS_FILE]
        subprocess.call(Sed)

    def generateTopLevel(self):
        SedString = 's|' + 'set_global_assignment -name VERILOG_FILE ../PatmosCore.v' + '|'
        index = 0
        for i in self.generated.keys():
            IPType = i
            print('IPType: '+IPType)

            SedString+= 'set_global_assignment -name VERILOG_FILE ../'+IPType+'PatmosCore.v'
            if index < len(self.generated.keys())-1:
                SedString+='\\\n'
            index=index+1

        SedString+= '|'
        Sed = ['sed','-i']
        Sed+= [SedString]
        Sed+= [self.p.QUARTUS_FILE]
        subprocess.call(Sed)

    def generate(self):
        self.parseIODevs()
        self.parseIPCores()
        self.generateNodes()
        self.generateIOPorts()
        self.generateTopLevel()
        f = open(self.p.AegeanFile, 'w')
        aegeanCode.writeHeader(f)

        for i in range(0,len(self.nodes)):
            aegeanCode.writeArbiterCompPort(f,i)
            if i != len(self.nodes)-1:
                f.write(';')

        aegeanCode.writeArbiterCompEnd(f)

        for i in range(0,len(self.IPCores)):
            IPType = self.IPCores[i].get('IPType')
            aegeanCode.writePatmosComp(f,IPType)

        aegeanCode.writeSignals(f)

        for p in range(0,len(self.nodes)):
            patmos = self.nodes[p]
            label = patmos.get('id')
            IPType = patmos.get('IPTypeRef')
            # TODO: this assumes that core 0 handles all I/O
            if p == 0:
                ledPort = 'led'
                txdPort = 'txd'
                rxdPort = 'rxd'
            else:
                ledPort = 'open'
                txdPort = 'open'
                rxdPort = "'1'"
            aegeanCode.writePatmosInst(f,label,IPType,p,ledPort,txdPort,rxdPort)

        aegeanCode.writeInterconnect(f)

        for i in range(0,len(self.nodes)):
            aegeanCode.writeArbiterInstPort(f,i)
            if i != len(self.nodes)-1:
                f.write(',')

        aegeanCode.writeFooter(f)

        f.close()

    def patmosGen(self,IPType,bootapp,configfile):
        Patmos = ['make','-C',self.p.CHISEL_PATH]
        Patmos+= ['BOOTAPP='+bootapp]
        Patmos+= ['BOOTBUILDDIR='+self.p.BUILD_PATH]
        Patmos+= ['CHISELBUILDDIR='+self.p.BUILD_PATH]
        Patmos+= ['HWMODULEPREFIX='+IPType]
        Patmos+= ['CONFIGFILE='+configfile]
        Patmos+= [self.p.BUILD_PATH+'/'+IPType+'PatmosCore.v']
        subprocess.call(Patmos)

    def ssramGen(self,addr):
        Ssram = ['make','-C',self.p.CHISEL_PATH]
        Ssram+= ['CHISELBUILDDIR='+self.p.BUILD_PATH]
        Ssram+= ['MEMCTRL_ADDR_WIDTH='+str(addr)]
        Ssram+= [self.p.BUILD_PATH+'/SsramBurstRW.v']
        subprocess.call(Ssram)

    def arbiterGen(self,cnt,addr,data,burstLength):
        Arbiter = ['make','-C',self.p.CHISEL_PATH]
        Arbiter+= ['CHISELBUILDDIR='+self.p.BUILD_PATH]
        Arbiter+= ['ARBITER_CNT='+str(cnt)]
        Arbiter+= ['ARBITER_ADDR_WIDTH='+str(addr)]
        Arbiter+= ['ARBITER_DATA_WIDTH='+str(data)]
        Arbiter+= ['ARBITER_BURST_LENGTH='+str(burstLength)]
        Arbiter+= [self.p.BUILD_PATH+'/Arbiter.v']
        subprocess.call(Arbiter)
