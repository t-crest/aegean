import sys
import string
import aegean
from lxml import etree

class HWConfig(object):
    """
    The HWConfig class handles the hardware configuration of the aegean platform
    """
    def __init__(self,aegean):
        self.platform = list(aegean)[0]

    def config(self):
        self.createHardware()

    def createHardware(self):
        print("Creating Hardware...",end="")
        et = etree.ElementTree(self.platform)
        et.write(aegean.TMP_PLAT)
        self.generateNoC()
        self.hardwareDone()

    def hardwareDone(self):
        print("Still To Be Done")

    def generateNoC(self):
        f = open(aegean.NOCFile, 'w')
        f.write('''\
--------------------------------------------------------------------------------
-- Auto generated NoC entity for the aegean platform.
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use ieee.numeric_std.all;
use work.config.all;
use work.ocp.all;
use work.noc_defs.all;
use work.noc_interface.all;


entity noc is
port (
    clk         : in std_logic;
    reset       : in std_logic;

    ocp_io_ms   : in ocp_io_m_a;
    ocp_io_ss   : out ocp_io_s_a;

    spm_ports_m : out spm_masters;
    spm_ports_s : in spm_slaves

);

end noc;

architecture struct of noc is

------------------------------component declarations----------------------------

component noc_node is
port (
    p_clk       : in std_logic;
    n_clk       : in std_logic;
    reset       : in std_logic;

    proc_m      : in ocp_io_m;
    proc_s      : out ocp_io_s;

    spm_m       : out spm_master;
    spm_s       : in spm_slave;

    inNorth     : in network_link;
    inSouth     : in network_link;
    inEast      : in network_link;
    inWest      : in network_link;

    outNorth    : out network_link;
    outSouth    : out network_link;
    outEast     : out network_link;
    outWest     : out network_link

);

end component;
        ''')
        f.close()

