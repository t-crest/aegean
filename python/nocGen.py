#import sys
#import string
import paths
import util
import nocCode
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


    """
    The generateNoC method writes an entity of the NoC according the the specification.
    """
    def generate(self):
        f = open(self.p.NOCFile, 'w')
        nocCode.writeNoCHeader(f)

# Instantiation of noc nodes and links
        nodes = self.getNodes()
        for k in range(0,len(nodes)):
            j, i = nodes[k].get('loc').strip('()').split(',')
            instancename = nodes[k].get('id') + '_' + nodes[k].get('IPTypeRef')
            #core_id = str(int(nodes[k].get("core_id"),16))
            nocCode.writeNodeInst(f,instancename,k,i,j)

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
                        nocCode.writeEast(f,i1,i2,j1,j2)
                    elif int(j1) < int(j2):
                        nocCode.writeWest(f,i1,i2,j1,j2)
                    else:
                        raise SystemExit(" error: Something is wrong!!!")

                if same_col:
                    if int(i1) > int(i2):
                        nocCode.writeSouth(f,i1,i2,j1,j2)
                    elif int(i1) < int(i2):
                        nocCode.writeNorth(f,i1,i2,j1,j2)
                    else:
                        raise SystemExit(" error: Something is wrong!!!")

        elif self.getTopType() == 'bitorus':
            nocCode.writeBitorus(f)
        elif self.getTopType() == 'mesh':
            nocCode.writeMesh(f)
        else:
            SystemExit(' error: xml validation error found in ' + __file__)

        nocCode.writeFooter(f)
        f.close()

