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

import util
from codeGen import testCode
from codeGen import topCode

class TestGen(object):
    """
    The TestGen class handles the generation of a testbench for the Aegean hardware platform
    """
    def __init__(self,p,platform):
        self.p = p
        self.platform = platform
        self.IPCores = util.findTag(self.platform,"IPCores")
        self.nodes = util.findTag(self.platform,"nodes")
        self.memory = util.findTag(self.platform,"memory")
        self.spys = dict({})


    def generate(self,top):
        test = testCode.getTest()

        for p in range(0,len(self.nodes)):
            node = self.nodes[p]
            label = node.get('id')
            IPTypeRef = node.get('IPTypeRef')
            for IPCore in list(self.IPCores):
                if IPCore.get('IPType') == IPTypeRef:
                    pat = util.findTag(IPCore,'patmos')
                    IOs = util.findTag(pat,'IOs')
                    for IO in list(IOs):
                        DevTypeRef = IO.get('DevTypeRef')
                        if DevTypeRef == 'Uart':
                            self.spys[label] = True
                            testCode.writeSignalSpySignals(test,label)
                            break
                        self.spys[label] = False
                    break

        sramName = self.memory.get('DevTypeRef')
        testCode.declareSignals(test,self.memory.get('DevTypeRef'))
        testCode.bindTop(top,sramName)
        test.arch.instComp(top,'top',True)

        for p in range(0,len(self.nodes)):
            node = self.nodes[p]
            IPTypeRef = node.get('IPTypeRef')
            BootApp = node.get('BootApp')
            if str(BootApp) != 'None':
                IPTypeRef = (IPTypeRef +'_'+BootApp).replace('-','_')
            label = node.get('id')
            if self.spys[label]:
                testCode.writeUartSpy(test,label,IPTypeRef)

        s = testCode.writeBaudIncBegin()

        s+= testCode.writeWait()
        for p in range(0,len(self.nodes)):
            node = self.nodes[p]
            IPTypeRef = node.get('IPTypeRef')
            BootApp = node.get('BootApp')
            if str(BootApp) != 'None':
                IPTypeRef = (IPTypeRef +'_'+BootApp).replace('-','_')
            label = node.get('id')
            if self.spys[label]:
                s+= testCode.writeUartForce(label,1,IPTypeRef)

        s+= testCode.writeWait()
        for p in range(0,len(self.nodes)):
            node = self.nodes[p]
            IPTypeRef = node.get('IPTypeRef')
            BootApp = node.get('BootApp')
            if str(BootApp) != 'None':
                IPTypeRef = (IPTypeRef +'_'+BootApp).replace('-','_')
            label = node.get('id')
            if self.spys[label]:
                s+= testCode.writeUartForce(label,0,IPTypeRef)

        s+= testCode.writeBaudIncEnd()
        test.arch.addToBody(s)

        testCode.writeSimMem(test,sramName,self.p.MAIN_MEM)

        test.writeComp(self.p.TestFile)
