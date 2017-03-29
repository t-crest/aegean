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
import math
import traceback

def writeConfig(fileName,burstAddrWidth):
    f = open(fileName, 'w')
    f.write('''library ieee;
use ieee.std_logic_1164.all;

package ocp_config is

    constant BURST_ADDR_WIDTH : integer := '''+str(burstAddrWidth)+''';

end package ; -- ocp_config
''')
    f.close()


def getAegean():
    aegean = Component('aegean')
    aegean.addPackage('ieee','std_logic_1164')
    aegean.addPackage('ieee','numeric_std')
    aegean.addPackage('work','config_types')
    aegean.addPackage('work','config')
    aegean.addPackage('work','ocp')
    aegean.addPackage('work','argo_types')
    aegean.addPackage('work','noc_interface')

    aegean.entity.addPort('clk')
    aegean.entity.addPort('reset')
    aegean.entity.addPort('sram_burst_m','out','ocp_burst_m')
    aegean.entity.addPort('sram_burst_s','in','ocp_burst_s')

    return aegean


def getArbiter(numPorts,ocpBurstAddrWidth):
    arbiter = Component('TdmArbiterWrapper')
    #arbiter = Component('Arbiter')
    arbiter.entity.addPort('clk')
    arbiter.entity.addPort('reset')
    arbiter.entity.addPort('io_slave_M_Cmd','out','std_logic_vector',3)
    arbiter.entity.addPort('io_slave_M_Addr','out','std_logic_vector',ocpBurstAddrWidth)
    arbiter.entity.addPort('io_slave_M_Data','out','std_logic_vector',32)
    arbiter.entity.addPort('io_slave_M_DataValid','out','std_logic')
    arbiter.entity.addPort('io_slave_M_DataByteEn','out','std_logic_vector',4)
    arbiter.entity.addPort('io_slave_S_Resp','in','std_logic_vector',2)
    arbiter.entity.addPort('io_slave_S_Data','in','std_logic_vector',32)
    arbiter.entity.addPort('io_slave_S_CmdAccept','in','std_logic')
    arbiter.entity.addPort('io_slave_S_DataAccept','in','std_logic')
    for i in range(0,numPorts):
        arbiter.entity.addPort('io_master_'+str(i)+'_M_Cmd','in','std_logic_vector',3)
        arbiter.entity.addPort('io_master_'+str(i)+'_M_Addr','in','std_logic_vector',ocpBurstAddrWidth)
        arbiter.entity.addPort('io_master_'+str(i)+'_M_Data','in','std_logic_vector',32)
        arbiter.entity.addPort('io_master_'+str(i)+'_M_DataValid','in','std_logic')
        arbiter.entity.addPort('io_master_'+str(i)+'_M_DataByteEn','in','std_logic_vector',4)
        arbiter.entity.addPort('io_master_'+str(i)+'_S_Resp','out','std_logic_vector',2)
        arbiter.entity.addPort('io_master_'+str(i)+'_S_Data','out','std_logic_vector',32)
        arbiter.entity.addPort('io_master_'+str(i)+'_S_CmdAccept','out','std_logic')
        arbiter.entity.addPort('io_master_'+str(i)+'_S_DataAccept','out','std_logic')
    return arbiter

def getPatmos(IPType,ocpBurstAddrWidth=21):
    patmos = Component(IPType+'PatmosCore')
    patmos.entity.addPort('clk')
    patmos.entity.addPort('reset')

    patmos.entity.addPort('io_superMode','out', 'std_logic')
    patmos.entity.addPort('io_comConf_M_Cmd','out', 'std_logic_vector',3)
    patmos.entity.addPort('io_comConf_M_Addr','out', 'std_logic_vector',32)
    patmos.entity.addPort('io_comConf_M_Data','out', 'std_logic_vector',32)
    patmos.entity.addPort('io_comConf_M_ByteEn','out', 'std_logic_vector',4)
    patmos.entity.addPort('io_comConf_M_RespAccept','out', 'std_logic')
    patmos.entity.addPort('io_comConf_S_Resp','in', 'std_logic_vector',2)
    patmos.entity.addPort('io_comConf_S_Data','in', 'std_logic_vector',32)
    patmos.entity.addPort('io_comConf_S_CmdAccept','in', 'std_logic')
    patmos.entity.addPort('io_comConf_S_Reset_n','in', 'std_logic')
    patmos.entity.addPort('io_comConf_S_Flag','in', 'std_logic_vector',2)
    patmos.entity.addPort('io_comSpm_M_Cmd','out', 'std_logic_vector',3)
    patmos.entity.addPort('io_comSpm_M_Addr','out', 'std_logic_vector',32)
    patmos.entity.addPort('io_comSpm_M_Data','out', 'std_logic_vector',32)
    patmos.entity.addPort('io_comSpm_M_ByteEn','out', 'std_logic_vector',4)
    patmos.entity.addPort('io_comSpm_S_Resp','in', 'std_logic_vector',2)
    patmos.entity.addPort('io_comSpm_S_Data','in', 'std_logic_vector',32)
    patmos.entity.addPort('io_cpuInfoPins_id','in', 'std_logic_vector',32)
    patmos.entity.addPort('io_cpuInfoPins_cnt','in', 'std_logic_vector',32)
    patmos.entity.addPort('io_memPort_M_Cmd','out', 'std_logic_vector',3)
    patmos.entity.addPort('io_memPort_M_Addr','out', 'std_logic_vector',ocpBurstAddrWidth)
    patmos.entity.addPort('io_memPort_M_Data','out', 'std_logic_vector',32)
    patmos.entity.addPort('io_memPort_M_DataValid','out', 'std_logic')
    patmos.entity.addPort('io_memPort_M_DataByteEn','out', 'std_logic_vector',4)
    patmos.entity.addPort('io_memPort_S_Resp','in', 'std_logic_vector',2)
    patmos.entity.addPort('io_memPort_S_Data','in', 'std_logic_vector',32)
    patmos.entity.addPort('io_memPort_S_CmdAccept','in', 'std_logic')
    patmos.entity.addPort('io_memPort_S_DataAccept','in', 'std_logic')

    return patmos


