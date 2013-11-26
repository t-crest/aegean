import util
import testCode

class TestGen(object):
    """
    The TestGen class handles the generation of a testbench for the Aegean hardware platform
    """
    def __init__(self,p,platform):
        self.p = p
        self.platform = platform
        self.IPCores = util.findTag(self.platform,"IPCores")
        self.nodes = util.findTag(self.platform,"nodes")


    def generate(self):
        f = open(self.p.TestFile, 'w')
        testCode.writeHeader(f)

        for p in range(0,len(self.nodes)):
            patmos = self.nodes[p]
            label = patmos.get('id')
            testCode.writeSignalSpySignals(f,label)

        testCode.writeAegeanInst(f)

        for p in range(0,len(self.nodes)):
            patmos = self.nodes[p]
            label = patmos.get('id')
            testCode.writeUartSpy(f,label)

        testCode.writeBaudIncBegin(f)

        testCode.writeWait(f)
        for p in range(0,len(self.nodes)):
            patmos = self.nodes[p]
            label = patmos.get('id')
            testCode.writeUartForce(f,label,1)

        testCode.writeWait(f)
        for p in range(0,len(self.nodes)):
            patmos = self.nodes[p]
            label = patmos.get('id')
            testCode.writeUartForce(f,label,0)

        testCode.writeBaudIncEnd(f)

        testCode.writeSimMem(f,self.p.MAIN_MEM)
        f.close()
