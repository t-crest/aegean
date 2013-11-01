#! /usr/bin/env python3


import sys
import string
from lxml import etree

class HWConfig(object):
    """docstring for HWConfig"""
    def __init__(self,aegean):
        self.platform = list(aegean)[0]

    def config(self):
        self.createHardware()

    def createHardware(self):
        print("Creating Hardware...",end="")
        et = etree.ElementTree(self.platform)
        et.write('test.xml')
        self.hardwareDone()

    def hardwareDone(self):
        print("Still To Be Done")
