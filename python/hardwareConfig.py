from nocGen import NoCGen
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

    def IPgen(self):
        for i in range(0,len(self.IPCores)):
            IPType = self.IPCores[i].get("IPType")

            patmos = list(self.IPCores[i])[0]
            app = ""
            for j in range(0,len(patmos)):
                if patmos[j].tag == "bootrom":
                    app = patmos[j].get("app")
                    break

            et = etree.ElementTree(patmos)
            et.write(aegean.TMP_DIR + IPType + ".xml")
         #   self.patmosGen(IPType,app,aegean.TMP_DIR + IPType + ".xml")

    def patmosGen(self,IPType,bootapp,configfile):
        Patmos = ["make","-C",aegean.PATMOS_PATH]
        Patmos+= ["BOOTAPP="+bootapp]
        Patmos+= ["BOOTBUILDDIR="+aegean.BUILD_PATH]
        Patmos+= ["CHISELBUILDDIR="+aegean.BUILD_PATH]
        Patmos+= ["HWMODULEPREFIX="+IPType]
        Patmos+= ["CONFIGFILE="+configfile]
        Patmos+= ["gen"]
        subprocess.call(Patmos)

#make -C $(PATMOS_PATH) \
#     BOOTAPP=$(PATMOS_BOOTAPP) \
#     BOOTBUILDDIR=$(BUILD_PATH) \
#     CHISELBUILDDIR=$(BUILD_PATH)
#     HWMODULEPREFIX=$(PREFIX)
#     CONFIGFILE=$(CONFIGFILE_PATH)
#     gen
#sed -i 's/module Patmos(input clk,/module Patmos1(input clk,/g' Patmos.test.v


    def config(self):
        self.createHardware()

    def createHardware(self):
        print("Creating Hardware...",end="")
        noc = NoCGen(self.platform)
        noc.config()
        noc.generate()
        self.IPgen()
        self.hardwareDone()

    def hardwareDone(self):
        print("Still To Be Done")

    def compile(self):
        pass



