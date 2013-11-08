#! /usr/bin/env python3

import sys
import paths
import os, errno
from lxml import etree
from io import StringIO

from paths import Paths
from hardwareConfig import HWConfig
from softwareConfig import SWConfig

def parseXML(filename,xmlscheme):
    parser = etree.XMLParser(remove_comments=True)
    tree = etree.parse(filename, parser=parser)
    xmlschema_doc = etree.parse(xmlscheme)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    xmlschema.assertValid(tree)
    if xmlschema.validate(tree):
        return tree.getroot()

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

xmlscheme = os.getcwd() + "/xmlNotes/Aegean.xsd"
aegean = parseXML(sys.argv[1],xmlscheme)
projectname = aegean.get("projectname")
p = Paths(projectname)
mkdir_p(p.TMP_BUILD_PATH)

hwc = HWConfig(p,aegean)
swc = SWConfig(p,aegean)
# At the moment software config needs to be done before hardware config
# because the schedule (init.h) is included in the patmos.v
swc.config()
hwc.config()

