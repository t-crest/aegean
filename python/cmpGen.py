from lxml import etree
import paths
import subprocess

class CMPGen(object):
    """
    The CMPGen class handles the generation of the Aegean hardware platform
    """
    def __init__(self,p,platform):
        self.p = p
        self.platform = platform
        self.IPCores = list(self.platform)[2]
        self.nodes = list(self.platform)[1]

    def IPgen(self):
        for i in range(0,len(self.IPCores)):
            IPType = self.IPCores[i].get("IPType")

            patmos = list(self.IPCores[i])[0]
            app = ""
            for j in range(0,len(patmos)):
                if patmos[j].tag == "bootrom":
                    app = patmos[j].get("app")
                    break

            et = etree.ElementTree(patmos)
            et.write(self.p.TMP_BUILD_PATH + "/" + IPType + ".xml")
            self.patmosGen(IPType,app,self.p.TMP_BUILD_PATH + "/" + IPType + ".xml")

    def patmosGen(self,IPType,bootapp,configfile):
        Patmos = ["make","-C",self.p.PATMOS_PATH]
        Patmos+= ["BOOTAPP="+bootapp]
        Patmos+= ["BOOTBUILDDIR="+self.p.BUILD_PATH]
        Patmos+= ["CHISELBUILDDIR="+self.p.BUILD_PATH]
        Patmos+= ["HWMODULEPREFIX="+IPType]
        Patmos+= ["CONFIGFILE="+configfile]
        Patmos+= ["gen"]
        subprocess.call(Patmos)

    def generate(self):
        self.IPgen()
        #self.nodes
        f = open(self.p.AegeanFile, 'w')
        f.write('''\
--------------------------------------------------------------------------------
-- Auto generated entity for the aegean platform,
-- processors, communication scratch pads and network on chip.
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.config.all;
use work.ocp.all;
use work.noc_interface.all;

entity aegean is
    port(
        clk   : in  std_logic;
        reset : in std_logic;
        led   : out std_logic_vector(8 downto 0);
        txd   : out std_logic;
        rxd   : in  std_logic;

        -- Sram signals
        io_sramPins_ram_out_addr    : out std_logic_vector(18 downto 0);
        io_sramPins_ram_out_dout_ena: out std_logic;
        io_sramPins_ram_out_nadsc   : out std_logic;
        io_sramPins_ram_out_noe     : out std_logic;
        io_sramPins_ram_out_nbwe    : out std_logic;
        io_sramPins_ram_out_nbw     : out std_logic_vector(3 downto 0);
        io_sramPins_ram_out_ngw     : out std_logic;
        io_sramPins_ram_out_nce1    : out std_logic;
        io_sramPins_ram_out_ce2     : out std_logic;
        io_sramPins_ram_out_nce3    : out std_logic;
        io_sramPins_ram_out_nadsp   : out std_logic;
        io_sramPins_ram_out_nadv    : out std_logic;
        io_sramPins_ram_out_dout    : out std_logic_vector(31 downto 0);
        io_sramPins_ram_in_din      : in  std_logic_vector(31 downto 0)
    );
end entity ; -- aegean

architecture struct of aegean is
    component patmosPatmos is
    port(
        clk                         : in  std_logic;
        reset                       : in  std_logic;
        io_cpuId                    : in  std_logic_vector(31 downto 0);
        -- Communication scratch pad signals
        io_comConf_M_Cmd            : out std_logic_vector(2 downto 0);
        io_comConf_M_Addr           : out std_logic_vector(31 downto 0);
        io_comConf_M_Data           : out std_logic_vector(31 downto 0);
        io_comConf_M_ByteEn         : out std_logic_vector(3 downto 0);
        io_comConf_M_RespAccept     : out std_logic;
        io_comConf_S_Resp           : in  std_logic_vector(1 downto 0);
        io_comConf_S_Data           : in  std_logic_vector(31 downto 0);
        io_comConf_S_CmdAccept      : in  std_logic;
        io_comSpm_M_Cmd             : out std_logic_vector(2 downto 0);
        io_comSpm_M_Addr            : out std_logic_vector(31 downto 0);
        io_comSpm_M_Data            : out std_logic_vector(31 downto 0);
        io_comSpm_M_ByteEn          : out std_logic_vector(3 downto 0);
        io_comSpm_S_Resp            : in  std_logic_vector(1 downto 0);
        io_comSpm_S_Data            : in  std_logic_vector(31 downto 0);
        -- Simple IO signals
        io_led                      : out std_logic_vector(8 downto 0);
        io_uartPins_tx              : out std_logic;
        io_uartPins_rx              : in  std_logic;
        -- Sram signals
        io_sramPins_ram_out_addr    : out std_logic_vector(18 downto 0);
        io_sramPins_ram_out_dout_ena: out std_logic;
        io_sramPins_ram_out_nadsc   : out std_logic;
        io_sramPins_ram_out_noe     : out std_logic;
        io_sramPins_ram_out_nbwe    : out std_logic;
        io_sramPins_ram_out_nbw     : out std_logic_vector(3 downto 0);
        io_sramPins_ram_out_ngw     : out std_logic;
        io_sramPins_ram_out_nce1    : out std_logic;
        io_sramPins_ram_out_ce2     : out std_logic;
        io_sramPins_ram_out_nce3    : out std_logic;
        io_sramPins_ram_out_nadsp   : out std_logic;
        io_sramPins_ram_out_nadv    : out std_logic;
        io_sramPins_ram_out_dout    : out std_logic_vector(31 downto 0);
        io_sramPins_ram_in_din      : in  std_logic_vector(31 downto 0)
        );
    end component;

    signal ocp_io_ms : ocp_io_m_a;
    signal ocp_io_ss : ocp_io_s_a;


    signal ocp_core_ms : ocp_core_m_a;
    signal ocp_core_ss : ocp_core_s_a;

    signal spm_ms : spm_masters;
    signal spm_ss : spm_slaves;


begin
''')
        for p in range(0,len(self.nodes)):
            patmos = self.nodes[p]
            label = patmos.get("id")
            IPType = patmos.get("IPTypeRef")
            if p == 0:
                f.write('''
    '''+label+''' : '''+IPType+'''Patmos port map(
        clk                           => clk,
        reset                         => reset,
        io_cpuId                      => std_logic_vector(to_unsigned('''+str(p)+''',32)),
        io_comConf_M_Cmd              => ocp_io_ms('''+str(p)+''').MCmd,
        io_comConf_M_Addr             => ocp_io_ms('''+str(p)+''').MAddr,
        io_comConf_M_Data             => ocp_io_ms('''+str(p)+''').MData,
        io_comConf_M_ByteEn           => ocp_io_ms('''+str(p)+''').MByteEn,
        io_comConf_M_RespAccept       => ocp_io_ms('''+str(p)+''').MRespAccept,
        io_comConf_S_Resp             => ocp_io_ss('''+str(p)+''').SResp,
        io_comConf_S_Data             => ocp_io_ss('''+str(p)+''').SData,
        io_comConf_S_CmdAccept        => ocp_io_ss('''+str(p)+''').SCmdAccept,
        io_comSpm_M_Cmd               => ocp_core_ms('''+str(p)+''').MCmd,
        io_comSpm_M_Addr              => ocp_core_ms('''+str(p)+''').MAddr,
        io_comSpm_M_Data              => ocp_core_ms('''+str(p)+''').MData,
        io_comSpm_M_ByteEn            => ocp_core_ms('''+str(p)+''').MByteEn,
        io_comSpm_S_Resp              => ocp_core_ss('''+str(p)+''').SResp,
        io_comSpm_S_Data              => ocp_core_ss('''+str(p)+''').SData,
        io_led                        => led,
        io_uartPins_tx                => txd,
        io_uartPins_rx                => rxd,
        io_sramPins_ram_out_addr      => io_sramPins_ram_out_addr    ,
        io_sramPins_ram_out_dout_ena  => io_sramPins_ram_out_dout_ena,
        io_sramPins_ram_out_nadsc     => io_sramPins_ram_out_nadsc   ,
        io_sramPins_ram_out_noe       => io_sramPins_ram_out_noe     ,
        io_sramPins_ram_out_nbwe      => io_sramPins_ram_out_nbwe    ,
        io_sramPins_ram_out_nbw       => io_sramPins_ram_out_nbw     ,
        io_sramPins_ram_out_ngw       => io_sramPins_ram_out_ngw     ,
        io_sramPins_ram_out_nce1      => io_sramPins_ram_out_nce1    ,
        io_sramPins_ram_out_ce2       => io_sramPins_ram_out_ce2     ,
        io_sramPins_ram_out_nce3      => io_sramPins_ram_out_nce3    ,
        io_sramPins_ram_out_nadsp     => io_sramPins_ram_out_nadsp   ,
        io_sramPins_ram_out_nadv      => io_sramPins_ram_out_nadv    ,
        io_sramPins_ram_out_dout      => io_sramPins_ram_out_dout    ,
        io_sramPins_ram_in_din        => io_sramPins_ram_in_din
    );

''')
            else:
                f.write('''
    '''+label+''' : '''+IPType+'''Patmos port map(
        clk                           => clk,
        reset                         => reset,
        io_cpuId                      => std_logic_vector(to_unsigned('''+str(p)+''',32)),
        io_comConf_M_Cmd              => ocp_io_ms('''+str(p)+''').MCmd,
        io_comConf_M_Addr             => ocp_io_ms('''+str(p)+''').MAddr,
        io_comConf_M_Data             => ocp_io_ms('''+str(p)+''').MData,
        io_comConf_M_ByteEn           => ocp_io_ms('''+str(p)+''').MByteEn,
        io_comConf_M_RespAccept       => ocp_io_ms('''+str(p)+''').MRespAccept,
        io_comConf_S_Resp             => ocp_io_ss('''+str(p)+''').SResp,
        io_comConf_S_Data             => ocp_io_ss('''+str(p)+''').SData,
        io_comConf_S_CmdAccept        => ocp_io_ss('''+str(p)+''').SCmdAccept,
        io_comSpm_M_Cmd               => ocp_core_ms('''+str(p)+''').MCmd,
        io_comSpm_M_Addr              => ocp_core_ms('''+str(p)+''').MAddr,
        io_comSpm_M_Data              => ocp_core_ms('''+str(p)+''').MData,
        io_comSpm_M_ByteEn            => ocp_core_ms('''+str(p)+''').MByteEn,
        io_comSpm_S_Resp              => ocp_core_ss('''+str(p)+''').SResp,
        io_comSpm_S_Data              => ocp_core_ss('''+str(p)+''').SData,
        io_led                        => open,
        io_uartPins_tx                => open,
        io_uartPins_rx                => '0',
        io_sramPins_ram_out_addr      => open,
        io_sramPins_ram_out_dout_ena  => open,
        io_sramPins_ram_out_nadsc     => open,
        io_sramPins_ram_out_noe       => open,
        io_sramPins_ram_out_nbwe      => open,
        io_sramPins_ram_out_nbw       => open,
        io_sramPins_ram_out_ngw       => open,
        io_sramPins_ram_out_nce1      => open,
        io_sramPins_ram_out_ce2       => open,
        io_sramPins_ram_out_nce3      => open,
        io_sramPins_ram_out_nadsp     => open,
        io_sramPins_ram_out_nadv      => open,
        io_sramPins_ram_out_dout      => open,
        io_sramPins_ram_in_din        => (others => '0')
    );

''')

        f.write('''\

    spms : for i in 0 to NODES-1 generate
        spm : entity work.com_spm port map(
                p_clk => clk,
                n_clk => clk,
                reset => reset,
                ocp_core_m => ocp_core_ms(i),
                ocp_core_s => ocp_core_ss(i),
                spm_m => spm_ms(i),
                spm_s => spm_ss(i)
            );
    end generate ; -- spms

    noc : entity work.noc port map(
            clk => clk,
            reset => reset,
            ocp_io_ms => ocp_io_ms,
            ocp_io_ss => ocp_io_ss,
            spm_ports_m => spm_ms,
            spm_ports_s => spm_ss
        );

end architecture ; -- struct

''')

        f.close()

