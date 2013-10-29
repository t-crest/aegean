#! /usr/bin/env python3

import sys
from lxml import etree
from io import StringIO
from subprocess import call

def parseXML(filename):
    tree = etree.parse(filename)
    xmlschema_doc = etree.parse("Aegean.xsd")
    xmlschema = etree.XMLSchema(xmlschema_doc)
    xmlschema.assertValid(tree)
    if xmlschema.validate(tree):
        return tree


#tree = parseXML(sys.argv[1])
tree = parseXML("Config_format.xml")
aegean = tree.getroot()

platform = list(aegean)[0]
application = list(aegean)[1]

for element in tree.iter():
   if (element.tag is etree.Comment) or (not element.text) or (not element.text.strip()):
       print(element.tag)
   else:
       print("%s - %s" % (element.tag, element.text))

call(["ls","-l"])
