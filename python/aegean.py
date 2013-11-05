import os

XMLSCHEME = "xmlNotes/Aegean.xsd"

AEGEAN_PATH = os.getcwd()

POSEIDON = AEGEAN_PATH + "/../poseidon/build/Poseidon"

PATMOS_PATH = AEGEAN_PATH + "/../patmos"
BUILD_PATH = AEGEAN_PATH + "/build"

TMP_DIR= BUILD_PATH + "/tmp/"
TMP_PLAT = TMP_DIR + "a.xml"
TMP_COM = TMP_DIR + "b.xml"
TMP_SCHED = TMP_DIR + "c.xml"

NOCFile = TMP_DIR + "noc.vhd"
ConfFile = TMP_DIR + "config.vhd"
