def writeConfig(f,N,M,NODES):
    f.write('''\
package config is

    constant N : integer := '''+N+''';
    constant M : integer := '''+M+''';
    constant NODES : integer := '''+str(NODES)+''';

end package ; -- aegean_def

''')

def writeNoCHeader(f):
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

------------------------------signal declarations----------------------------

type link_n is array(0 to (N - 1)) of network_link;
type link_m is array(0 to (M - 1)) of link_n;

signal north_in  : link_m;
signal east_in   : link_m;
signal south_in  : link_m;
signal west_in   : link_m;
signal north_out : link_m;
signal east_out  : link_m;
signal south_out : link_m;
signal west_out  : link_m;


begin

''')

def writeNodeInst(f,instancename,k,i,j):
    f.write('''\
    '''+instancename+''' : noc_node
    port map (
        p_clk => clk,
        n_clk => clk,
        reset => reset,

        proc_m => ocp_io_ms('''+str(k)+'''),
        proc_s => ocp_io_ss('''+str(k)+'''),

        spm_m => spm_ports_m('''+str(k)+'''),
        spm_s => spm_ports_s('''+str(k)+'''),

        inNorth => north_in('''+i+''')('''+j+'''),
        inSouth => south_in('''+i+''')('''+j+'''),
        inEast => east_in('''+i+''')('''+j+'''),
        inWest => west_in('''+i+''')('''+j+'''),

        outNorth => north_out('''+i+''')('''+j+'''),
        outSouth => south_out('''+i+''')('''+j+'''),
        outEast => east_out('''+i+''')('''+j+'''),
        outWest => west_out('''+i+''')('''+j+''')
    );

''')

def writeEast(f,i1,i2,j1,j2):
    f.write('''
    east_in('''+i2+''')('''+j2+''') <= west_out('''+i1+''')('''+j1+''');
''')

def writeWest(f,i1,i2,j1,j2):
    f.write('''
    west_in('''+i2+''')('''+j2+''') <= east_out('''+i1+''')('''+j1+''');
''')

def writeSouth(f,i1,i2,j1,j2):
    f.write('''
    south_in('''+i2+''')('''+j2+''') <= north_out('''+i1+''')('''+j1+''');
''')

def writeNorth(f,i1,i2,j1,j2):
    f.write('''
    north_in('''+i2+''')('''+j2+''') <= south_out('''+i1+''')('''+j1+''');
''')

def writeBitorus(f):
    f.write('''
    links_m : for i in 0 to M-1 generate
        links_n : for j in 0 to N-1 generate
            top : if (i = 0) generate
                north_in(i)(j) <= south_out(M-1)(j);
                south_in(M-1)(j) <= north_out(i)(j);
            end generate top;
            left : if (j = 0) generate
                west_in(i)(j) <= east_out(i)(N-1);
                east_in(i)(N-1) <= west_out(i)(j);
            end generate left;
            bottom : if (i = (M-1) and j < (N-1)) generate
                east_in(i)(j) <= west_out(i)(j+1);
                west_in(i)(j+1) <= east_out(i)(j);
            end generate bottom;
            right : if (i < (M-1) and j = (N-1)) generate
                south_in(i)(j) <= north_out(i+1)(j);
                north_in(i+1)(j) <= south_out(i)(j);
            end generate right;
            center : if (i < (M-1) and j < (N-1)) generate
                north_in(i+1)(j) <= south_out(i)(j);
                south_in(i)(j) <= north_out(i+1)(j);
                west_in(i)(j+1) <= east_out(i)(j);
                east_in(i)(j) <= west_out(i)(j+1);
            end generate center;
        end generate links_n;
    end generate links_m;

''')

def writeMesh(f):
    f.write('''
    links_m : for i in 0 to M-1 generate
        links_n : for j in 0 to N-1 generate
            bottom : if (i = (M-1) and j < (N-1)) generate
                east_in(i)(j) <= west_out(i)(j+1);
                west_in(i)(j+1) <= east_out(i)(j);
            end generate bottom;
            right : if (i < (M-1) and j = (N-1)) generate
                south_in(i)(j) <= north_out(i+1)(j);
                north_in(i+1)(j) <= south_out(i)(j);
            end generate right;
            center : if (i < (M-1) and j < (N-1)) generate
                north_in(i+1)(j) <= south_out(i)(j);
                south_in(i)(j) <= north_out(i+1)(j);
                west_in(i)(j+1) <= east_out(i)(j);
                east_in(i)(j) <= west_out(i)(j+1);
            end generate center;
        end generate links_n;
    end generate links_m;

''')

def writeFooter(f):
    f.write('''\
end struct;
''')
