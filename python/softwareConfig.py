#! /usr/bin/env python3

import sys
import string
import aegean
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
        et.write(aegean.GEN_COM)
        self.createSched()
        self.createScript()

    def createSched(self):
        print("Creating schedule")
        Poseidon = [aegean.POSEIDON]
        Poseidon+= ["-p",aegean.GEN_PLAT]
        Poseidon+= ["-c",aegean.GEN_COM]
        Poseidon+= ["-s",aegean.GEN_SCHED]
        Poseidon+= ["-m","GREEDY"]
        Poseidon+= ["-d"]
        subprocess.call(Poseidon)

    def createScript(self):
        print("Creating compiler scripts")