def declareSignals(aegean,numNodes):
    aegean.arch.declSignal('ocp_io_ms','ocp_io_m_a')
    aegean.arch.declSignal('ocp_io_ss','ocp_io_s_a')
    aegean.arch.declSignal('ocp_core_ms','ocp_core_m_a')
    aegean.arch.declSignal('ocp_core_ss','ocp_core_s_a')
    aegean.arch.declSignal('ocp_burst_ms','ocp_burst_m_a')
    aegean.arch.declSignal('ocp_burst_ss','ocp_burst_s_a')
    aegean.arch.declSignal('spm_ms','mem_if_masters')
    aegean.arch.declSignal('spm_ss','mem_if_slaves')
    aegean.arch.declSignal('supervisor','std_logic_vector',numNodes)
    aegean.arch.declSignal('irq','std_logic_vector',numNodes*2)

def setSPMSize(aegean,sizes):
    aegean.arch.decl('''
    type size_array is array(0 to NODES-1) of integer;
''')
    #name, constType, width, value
    s = ', '.join(str(math.ceil(math.log(size,2))) for size in sizes)
    aegean.arch.declConstant('SPM_WIDTH', 'size_array', 1, '('+ s +')')


def bindPatmos(patmos,cnt,p):

    patmos.entity.bindPort('clk','clk')
    patmos.entity.bindPort('reset','reset')
    patmos.entity.bindPort('io_superMode','supervisor('+str(p)+')')
    patmos.entity.bindPort('io_comConf_M_Cmd','ocp_io_ms('+str(p)+').MCmd')
    patmos.entity.bindPort('io_comConf_M_Addr','ocp_io_ms('+str(p)+').MAddr')
    patmos.entity.bindPort('io_comConf_M_Data','ocp_io_ms('+str(p)+').MData')
    patmos.entity.bindPort('io_comConf_M_ByteEn','ocp_io_ms('+str(p)+').MByteEn')
    patmos.entity.bindPort('io_comConf_M_RespAccept','ocp_io_ms('+str(p)+').MRespAccept')
    patmos.entity.bindPort('io_comConf_S_Resp','ocp_io_ss('+str(p)+').SResp')
    patmos.entity.bindPort('io_comConf_S_Data','ocp_io_ss('+str(p)+').SData')
    patmos.entity.bindPort('io_comConf_S_CmdAccept','ocp_io_ss('+str(p)+').SCmdAccept')
    patmos.entity.bindPort('io_comConf_S_Flag', 'irq('+str((p*2)+1)+' downto '+str(p*2)+')')
    patmos.entity.bindPort('io_comSpm_M_Cmd','ocp_core_ms('+str(p)+').MCmd')
    patmos.entity.bindPort('io_comSpm_M_Addr','ocp_core_ms('+str(p)+').MAddr')
    patmos.entity.bindPort('io_comSpm_M_Data','ocp_core_ms('+str(p)+').MData')
    patmos.entity.bindPort('io_comSpm_M_ByteEn','ocp_core_ms('+str(p)+').MByteEn')
    patmos.entity.bindPort('io_comSpm_S_Resp','ocp_core_ss('+str(p)+').SResp')
    patmos.entity.bindPort('io_comSpm_S_Data','ocp_core_ss('+str(p)+').SData')
    patmos.entity.bindPort('io_cpuInfoPins_id','std_logic_vector(to_unsigned('+str(p)+',32))')
    patmos.entity.bindPort('io_cpuInfoPins_cnt','std_logic_vector(to_unsigned('+str(cnt)+',32))')
    patmos.entity.bindPort('io_memPort_M_Cmd','ocp_burst_ms('+str(p)+').MCmd')
    patmos.entity.bindPort('io_memPort_M_Addr','ocp_burst_ms('+str(p)+').MAddr')
    patmos.entity.bindPort('io_memPort_M_Data','ocp_burst_ms('+str(p)+').MData')
    patmos.entity.bindPort('io_memPort_M_DataValid','ocp_burst_ms('+str(p)+').MDataValid')
    patmos.entity.bindPort('io_memPort_M_DataByteEn','ocp_burst_ms('+str(p)+').MDataByteEn')
    patmos.entity.bindPort('io_memPort_S_Resp','ocp_burst_ss('+str(p)+').SResp')
    patmos.entity.bindPort('io_memPort_S_Data','ocp_burst_ss('+str(p)+').SData')
    patmos.entity.bindPort('io_memPort_S_CmdAccept','ocp_burst_ss('+str(p)+').SCmdAccept')
    patmos.entity.bindPort('io_memPort_S_DataAccept','ocp_burst_ss('+str(p)+').SDataAccept')


