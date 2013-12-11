#import sys
#import string
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

    def config(self):
        N = self.platform.get('width')
        M = self.platform.get('height')
        NODES = len(self.getNodes())
        f = open(self.p.ConfFile, 'w')
        nocCode.writeConfig(f,N,M,NODES)

    def getNocNode(self):
        nocNode = Component('noc_node')
        nocNode.entity.addPort('p_clk')
        nocNode.entity.addPort('n_clk')
        nocNode.entity.addPort('reset')
        nocNode.entity.addPort('proc_m','in','ocp_io_m')
        nocNode.entity.addPort('proc_s','out','ocp_io_s')
        nocNode.entity.addPort('spm_m','out','spm_master')
        nocNode.entity.addPort('spm_s','in','spm_slave')
        nocNode.entity.addPort('inNorth','in','link_t')
        nocNode.entity.addPort('inSouth','in','link_t')
        nocNode.entity.addPort('inEast','in','link_t')
        nocNode.entity.addPort('inWest','in','link_t')
        nocNode.entity.addPort('outNorth','out','link_t')
        nocNode.entity.addPort('outSouth','out','link_t')
        nocNode.entity.addPort('outEast','out','link_t')
        nocNode.entity.addPort('outWest','out','link_t')
        return nocNode

    def bindNocNode(self,nocNode,k,i,j):
        nocNode.entity.bindPort('p_clk','clk')
        nocNode.entity.bindPort('n_clk','clk')
        nocNode.entity.bindPort('reset','reset')
        nocNode.entity.bindPort('proc_m','ocp_io_ms('+str(k)+')')
        nocNode.entity.bindPort('proc_s','ocp_io_ss('+str(k)+')')
        nocNode.entity.bindPort('spm_m','spm_ports_m('+str(k)+')')
        nocNode.entity.bindPort('spm_s','spm_ports_s('+str(k)+')')
        nocNode.entity.bindPort('inNorth','north_in('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('inSouth','south_in('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('inEast','east_in('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('inWest','west_in('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('outNorth','north_out('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('outSouth','south_out('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('outEast','east_out('+str(i)+')('+str(j)+')')
        nocNode.entity.bindPort('outWest','west_out('+str(i)+')('+str(j)+')')
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


        noc.arch.declSignal('north_in, east_in, south_in, west_in','link_m')
        noc.arch.declSignal('north_out, east_out, south_out, west_out','link_m')

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
                    raise SystemExit(' error: Link in specification is illegal. ' + str(etree.tostring(links[k])))

                if (abs(int(j1)-int(j2)) > 1) or (abs(int(i1)-int(i2)) > 1):
                    raise SystemExit(' error: Link is trying to connect cores too far appart. ' + str(etree.tostring(links[k])))


                if same_row:
                    if int(j1) > int(j2):
                        nocCode.writeEast(noc,i1,i2,j1,j2)
                    elif int(j1) < int(j2):
                        nocCode.writeWest(noc,i1,i2,j1,j2)
                    else:
                        raise SystemExit(" error: Something is wrong!!!")

                if same_col:
                    if int(i1) > int(i2):
                        nocCode.writeSouth(noc,i1,i2,j1,j2)
                    elif int(i1) < int(i2):
                        nocCode.writeNorth(noc,i1,i2,j1,j2)
                    else:
                        raise SystemExit(" error: Something is wrong!!!")

        elif self.getTopType() == 'bitorus':
            nocCode.writeBitorus(noc)
        elif self.getTopType() == 'mesh':
            nocCode.writeMesh(noc)
        else:
            SystemExit(' error: xml validation error found in ' + __file__)

        noc.writeComp(self.p.NOCFile)

        return noc

