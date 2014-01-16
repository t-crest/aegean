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

from codeGen.nocGen import NoCGen
from codeGen.aegeanGen import AegeanGen
from codeGen.testGen import TestGen
from lxml import etree
import paths
import subprocess
import util

class HWConfig(object):
    """
    The HWConfig class handles the hardware configuration of the aegean platform
    """
    def __init__(self,p,aegean):
        self.p = p
        self.platform = util.findTag(aegean,'platform')
        topology = util.findTag(self.platform,'topology')
        self.routerDepth = topology.get('routerDepth')
        self.IPCores = util.findTag(self.platform,'IPCores')
        et = etree.ElementTree(self.platform)
        et.write(self.p.GEN_PLAT)

    def config(self):
        nocComp = NoCGen(self.p,self.platform)
        nocComp.config()
        noc = nocComp.generate()
        aegeanGen = AegeanGen(self.p,self.platform)
        aegean = aegeanGen.generate(noc)
        top = aegeanGen.generateTopLevel(aegean)
        testGen = TestGen(self.p,self.platform)
        test = testGen.generate(top)

#        VCOM = ['vcom','-quiet',self.p.NOCFile]
#        VCOM+= [self.p.AegeanFile]
#        VCOM+= [self.p.TopFile]
#        VCOM+= [self.p.TestFile]
#        VCOM+= [self.p.ConfFile]
#        VCOM+= ['-work',self.p.BUILD_PATH+'/work']
#        subprocess.call(VCOM)