def bindNoc(noc):
    noc.entity.bindPort('clk','clk')
    noc.entity.bindPort('reset','reset')
    noc.entity.bindPort('supervisor','supervisor')
    noc.entity.bindPort('ocp_io_ms','ocp_io_ms')
    noc.entity.bindPort('ocp_io_ss','ocp_io_ss')
    noc.entity.bindPort('spm_ports_m','spm_ms')
    noc.entity.bindPort('spm_ports_s','spm_ss')
    noc.entity.bindPort('irq','irq')

def addSPM():
    return '''
    spms : for i in 0 to NODES-1 generate
        spm : entity work.com_spm
        generic map(
            SPM_IDX_SIZE => SPM_WIDTH(i)
            )
        port map(
            p_clk => clk,
            n_clk => clk,
            reset => reset,
            ocp_core_m => ocp_core_ms(i),
            ocp_core_s => ocp_core_ss(i),
            spm_m => spm_ms(i),
            spm_s => spm_ss(i)
            );
    end generate ; -- spms
'''

def bindArbiter(arbiter,numPorts):
    arbiter.entity.bindPort('clk','clk')
    arbiter.entity.bindPort('reset','reset')
    arbiter.entity.bindPort('io_slave_M_Cmd','sram_burst_m.MCmd')
    arbiter.entity.bindPort('io_slave_M_Addr','sram_burst_m.MAddr')
    arbiter.entity.bindPort('io_slave_M_Data','sram_burst_m.MData')
    arbiter.entity.bindPort('io_slave_M_DataValid','sram_burst_m.MDataValid')
    arbiter.entity.bindPort('io_slave_M_DataByteEn','sram_burst_m.MDataByteEn')
    arbiter.entity.bindPort('io_slave_S_Resp','sram_burst_s.SResp')
    arbiter.entity.bindPort('io_slave_S_Data','sram_burst_s.SData')
    arbiter.entity.bindPort('io_slave_S_CmdAccept','sram_burst_s.SCmdAccept')
    arbiter.entity.bindPort('io_slave_S_DataAccept','sram_burst_s.SDataAccept')

    for i in range(0,numPorts):
        arbiter.entity.bindPort('io_master_'+str(i)+'_M_Cmd       ','ocp_burst_ms('+str(i)+').MCmd')
        arbiter.entity.bindPort('io_master_'+str(i)+'_M_Addr      ','ocp_burst_ms('+str(i)+').MAddr')
        arbiter.entity.bindPort('io_master_'+str(i)+'_M_Data      ','ocp_burst_ms('+str(i)+').MData')
        arbiter.entity.bindPort('io_master_'+str(i)+'_M_DataValid ','ocp_burst_ms('+str(i)+').MDataValid')
        arbiter.entity.bindPort('io_master_'+str(i)+'_M_DataByteEn','ocp_burst_ms('+str(i)+').MDataByteEn')
        arbiter.entity.bindPort('io_master_'+str(i)+'_S_Resp      ','ocp_burst_ss('+str(i)+').SResp')
        arbiter.entity.bindPort('io_master_'+str(i)+'_S_Data      ','ocp_burst_ss('+str(i)+').SData')
        arbiter.entity.bindPort('io_master_'+str(i)+'_S_CmdAccept ','ocp_burst_ss('+str(i)+').SCmdAccept')
        arbiter.entity.bindPort('io_master_'+str(i)+'_S_DataAccept','ocp_burst_ss('+str(i)+').SDataAccept')
