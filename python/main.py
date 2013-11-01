#! /usr/bin/env python3

import sys
from lxml import etree
from io import StringIO
from subprocess import call

from hardwareConfig import HWConfig
from softwareConfig import SWConfig


XMLSCHEME = "../xmlNotes/Aegean.xsd"

def parseXML(filename):
    tree = etree.parse(filename)
    xmlschema_doc = etree.parse(XMLSCHEME)
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
