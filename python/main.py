#! /usr/bin/env python3

import sys
import paths
from lxml import etree
from io import StringIO

from hardwareConfig import HWConfig
from softwareConfig import SWConfig

def parseXML(filename):
    parser = etree.XMLParser(remove_comments=True)
    tree = etree.parse(filename, parser=parser)
    xmlschema_doc = etree.parse(paths.XMLSCHEME)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    xmlschema.assertValid(tree)
    if xmlschema.validate(tree):
        return tree.getroot()


aegean = parseXML(sys.argv[1])

application = list(aegean)[1]

hwc = HWConfig(aegean)
swc = SWConfig(aegean)
# At the moment software config needs to be done before hardware config
# because the schedule (init.h) is included in the patmos.v
swc.config()
hwc.config()

