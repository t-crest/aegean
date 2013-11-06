import os

XMLSCHEME = "xmlNotes/Aegean.xsd"

AEGEAN_PATH = os.getcwd()

POSEIDON = AEGEAN_PATH + "/../poseidon/build/Poseidon"

PATMOS_PATH = AEGEAN_PATH + "/../patmos"
BUILD_PATH = AEGEAN_PATH + "/build"

GEN_DIR= BUILD_PATH + "/generated/"
GEN_PLAT = GEN_DIR + "a.xml"
GEN_COM = GEN_DIR + "b.xml"
GEN_SCHED = GEN_DIR + "c.xml"

NOCFile = GEN_DIR + "noc.vhd"
AegeanFile = GEN_DIR + "noc.vhd"
ConfFile = GEN_DIR + "config.vhd"
