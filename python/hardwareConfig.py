#! /usr/bin/env python3

class HWConfig(object):
    """docstring for HWConfig"""
    def __init__(self,aegean):
        self.platform = list(aegean)[0]

    def config(self):
        self.createHardware()

    def createHardware(self):
        print("Creating Hardware...",end="")
        self.hardwareDone()

    def hardwareDone(self):
        print("Done")
