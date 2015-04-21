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

from codeGen.Component import Component

def addMasterPort(comp,iFace,addrWidth,dataWidth=32):
    addPort(comp,'out','in',iFace,addrWidth,dataWidth)

def addSlavePort(comp,iFace,addrWidth,dataWidth=32):
    addPort(comp,'in','out',iFace,addrWidth,dataWidth)

def addPort(comp,mDirection,sDirection,iFace,addrWidth,dataWidth):
    if iFace == 'OcpBurst':
        comp.entity.addPort('io_ocp_M_Cmd',mDirection,'std_logic_vector',3)
        comp.entity.addPort('io_ocp_M_Addr',mDirection,'std_logic_vector',addrWidth)
        comp.entity.addPort('io_ocp_M_Data',mDirection,'std_logic_vector',dataWidth)
        comp.entity.addPort('io_ocp_M_DataValid',mDirection,'std_logic')
        comp.entity.addPort('io_ocp_M_DataByteEn',mDirection,'std_logic_vector',4)
        comp.entity.addPort('io_ocp_S_Resp',sDirection,'std_logic_vector',2)
        comp.entity.addPort('io_ocp_S_Data',sDirection,'std_logic_vector',dataWidth)
        comp.entity.addPort('io_ocp_S_CmdAccept',sDirection,'std_logic')
        comp.entity.addPort('io_ocp_S_DataAccept',sDirection,'std_logic')
    else:
        raise SystemError(__file__ +': Error: iface: " + iFace + " is not supported.')


def bindPort(comp,iFace,bindingMSignal,bindingSSignal):
    if iFace == 'OcpBurst':
        comp.entity.bindPort('io_ocp_M_Cmd',bindingMSignal+'.MCmd')
        comp.entity.bindPort('io_ocp_M_Addr',bindingMSignal+'.MAddr')
        comp.entity.bindPort('io_ocp_M_Data',bindingMSignal+'.MData')
        comp.entity.bindPort('io_ocp_M_DataValid',bindingMSignal+'.MDataValid')
        comp.entity.bindPort('io_ocp_M_DataByteEn',bindingMSignal+'.MDataByteEn')
        comp.entity.bindPort('io_ocp_S_Resp',bindingSSignal+'.SResp')
        comp.entity.bindPort('io_ocp_S_Data',bindingSSignal+'.SData')
        comp.entity.bindPort('io_ocp_S_CmdAccept',bindingSSignal+'.SCmdAccept')
        comp.entity.bindPort('io_ocp_S_DataAccept',bindingSSignal+'.SDataAccept')
    else:
        raise SystemError(__file__ +': Error: iface: " + iFace + " is not supported.')
