import os

AEGEAN_PATH = os.getcwd()


XMLSCHEME = AEGEAN_PATH + "/xmlNotes/Aegean.xsd"

POSEIDON = AEGEAN_PATH + "/../poseidon/build/Poseidon"

PATMOS_PATH = AEGEAN_PATH + "/../patmos"
BUILD_PATH = AEGEAN_PATH + "/build"

GEN_PLAT = BUILD_PATH + "/a.xml"
GEN_COM = BUILD_PATH + "/b.xml"
GEN_SCHED = BUILD_PATH + "/c.xml"

NOCFile = BUILD_PATH + "/noc.vhd"
AegeanFile = BUILD_PATH + "/aegean.vhd"
ConfFile = BUILD_PATH + "/config.vhd"
