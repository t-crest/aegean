#! /usr/bin/env python3

import sys
from lxml import etree
from io import StringIO

#f = open('../Poseidon/Config_format.xml')
#root = etree.XML(f.read())
#root = etree.parse("../Poseidon/Config_format.xml")
print(sys.argv)
root = etree.parse(sys.argv[1])

for element in root.iter():
	if (element.tag is etree.Comment) or (not element.text) or (not element.text.strip()):
		print(element.tag)
	else:
		print("%s - %s" % (element.tag, element.text))



xmlschema_doc = etree.parse("Aegean.xsd")
xmlschema = etree.XMLSchema(xmlschema_doc)

xmlschema.assertValid(root)

#if xmlschema.validate(root):
#	print("XML file validated.")
#else:
#	print("XML file invalid")
#
