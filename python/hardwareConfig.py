from nocGen import NoCGen
from cmpGen import CMPGen
from lxml import etree
import paths
import subprocess

class HWConfig(object):
    """
    The HWConfig class handles the hardware configuration of the aegean platform
    """
    def __init__(self,aegean):
        self.platform = list(aegean)[0]
        self.IPCores = list(self.platform)[2]
        et = etree.ElementTree(self.platform)
        et.write(paths.GEN_PLAT)

    def config(self):
        noc = NoCGen(self.platform)
        noc.config()
        noc.generate()
        cmp = CMPGen(self.platform)
        cmp.generate()





