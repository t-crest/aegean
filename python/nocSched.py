import sys
import paths
import os, errno
import ntpath
from lxml import etree
from io import StringIO

from paths import Paths

from paths import Paths
from nocSchedConfig import NoCSchedConfig

def parseXML(filename,xmlscheme):
    parser = etree.XMLParser(remove_comments=True)
    tree = etree.parse(filename, parser=parser)
    tree.xinclude()
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

xmlscheme = os.getcwd() + '/xml_validation/Aegean_nocsched.xsd'
nocsched = parseXML(sys.argv[1],xmlscheme)

projectname = ntpath.basename(sys.argv[1])
projectname = os.path.splitext(projectname)[0]
print("Projectname: " + projectname)

p = Paths(projectname)
mkdir_p(p.TMP_BUILD_PATH)

nsc = NoCSchedConfig(p,nocsched)
nsc.config()
