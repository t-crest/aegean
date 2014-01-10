#! /usr/bin/env python3
#
# Copyright Technical University of Denmark. All rights reserved.
# This file is part of the T-CREST project.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN
# NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of the copyright holder.
#
###############################################################################
# Authors:
#    Rasmus Bo Soerensen (rasmus@rbscloud.dk)
#
###############################################################################

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



