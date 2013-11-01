#! /usr/bin/env python3

import sys
import string
from lxml import etree
from subprocess import call

class SWConfig(object):
    """docstring for SWConfig"""
    def __init__(self, aegean):
        self.application = list(aegean)[1]

    def config(self):
        tags = list(self.application)
        for i in range(0,len(tags)):
            if tags[i].tag == "communication":
                communication = tags[i]
                break

        et = etree.ElementTree(communication)
        et.write('com.xml')
        self.createSched()
        self.createScript()

    def createSched(self):
        print("Creating schedule")
        Poseidon = ["../../poseidon/build/Poseidon"]
        Poseidon+= ["-p","./test.xml"]
        Poseidon+= ["-c","./com.xml"]
        Poseidon+= ["-s","./out.xml"]
        Poseidon+= ["-m","GREEDY"]
        call(Poseidon)

    def createScript(self):
        print("Creating compiler scripts")

