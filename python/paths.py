import os

class Paths(object):
    """docstring for Paths"""
    def __init__(self, projectname):
        self.projectname = projectname

        self.AEGEAN_PATH = os.getcwd()

        self.XMLSCHEME = self.AEGEAN_PATH + '/xmlNotes/Aegean.xsd'

        self.POSEIDON_PATH = self.AEGEAN_PATH + '/../poseidon'
        self.POSEIDON_CONV = self.POSEIDON_PATH + '/Converter/build'
        self.POSEIDON = self.POSEIDON_PATH + '/build/Poseidon'

        self.PATMOS_PATH = self.AEGEAN_PATH + '/../patmos'
        self.CHISEL_PATH = self.PATMOS_PATH + '/chisel'
        self.BUILD_PATH = self.AEGEAN_PATH + '/build/' + projectname
        self.TMP_BUILD_PATH = self.BUILD_PATH + '/xml'

        ###################################################
        # Intermediate files
        self.GEN_PLAT = self.TMP_BUILD_PATH + '/plat.xml'
        self.GEN_COM = self.TMP_BUILD_PATH + '/com.xml'
        self.GEN_SCHED = self.TMP_BUILD_PATH + '/sched.xml'
        self.SED_FILE = self.BUILD_PATH + '/.sed'

        ###################################################
        # Final config files
        self.CSCHED = self.BUILD_PATH + '/init.h'
        self.NOCFile = self.BUILD_PATH + '/noc.vhd'
        self.AegeanFile = self.BUILD_PATH + '/aegean.vhd'
        self.TestFile = self.BUILD_PATH + '/aegean_testbench.vhd'
        self.ConfFile = self.BUILD_PATH + '/config.vhd'
        self.QUARTUS_FILE = self.BUILD_PATH + '/quartus/'+projectname+'_top.qsf'
