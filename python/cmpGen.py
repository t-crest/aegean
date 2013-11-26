from lxml import etree
import paths
import subprocess
import util
import aegeanCode

class CMPGen(object):
    """
    The CMPGen class handles the generation of the Aegean hardware platform
    """
    def __init__(self,p,platform):
        self.p = p
        self.platform = platform
        self.nodes = util.findTag(self.platform,"nodes")
        self.memory = util.findTag(self.platform,"memory")
        self.IPCores = util.findTag(self.platform,"IPCores")
        self.IODevs = util.findTag(self.platform,"IODevs")
        self.IOPorts = util.findTag(self.platform,"IOPorts")


    def IPgen(self):
        self.ssramGen(21)
        self.arbiterGen(len(self.nodes),21,32,4)
        # Arbiter addr width
        # Arbiter data width
        # The burst length of 4 should be read from a config file
        # At the moment it is not configurable
        SedString = 's|' + 'set_global_assignment -name VERILOG_FILE ../PatmosCore.v' + '|'
        for i in range(0,len(self.IPCores)):
            IPType = self.IPCores[i].get('IPType')

            patmos = util.findTag(self.IPCores[i],"patmos")
            app = ""
            for j in range(0,len(patmos)):
                if patmos[j].tag == 'bootrom':
                    app = patmos[j].get('app')
                    break

            et = etree.ElementTree(patmos)
            et.write(self.p.TMP_BUILD_PATH + '/' + IPType + '.xml')
            self.patmosGen(IPType,app,self.p.TMP_BUILD_PATH + '/' + IPType + '.xml')
            SedString+= 'set_global_assignment -name VERILOG_FILE ../'+IPType+'PatmosCore.v'
            if i < len(self.IPCores)-1:
                SedString+='\\\n'

        SedString+= '|'
        Sed = ['sed','-i']
        Sed+= [SedString]
        Sed+= [self.p.QUARTUS_FILE]
        subprocess.call(Sed)

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

    def genDev(self,IODev):
        name = IODev.get("IODevType")
        entity = IODev.get("entity")
        iface = IODev.get("iface")
        params = util.findTag(IODev,"params")

        if entity == "SsramBurstRW":
            pass
        elif entity == "UART":
            pass
        elif entity == "Leds":
            pass



        util.findType(self.IODevs,"IODevType","Ssram")

    def genPins(self):
        ports = list(self.IOPorts)
        for i in range(0,len(ports)): # For each port
            topSig = ports[i].get("name")
            signals = list(ports[i])
            for j in range(0,len(signals)): # For each signal
                sig = signals[j].get("name")
                pins = signals[j].get("pin").split(',')

                for k in range(0,len(pins)):
                    PinName = 'PIN_'+pins[k]
                    SignalName = topSig+'_'+sig+'['+str(k)+']'
                    print('SignalName: ' + SignalName)


    def arbiterGen(self,cnt,addr,data,burstLength):
        Arbiter = ['make','-C',self.p.CHISEL_PATH]
        Arbiter+= ['CHISELBUILDDIR='+self.p.BUILD_PATH]
        Arbiter+= ['ARBITER_CNT='+str(cnt)]
        Arbiter+= ['ARBITER_ADDR_WIDTH='+str(addr)]
        Arbiter+= ['ARBITER_DATA_WIDTH='+str(data)]
        Arbiter+= ['ARBITER_BURST_LENGTH='+str(burstLength)]
        Arbiter+= [self.p.BUILD_PATH+'/Arbiter.v']
        subprocess.call(Arbiter)

    def generate(self):
        self.IPgen()
        #self.genPins()
        f = open(self.p.AegeanFile, 'w')
        aegeanCode.writeHeader(f)


        for i in range(0,len(self.nodes)):
            aegeanCode.writeArbiterCompPort(f,i)
            if i != len(self.nodes)-1:
                f.write(''';''')

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
                ledPort = "led"
                txdPort = "txd"
                rxdPort = "rxd"
            else:
                ledPort = "open"
                txdPort = "open"
                rxdPort = "'1'"

            aegeanCode.writePatmosInst(f,label,IPType,p,ledPort,txdPort,rxdPort)

        aegeanCode.writeInterconnect(f)

        for i in range(0,len(self.nodes)):
            aegeanCode.writeArbiterInstPort(f,i)
            if i != len(self.nodes)-1:
                f.write(''',''')

        aegeanCode.writeFooter(f)

        f.close()


