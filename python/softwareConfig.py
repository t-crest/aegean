#! /usr/bin/env python3

import sys
import string
import paths
import util
from lxml import etree
import subprocess

#def findTag(x,s):
#    tags = list(x)
#    for i in range(0,len(tags)):
#        if tags[i].tag == s:
#            return tags[i]

class SWConfig(object):
    """
    The SWConfig class handles the configuration steps
    for configuring the software of the Aegean platform
    """
    def __init__(self,p,aegean):
        self.application = util.findTag(aegean,"application")
        self.p = p

    def config(self,routerDepth,schedType='Aegean-c'):
#        tags = list(self.application)
#        for i in range(0,len(tags)):
#            if tags[i].tag == 'communication':
#                communication = tags[i]
#                break
        communication = util.findTag(self.application,"communication")
        et = etree.ElementTree(communication)
        et.write(self.p.GEN_COM)
        self.createSched(routerDepth,schedType)
        self.createScript()

    def createSched(self,routerDepth,schedType):
        print('Creating schedule')
        Poseidon = [self.p.POSEIDON]
        Poseidon+= ['-p',self.p.GEN_PLAT]  # Platform specification
        Poseidon+= ['-c',self.p.GEN_COM]   # Communication specification
        Poseidon+= ['-s',self.p.GEN_SCHED] # XML Schedule output
        Poseidon+= ['-m','GREEDY']         # Optimization algorithm
        Poseidon+= ['-d']                  # Draw the topology
        subprocess.call(Poseidon)
        print('Converting schedule')
        Converter = [self.p.POSEIDON_CONV]
        Converter+= [self.p.GEN_SCHED,self.p.CSCHED,schedType,routerDepth]
        subprocess.call(Converter)
        print('Copying schedule')
        Cp = ['cp']              # Copy
        Cp+= [self.p.CSCHED]     # Source
        Cp+= [self.p.PATMOS_PATH + '/c/init.h'] # Destination
        subprocess.call(Cp)

    def createScript(self):
        print('Creating compiler scripts')



