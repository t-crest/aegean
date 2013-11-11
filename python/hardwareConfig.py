from nocGen import NoCGen
from cmpGen import CMPGen
from testGen import TestGen
from lxml import etree
import paths
import subprocess

class HWConfig(object):
    """
    The HWConfig class handles the hardware configuration of the aegean platform
    """
    def __init__(self,p,aegean):
        self.p = p
        self.platform = list(aegean)[0]
        self.IPCores = list(self.platform)[2]
        et = etree.ElementTree(self.platform)
        et.write(self.p.GEN_PLAT)

    def config(self):
        noc = NoCGen(self.p,self.platform)
        noc.config()
        noc.generate()
        cmp = CMPGen(self.p,self.platform)
        cmp.generate()
        test = TestGen(self.p,self.platform)
        test.generate()





