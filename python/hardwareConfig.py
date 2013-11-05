from nocGen import NoCGen

class HWConfig(object):
    """
    The HWConfig class handles the hardware configuration of the aegean platform
    """
    def __init__(self,aegean):
        self.platform = list(aegean)[0]

    def config(self):
        self.createHardware()

    def createHardware(self):
        print("Creating Hardware...",end="")
        noc = NoCGen(self.platform)
        noc.config()
        noc.generate()
        self.hardwareDone()

    def hardwareDone(self):
        print("Still To Be Done")

    def compile(self):
        pass


