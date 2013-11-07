import os

AEGEAN_PATH = os.getcwd()


XMLSCHEME = AEGEAN_PATH + "/xmlNotes/Aegean.xsd"

POSEIDON_PATH = AEGEAN_PATH + "/../poseidon"
POSEIDON_CONV = POSEIDON_PATH + "/Converter/build"
POSEIDON = POSEIDON_PATH + "/build/Poseidon"

PATMOS_PATH = AEGEAN_PATH + "/../patmos"
BUILD_PATH = AEGEAN_PATH + "/build"
TMP_BUILD_PATH = BUILD_PATH + "/xml"

###################################################
# Intermediate files
GEN_PLAT = TMP_BUILD_PATH + "/plat.xml"
GEN_COM = TMP_BUILD_PATH + "/com.xml"
GEN_SCHED = TMP_BUILD_PATH + "/sched.xml"

###################################################
# Final config files
CSCHED = BUILD_PATH + "/init.h"
NOCFile = BUILD_PATH + "/noc.vhd"
AegeanFile = BUILD_PATH + "/aegean.vhd"
ConfFile = BUILD_PATH + "/config.vhd"
