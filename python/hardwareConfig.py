from nocGen import NoCGen
from cmpGen import CMPGen
from lxml import etree
import aegean
import subprocess

class HWConfig(object):
    """
    The HWConfig class handles the hardware configuration of the aegean platform
    """
    def __init__(self,aegean):
        self.platform = list(aegean)[0]
        self.IPCores = list(self.platform)[2]

    def config(self):
        self.createHardware()

    def createHardware(self):
        print("Creating Hardware...",end="")
        noc = NoCGen(self.platform)
        noc.config()
        noc.generate()
        cmp = CMPGen(self.platform)
        cmp.generate()
        self.hardwareDone()

    def hardwareDone(self):
        print("Still To Be Done")

    def compile(self):
        pass



