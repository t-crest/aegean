import util
from codeGen import testCode

class TestGen(object):
    """
    The TestGen class handles the generation of a testbench for the Aegean hardware platform
    """
    def __init__(self,p,platform):
        self.p = p
        self.platform = platform
        self.IPCores = util.findTag(self.platform,"IPCores")
        self.nodes = util.findTag(self.platform,"nodes")
        self.spys = dict({})


    def generate(self):
        f = open(self.p.TestFile, 'w')
        testCode.writeHeader(f)

        for p in range(0,len(self.nodes)):
            node = self.nodes[p]
            label = node.get('id')
            IPTypeRef = node.get('IPTypeRef')
            for IPCore in list(self.IPCores):
                if IPCore.get('IPType') == IPTypeRef:
                    pat = util.findTag(IPCore,'patmos')
                    IOs = util.findTag(pat,'IOs')
                    for IO in list(IOs):
                        IODevTypeRef = IO.get('IODevTypeRef')
                        if IODevTypeRef == 'Uart':
                            self.spys[label] = True
                            testCode.writeSignalSpySignals(f,label)
                            break
                        self.spys[label] = False
                    break



        testCode.writeAegeanInst(f)

        for p in range(0,len(self.nodes)):
            node = self.nodes[p]
            label = node.get('id')
            if self.spys[label]:
                testCode.writeUartSpy(f,label)

        testCode.writeBaudIncBegin(f)

        testCode.writeWait(f)
        for p in range(0,len(self.nodes)):
            node = self.nodes[p]
            label = node.get('id')
            if self.spys[label]:
                testCode.writeUartForce(f,label,1)

        testCode.writeWait(f)
        for p in range(0,len(self.nodes)):
            node = self.nodes[p]
            label = node.get('id')
            if self.spys[label]:
                testCode.writeUartForce(f,label,0)

        testCode.writeBaudIncEnd(f)

        testCode.writeSimMem(f,self.p.MAIN_MEM)
        f.close()
