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


    def generate(self,aegean):
        test = testCode.getTest()

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
                            testCode.writeSignalSpySignals(test,label)
                            break
                        self.spys[label] = False
                    break


        testCode.bindAegean(aegean)
        test.arch.instComp(aegean,'aegean',True)
        testCode.writeAegeanInst(test)

        for p in range(0,len(self.nodes)):
            node = self.nodes[p]
            IPTypeRef = node.get('IPTypeRef')
            label = node.get('id')
            if self.spys[label]:
                testCode.writeUartSpy(test,label,IPTypeRef)

        s = testCode.writeBaudIncBegin()

        s+= testCode.writeWait()
        for p in range(0,len(self.nodes)):
            node = self.nodes[p]
            IPTypeRef = node.get('IPTypeRef')
            label = node.get('id')
            if self.spys[label]:
                s+= testCode.writeUartForce(label,1,IPTypeRef)

        s+= testCode.writeWait()
        for p in range(0,len(self.nodes)):
            IPTypeRef = node.get('IPTypeRef')
            node = self.nodes[p]
            label = node.get('id')
            if self.spys[label]:
                s+= testCode.writeUartForce(label,0,IPTypeRef)

        s+= testCode.writeBaudIncEnd()
        test.arch.addToBody(s)

        testCode.writeSimMem(test,self.p.MAIN_MEM)

        test.writeComp(self.p.TestFile)
