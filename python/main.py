#! /usr/bin/env python3

import sys
import aegean
from lxml import etree
from io import StringIO

from hardwareConfig import HWConfig
from softwareConfig import SWConfig

def parseXML(filename):
    parser = etree.XMLParser(remove_comments=True)
    tree = etree.parse(filename, parser=parser)
    xmlschema_doc = etree.parse(aegean.XMLSCHEME)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    xmlschema.assertValid(tree)
    if xmlschema.validate(tree):
        return tree.getroot()


def createMakefile():
    pass

aegean = parseXML(sys.argv[1])

application = list(aegean)[1]

# Hardware config needs to be done before software config
hwc = HWConfig(aegean)
hwc.config()

swc = SWConfig(aegean)
swc.config()

createMakefile()




#for element in tree.iter():
#   if (element.tag is etree.Comment) or (not element.text) or (not element.text.strip()):
#       print(element.tag)
#   else:
#       print("%s - %s" % (element.tag, element.text))

#call(["ls","-l"])
