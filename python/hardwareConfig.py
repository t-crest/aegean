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
        nocComp = NoCGen(self.p,self.platform)
        nocComp.config()
        noc = nocComp.generate()
        aegeanGen = AegeanGen(self.p,self.platform)
        aegean = aegeanGen.generate(noc)
        testGen = TestGen(self.p,self.platform)
        test = testGen.generate(aegean)

#        VCOM = ['vcom','-quiet',self.p.NOCFile]
#        VCOM+= [self.p.AegeanFile]
#        VCOM+= [self.p.TopFile]
#        VCOM+= [self.p.TestFile]
#        VCOM+= [self.p.ConfFile]
#        VCOM+= ['-work',self.p.BUILD_PATH+'/work']
#        subprocess.call(VCOM)

