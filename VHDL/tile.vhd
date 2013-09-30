--
-- Copyright: 2013, Technical University of Denmark, DTU Compute
-- Author: Rasmus BO Sorensen (rasmus@rbscloud.dk)
-- License: Simplified BSD License
--

-- VHDL component describing a tile in the Aegean platform
-- Including the following components:
--     Patmos (Processor)
--     Argo (Network Interface + Router)
--     Communication Scratchpad Memory

library ieee;
use ieee.std_logic_1164.all;

entity tile is
    generic(
        PROC_ID : natural
        );
    port (
        clk   : in  std_logic;
        reset : in  std_logic;
        io_led          : out std_logic_vector(8 downto 0);
        io_uartPins_tx  : out std_logic;
        io_uartPins_rx  : in  std_logic
        );
end entity ; -- tile

architecture arch of tile is
    component Patmos is
    port(
        clk             : in  std_logic;
        reset           : in  std_logic;
        io_dummy        : out std_logic_vector(31 downto 0);
        io_cpuId               : in  std_logic_vector(31 downto 0);
        -- Communication scratch pad signals
        io_comConf_M_Cmd       : out std_logic_vector(2 downto 0);
        io_comConf_M_Addr      : out std_logic_vector(31 downto 0);
        io_comConf_M_Data      : out std_logic_vector(31 downto 0);
        io_comConf_M_ByteEn    : out std_logic_vector(3 downto 0);
        io_comConf_M_RespAccept: out std_logic;
        io_comConf_S_Resp      : in  std_logic_vector(1 downto 0);
        io_comConf_S_Data      : in  std_logic_vector(31 downto 0);
        io_comConf_S_CmdAccept : in  std_logic;
        io_comSpm_M_Cmd        : out std_logic_vector(2 downto 0);
        io_comSpm_M_Addr       : out std_logic_vector(31 downto 0);
        io_comSpm_M_Data       : out std_logic_vector(31 downto 0);
        io_comSpm_M_ByteEn     : out std_logic_vector(3 downto 0);
        io_comSpm_S_Resp       : in  std_logic_vector(1 downto 0);
        io_comSpm_S_Data       : in  std_logic_vector(31 downto 0);
        -- Simple IO signals
        io_led          : out std_logic_vector(8 downto 0);
        io_uartPins_tx  : out std_logic;
        io_uartPins_rx  : in  std_logic;
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


begin

end architecture ; -- arch
