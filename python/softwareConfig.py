#! /usr/bin/env python3

import sys
import string
import paths
from lxml import etree
import subprocess

class SWConfig(object):
    """
    The SWConfig class handles the configuration steps
    for configuring the software of the Aegean platform
    """
    def __init__(self, aegean):
        self.application = list(aegean)[1]

    def config(self):
        tags = list(self.application)
        for i in range(0,len(tags)):
            if tags[i].tag == "communication":
                communication = tags[i]
                break

        et = etree.ElementTree(communication)
        et.write(paths.GEN_COM)
        self.createSched()
        self.createScript()

    def createSched(self):
        print("Creating schedule")
        Poseidon = [paths.POSEIDON]
        Poseidon+= ["-p",paths.GEN_PLAT]  # Platform specification
        Poseidon+= ["-c",paths.GEN_COM]   # Communication specification
        Poseidon+= ["-s",paths.GEN_SCHED] # XML Schedule output
        Poseidon+= ["-m","GREEDY"]         # Optimization algorithm
        Poseidon+= ["-d"]                  # Draw the topology
        subprocess.call(Poseidon)
        print("Converting schedule")
        Converter = ["java"]
        Converter+= ["-cp",paths.POSEIDON_CONV,"converter.Converter"]
        Converter+= [paths.GEN_SCHED,paths.CSCHED,"Aegean-c"]
        subprocess.call(Converter)
        print("Copying schedule")
        Cp = ["cp"]              # Copy
        Cp+= [paths.CSCHED]     # Source
        Cp+= [paths.PATMOS_PATH + "/c/init.h"] # Destination
        subprocess.call(Cp)

    def createScript(self):
        print("Creating compiler scripts")

