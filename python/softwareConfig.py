#! /usr/bin/env python3

class SWConfig(object):
    """docstring for SWConfig"""
    def __init__(self, aegean):
        self.application = list(aegean)[1]

    def config(self):
        self.createSched()
        self.createScript()

    def createSched(self):
        print("Creating schedule")

    def createScript(self):
        print("Creating compiler scripts")

