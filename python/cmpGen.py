from lxml import etree
import aegean
import subprocess

class CMPGen(object):
    """
    The CMPGen class handles the generation of the Aegean hardware platform
    """
    def __init__(self,platform):
        self.platform = platform
        self.IPCores = list(self.platform)[2]
        self.nodes = list(self.platform)[1]

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
            et.write(aegean.GEN_DIR + IPType + ".xml")
            self.patmosGen(IPType,app,aegean.GEN_DIR + IPType + ".xml")

    def patmosGen(self,IPType,bootapp,configfile):
        Patmos = ["make","-C",aegean.PATMOS_PATH]
        Patmos+= ["BOOTAPP="+bootapp]
        Patmos+= ["BOOTBUILDDIR="+aegean.BUILD_PATH]
        Patmos+= ["CHISELBUILDDIR="+aegean.BUILD_PATH]
        Patmos+= ["HWMODULEPREFIX="+IPType]
        Patmos+= ["CONFIGFILE="+configfile]
        Patmos+= ["gen"]
        subprocess.call(Patmos)

    def generate(self):
        self.IPgen()
        #self.nodes
        f = open(aegean.AegeanFile, 'w')
        f.write('''\ ''')

        f.close()

