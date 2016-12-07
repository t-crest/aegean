import sys
import string
import paths
import util
from lxml import etree
import subprocess

class NoCSchedConfig(object):
    """
    The NoCSchedConfig class handles the configuration steps
    for configuring the NoC TDM Schedule
    """
    def __init__(self,p,nocsched):
        self.application = util.findTag(nocsched,"application")
        self.p = p

    def config(self):
        configurations = list(util.findTag(self.application,"configurations"))
        for i in range(0,len(configurations)):
            #communication = util.findTag(configurations,"communication")
            et = etree.ElementTree(configurations[i])
            et.write(self.p.GEN_COM+str(i)+'.xml')
        self.createSched(len(configurations))
        self.createScript()

    def createSched(self,numConfig):
        print('Creating schedule')
        for i in range(0,numConfig):
            Poseidon = [self.p.POSEIDON]
            Poseidon+= ['-p',self.p.GEN_PLAT]  # Platform specification
            Poseidon+= ['-c',self.p.GEN_COM+str(i)+'.xml']   # Communication specification
            Poseidon+= ['-s',self.p.GEN_SCHED+str(i)+'.xml'] # XML Schedule output
            Poseidon+= ['-m','GREEDY']         # Optimization algorithm
            Poseidon+= ['-v',"2"]              # Argo version
            Poseidon+= ['-d']                  # Draw the topology
            ret = subprocess.call(Poseidon)
            if ret != 0:
                raise SystemExit(__file__ +': Error: poseidon: ' + str(ret))

        print('Converting schedule')
        Converter = [self.p.POSEIDON_CONV]
        for i in range(0,numConfig):
            Converter+= [self.p.GEN_SCHED+str(i)+'.xml']

        Converter+= ['-o',self.p.CSCHED]
        ret = subprocess.call(Converter)
        if ret != 0:
            raise SystemExit(__file__ +': Error: poseidon-conv: ' + str(ret))
        print('Copying schedule')
        Cp = ['cp']              # Copy
        Cp+= [self.p.CSCHED]     # Source
        Cp+= [self.p.PATMOS_PATH + '/c/cmp/nocinit.c'] # Destination
        ret = subprocess.call(Cp)
        if ret != 0:
            raise SystemExit(__file__ +': Error: cp: ' + str(ret))

    def createScript(self):
        print('Creation of compiler scripts is NOT YET IMPLEMENTED')
