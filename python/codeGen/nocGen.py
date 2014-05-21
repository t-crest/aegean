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

import paths
import util
from codeGen import nocCode
from codeGen.Component import Component
from lxml import etree

class NoCGen(object):
    """docstring for HWGen"""
    def __init__(self,p,platform):
        self.platform = platform
        self.p = p

    def getLinks(self):
        return list(util.findTag(self.platform,"topology"))

    def getNodes(self):
        return list(util.findTag(self.platform,"nodes"))

    def getTopType(self):
        return util.findTag(self.platform,"topology").get('topoType')

    def getRouterType(self):
        return util.findTag(self.platform,"topology").get('routerType')

    def config(self):
        N = self.platform.get('width')
        M = self.platform.get('height')
        NODES = len(self.getNodes())
        f = open(self.p.ConfFile, 'w')
        RT = self.getRouterType()
        nocCode.writeConfig(f,N,M,NODES,RT.upper())

    def getNocNode(self):
        nocNode = Component('noc_node')
        nocNode.entity.addPort('p_clk')
        nocNode.entity.addPort('n_clk')
        nocNode.entity.addPort('reset')
        nocNode.entity.addPort('proc_m','in','ocp_io_m')
        nocNode.entity.addPort('proc_s','out','ocp_io_s')
        nocNode.entity.addPort('spm_m','out','spm_master')
        nocNode.entity.addPort('spm_s','in','spm_slave')

        nocNode.entity.addPort('north_in_f','in','channel_forward')
        nocNode.entity.addPort('north_in_b','out','channel_backward')
        nocNode.entity.addPort('south_in_f','in','channel_forward')
        nocNode.entity.addPort('south_in_b','out','channel_backward')
        nocNode.entity.addPort('east_in_f','in','channel_forward')
        nocNode.entity.addPort('east_in_b','out','channel_backward')
        nocNode.entity.addPort('west_in_f','in','channel_forward')
        nocNode.entity.addPort('west_in_b','out','channel_backward')
        nocNode.entity.addPort('north_out_f','out','channel_forward')
        nocNode.entity.addPort('north_out_b','in','channel_backward')
        nocNode.entity.addPort('south_out_f','out','channel_forward')
        nocNode.entity.addPort('south_out_b','in','channel_backward')
        nocNode.entity.addPort('east_out_f','out','channel_forward')
        nocNode.entity.addPort('east_out_b','in','channel_backward')
        nocNode.entity.addPort('west_out_f','out','channel_forward')
        nocNode.entity.addPort('west_out_b','in','channel_backward')

        return nocNode

    def bindNocNode(self,nocNode,k,i,j):
        nocNode.entity.bindPort('p_clk','clk')
        nocNode.entity.bindPort('n_clk','clk')
        nocNode.entity.bindPort('reset','reset')
        nocNode.entity.bindPort('proc_m','ocp_io_ms('+str(k)+')')
        nocNode.entity.bindPort('proc_s','ocp_io_ss('+str(k)+')')
        nocNode.entity.bindPort('spm_m','spm_ports_m('+str(k)+')')
        nocNode.entity.bindPort('spm_s','spm_ports_s('+str(k)+')')

        nocNode.entity.bindPort('north_in_f','north_in_f('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('north_in_b','north_in_b('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('south_in_f','south_in_f('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('south_in_b','south_in_b('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('east_in_f','east_in_f('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('east_in_b','east_in_b('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('west_in_f','west_in_f('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('west_in_b','west_in_b('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('north_out_f','north_out_f('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('north_out_b','north_out_b('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('south_out_f','south_out_f('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('south_out_b','south_out_b('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('east_out_f','east_out_f('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('east_out_b','east_out_b('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('west_out_f','west_out_f('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('west_out_b','west_out_b('+str(i)+')('+str(j)+')')

        return nocNode


    """
    The generateNoC method writes an entity of the NoC according the the specification.
    """
    def generate(self):
        # Instantiation of noc nodes and links
        nodes = self.getNodes()

        noc = Component('noc')
        noc.addPackage('ieee','std_logic_1164')
        noc.addPackage('ieee','std_logic_unsigned')
        noc.addPackage('ieee','numeric_std')
        noc.addPackage('work','config_types')
        noc.addPackage('work','config')
        noc.addPackage('work','ocp')
        noc.addPackage('work','noc_defs')
        noc.addPackage('work','noc_interface')

        noc.entity.addPort('clk','in','std_logic',1)
        noc.entity.addPort('reset','in','std_logic',1)
        noc.entity.addPort('ocp_io_ms','in','ocp_io_m_a',1)
        noc.entity.addPort('ocp_io_ss','out','ocp_io_s_a',1)
        noc.entity.addPort('spm_ports_m','out','spm_masters',1)
        noc.entity.addPort('spm_ports_s','in','spm_slaves',1)


        noc.arch.declSignal('north_in_f, east_in_f, south_in_f, west_in_f','link_m_f')
        noc.arch.declSignal('north_in_b, east_in_b, south_in_b, west_in_b','link_m_b')
        noc.arch.declSignal('north_out_f, east_out_f, south_out_f, west_out_f','link_m_f')
        noc.arch.declSignal('north_out_b, east_out_b, south_out_b, west_out_b','link_m_b')

        for k in range(0,len(nodes)):
            j, i = nodes[k].get('loc').strip('()').split(',')
            instancename = nodes[k].get('id') + '_' + nodes[k].get('IPTypeRef')
            nocNode = self.getNocNode()
            self.bindNocNode(nocNode,k,i,j)
            noc.arch.instComp(nocNode,instancename)

        noc.arch.declComp(nocNode)

        if self.getTopType() == 'custom':
            links = self.getLinks()
            for k in range(0,len(links)):
                j1, i1 = links[k].get('source').strip('()').split(',')
                j2, i2 = links[k].get('sink').strip('()').split(',')
                same_col = (j1 == j2)
                same_row = (i1 == i2)
                #if not (same_row != same_col):
                if not ((same_row or same_col) and (same_row != same_col)):
                    raise SystemExit(__file__ +': Error: Link in specification is illegal. ' + str(etree.tostring(links[k])))

                if (abs(int(j1)-int(j2)) > 1) or (abs(int(i1)-int(i2)) > 1):
                    raise SystemExit(__file__ +': Error: Link is trying to connect cores too far appart. ' + str(etree.tostring(links[k])))


                if same_row:
                    if int(j1) > int(j2):
                        nocCode.writeEast(noc,i1,i2,j1,j2)
                    elif int(j1) < int(j2):
                        nocCode.writeWest(noc,i1,i2,j1,j2)
                    else:
                        raise SystemExit(__file__ +': Error: Something is wrong!!!')

                if same_col:
                    if int(i1) > int(i2):
                        nocCode.writeSouth(noc,i1,i2,j1,j2)
                    elif int(i1) < int(i2):
                        nocCode.writeNorth(noc,i1,i2,j1,j2)
                    else:
                        raise SystemExit(__file__ +': Error: Something is wrong!!!')

        elif self.getTopType() == 'bitorus':
            nocCode.writeBitorus(noc)
        elif self.getTopType() == 'mesh':
            nocCode.writeMesh(noc)
        else:
            SystemExit(__file__ +': Error: xml validation error')

        noc.writeComp(self.p.NOCFile)

        routerType = self.getRouterType()
        argo_src = open(self.p.BUILD_PATH+'/.argo_src','w')
        argo_src.write(self.p.ARGO_PATH+'/src/config_types.vhd ')
        argo_src.write(self.p.BUILD_PATH + '/ocp_config.vhd ')
        argo_src.write(self.p.ARGO_PATH+'/src/ocp/ocp.vhd ')
        argo_src.write(self.p.ARGO_PATH+'/src/util/math_util.vhd ')
        argo_src.write(self.p.ARGO_PATH+'/src/noc_defs.vhd ')
        argo_src.write(self.p.ARGO_PATH+'/src/noc_interface.vhd ')
        argo_src.write(self.p.ARGO_PATH+'/src/mem/bram.vhd ')
        argo_src.write(self.p.ARGO_PATH+'/src/mem/bram_tdp.vhd ')
        argo_src.write(self.p.ARGO_PATH+'/src/ni/counter.vhd ')
        argo_src.write(self.p.ARGO_PATH+'/src/ni/dma.vhd ')
        argo_src.write(self.p.ARGO_PATH+'/src/mem/com_spm.vhd ')
        argo_src.write(self.p.ARGO_PATH+'/src/ni/nAdapter.vhd ')

        if routerType == 'sync':
            argo_src.write(self.p.ARGO_PATH+'/src/routers/synchronous/xbar.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/synchronous/hpu.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/synchronous/router.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/noc/synchronous/noc_node.vhd ')
            #raise SystemExit(__file__ +': Error: routerType: ' + routerType + ' is not yet implemented.')
        elif routerType == 'async':
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/delays.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/rtl/matched_delay.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/rtl/sr_latch.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/rtl/c_gate_generic.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/crossbar.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/latch_controller.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/channel_latch.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/hpu_latch.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/hpu_comb.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/crossbar_stage.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/hpu.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/router.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/fifo.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/noc/asynchronous/noc_node.vhd ')
        elif routerType == 'async_fpga':
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/delays.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/fpga/matched_delay.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/fpga/AS_C2.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/fpga/c_gate_generic.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/crossbar.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/latch_controller.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/channel_latch.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/hpu_latch.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/hpu_comb.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/crossbar_stage.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/hpu.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/router.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/routers/asynchronous/fifo.vhd ')
            argo_src.write(self.p.ARGO_PATH+'/src/noc/asynchronous/noc_node.vhd ')

        argo_src.close()
        return noc

