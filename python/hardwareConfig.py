from codeGen.nocGen import NoCGen
from codeGen.aegeanGen import AegeanGen
from codeGen.testGen import TestGen
from lxml import etree
import paths
import subprocess
import util

class HWConfig(object):
    """
    The HWConfig class handles the hardware configuration of the aegean platform
    """
    def __init__(self,p,aegean):
        self.p = p
        self.platform = util.findTag(aegean,"platform")
        self.IPCores = util.findTag(self.platform,"IPCores")
        et = etree.ElementTree(self.platform)
        et.write(self.p.GEN_PLAT)

    def config(self):
        noc = NoCGen(self.p,self.platform)
        noc.config()
        noc.generate()
        cmp = AegeanGen(self.p,self.platform)
        cmp.generate()
        test = TestGen(self.p,self.platform)
        test.generate()





