--
-- Copyright: 2013, Technical University of Denmark, DTU Compute
-- Author: Luca Pezzarossa (lpez@dtu.dk)
-- License: Simplified BSD License
--

--
-- VHDL top level for Aegean on the Digilent/Xilinx Genesys 2 board with off-chip memory
--

library work;
use work.config.all;
use work.ocp.all;

use work.icap_ctrl_defs.all;
use work.icap_ctrl_config.all;

Library UNISIM;
use UNISIM.vcomponents.all;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity aegean_top is
    port(
        clk_in_p        : in    std_logic;
        clk_in_n        : in    std_logic;

        led             : out   std_logic_vector(7 downto 0);
        keys            : in    std_logic_vector(3 downto 0);
        sw              : in    std_logic_vector(7 downto 0);

        --TXD, RXD naming uses terminal-centric naming convention
        uart_txd        : in    std_logic;
        uart_rxd        : out   std_logic;

        --DDR3 pins
        ddr3_dq         : inout std_logic_vector(31 downto 0);
        ddr3_dqs_p      : inout std_logic_vector(3 downto 0);
        ddr3_dqs_n      : inout std_logic_vector(3 downto 0);

        ddr3_addr       : out   std_logic_vector(14 downto 0);
        ddr3_ba         : out   std_logic_vector(2 downto 0);
        ddr3_ras_n      : out   std_logic;
        ddr3_cas_n      : out   std_logic;
        ddr3_we_n       : out   std_logic;
        ddr3_reset_n    : out   std_logic;
        ddr3_ck_p       : out   std_logic_vector(0 downto 0);
        ddr3_ck_n       : out   std_logic_vector(0 downto 0);
        ddr3_cke        : out   std_logic_vector(0 downto 0);
        ddr3_cs_n       : out   std_logic_vector(0 downto 0);
        ddr3_dm         : out   std_logic_vector(3 downto 0);
        ddr3_odt        : out   std_logic_vector(0 downto 0);

        --Audio interface
        audio_adc_sdata : in    std_logic;
        audio_adr       : out   std_logic_vector(1 downto 0);
        audio_bclk      : in    std_logic; --out std_logic;
        audio_dac_sdata : out   std_logic;
        audio_lrclk     : in    std_logic; --out std_logic;
        audio_mclk      : out   std_logic;
        audio_scl       : inout std_logic; --serial data output of i2c bus
        audio_sda       : inout std_logic --serial clock output of i2c bus

    );
end entity;

architecture struct of aegean_top is
    component ddr3_ctrl is
        port(
            ddr3_dq             : inout std_logic_vector(31 downto 0);
            ddr3_dqs_p          : inout std_logic_vector(3 downto 0);
            ddr3_dqs_n          : inout std_logic_vector(3 downto 0);

            ddr3_addr           : out   std_logic_vector(14 downto 0);
            ddr3_ba             : out   std_logic_vector(2 downto 0);
            ddr3_ras_n          : out   std_logic;
            ddr3_cas_n          : out   std_logic;
            ddr3_we_n           : out   std_logic;
            ddr3_reset_n        : out   std_logic;
            ddr3_ck_p           : out   std_logic_vector(0 downto 0);
            ddr3_ck_n           : out   std_logic_vector(0 downto 0);
            ddr3_cke            : out   std_logic_vector(0 downto 0);
            ddr3_cs_n           : out   std_logic_vector(0 downto 0);
            ddr3_dm             : out   std_logic_vector(3 downto 0);
            ddr3_odt            : out   std_logic_vector(0 downto 0);
            app_addr            : in    std_logic_vector(28 downto 0);
            app_cmd             : in    std_logic_vector(2 downto 0);
            app_en              : in    std_logic;
            app_wdf_data        : in    std_logic_vector(255 downto 0);
            app_wdf_end         : in    std_logic;
            app_wdf_mask        : in    std_logic_vector(31 downto 0);
            app_wdf_wren        : in    std_logic;
            app_rd_data         : out   std_logic_vector(255 downto 0);
            app_rd_data_end     : out   std_logic;
            app_rd_data_valid   : out   std_logic;
            app_rdy             : out   std_logic;
            app_wdf_rdy         : out   std_logic;
            app_sr_req          : in    std_logic;
            app_ref_req         : in    std_logic;
            app_zq_req          : in    std_logic;
            app_sr_active       : out   std_logic;
            app_ref_ack         : out   std_logic;
            app_zq_ack          : out   std_logic;
            ui_clk              : out   std_logic;
            ui_clk_sync_rst     : out   std_logic;
            init_calib_complete : out   std_logic;
            device_temp         : out   std_logic_vector(11 downto 0);
            -- System Clock Ports
            sys_clk_i           : in    std_logic;
            --device_temp_o                    : out std_logic_vector(11 downto 0);
            sys_rst             : in    std_logic
        );
    end component;

    component ocp_burst_to_ddr3_ctrl is
        port(
            -- Common
            clk               : in  std_logic;
            rst               : in  std_logic;

            -- OCPburst IN (slave)
            MCmd              : in  std_logic_vector(2 downto 0);
            MAddr             : in  std_logic_vector(31 downto 0);
            MData             : in  std_logic_vector(31 downto 0);
            MDataValid        : in  std_logic;
            MDataByteEn       : in  std_logic_vector(3 downto 0);

            SResp             : out std_logic_vector(1 downto 0);
            SData             : out std_logic_vector(31 downto 0);
            SCmdAccept        : out std_logic;
            SDataAccept       : out std_logic;

            -- Xilinx interface
            app_addr          : out std_logic_vector(28 downto 0); --
            app_cmd           : out std_logic_vector(2 downto 0); --
            app_en            : out std_logic;
            app_wdf_data      : out std_logic_vector(255 downto 0);
            app_wdf_end       : out std_logic;
            app_wdf_mask      : out std_logic_vector(31 downto 0);
            app_wdf_wren      : out std_logic;
            app_rd_data       : in  std_logic_vector(255 downto 0); --
            app_rd_data_end   : in  std_logic; --
            app_rd_data_valid : in  std_logic;
            app_rdy           : in  std_logic;
            app_wdf_rdy       : in  std_logic
        );
    end component;

    component clk_manager is
        port(
            clk_in_p  : in  std_logic;
            clk_in_n  : in  std_logic;
            clk_out_1 : out std_logic;
            clk_out_2 : out std_logic;
            locked    : out std_logic
        );
    end component;

    component ADAU1761_i2c_bridge is
        generic(
            OCP_DATA_WIDTH : integer := 32;
            OCP_ADDR_WIDTH : integer := 16;
            input_clk      : integer := 100_000_000; --input clock speed from user logic in Hz
            bus_clk        : integer := 400_000); --speed the i2c bus (scl) will run at in Hz
        port(
            clk     : in    std_logic;
            reset   : in    std_logic;

            -- OCP IN (slave)
            MCmd    : in    std_logic_vector(2 downto 0);
            MAddr   : in    std_logic_vector((OCP_ADDR_WIDTH - 1) downto 0);
            MData   : in    std_logic_vector((OCP_DATA_WIDTH - 1) downto 0);
            MByteEn : in    std_logic_vector(3 downto 0);
            SResp   : out   std_logic_vector(1 downto 0);
            SData   : out   std_logic_vector((OCP_DATA_WIDTH - 1) downto 0);

            sda     : inout std_logic;  --serial data output of i2c bus
            scl     : inout std_logic   --serial clock output of i2c bus
        );
    end component;

    component I2S_seri_deseri_cdc is
        generic(
            ADC_RESOLUTION : natural := 24;
            DAC_RESOLUTION : natural := 24
        );
        port(clk           : in  STD_LOGIC;
             reset         : in  STD_LOGIC;

             adc_valid     : out STD_LOGIC;
             adc_data_l    : out STD_LOGIC_VECTOR(ADC_RESOLUTION - 1 downto 0);
             adc_data_r    : out STD_LOGIC_VECTOR(ADC_RESOLUTION - 1 downto 0);

             dac_accept    : out STD_LOGIC;
             dac_data_l    : in  STD_LOGIC_VECTOR(DAC_RESOLUTION - 1 downto 0);
             dac_data_r    : in  STD_LOGIC_VECTOR(DAC_RESOLUTION - 1 downto 0);

             i2s_bclk      : in  STD_LOGIC;
             i2s_lrclk     : in  STD_LOGIC;
             i2s_adc_sdata : in  STD_LOGIC;
             i2s_dac_sdata : out STD_LOGIC);
    end component;

    component audio_buffer is
        generic(
            BUFFER_SIZE_WIDTH : integer := 8; --IN BITS OF ADDRESSING
            BUFFER_DATA_WIDTH : integer := 16;
            OCP_DATA_WIDTH    : integer := 32;
            OCP_ADDR_WIDTH    : integer := 16
        );
        port(
            clk      : in  std_logic;
            reset    : in  std_logic;

            --ADC
            --write port
            data_in  : in  std_logic_vector(BUFFER_DATA_WIDTH - 1 downto 0);
            wr_en    : in  std_logic;

            --DAC
            --read port
            data_out : out std_logic_vector(BUFFER_DATA_WIDTH - 1 downto 0);
            rd_en    : in  std_logic;

            -- OCP IN (slave)
            MCmd     : in  std_logic_vector(2 downto 0);
            MAddr    : in  std_logic_vector((OCP_ADDR_WIDTH - 1) downto 0);
            MData    : in  std_logic_vector((OCP_DATA_WIDTH - 1) downto 0);
            MByteEn  : in  std_logic_vector(3 downto 0);
            SResp    : out std_logic_vector(1 downto 0);
            SData    : out std_logic_vector((OCP_DATA_WIDTH - 1) downto 0);

            gpio     : out std_logic_vector(31 downto 0)
        );
    end component;

    component filter_lp IS
        PORT(clk        : IN  std_logic;
             clk_enable : IN  std_logic;
             reset      : IN  std_logic;
             filter_in  : IN  std_logic_vector(15 DOWNTO 0); -- sfix16_En15
             filter_out : OUT std_logic_vector(15 DOWNTO 0) -- sfix16_En15
        );
    END component;

    component filter_hp IS
        PORT(clk        : IN  std_logic;
             clk_enable : IN  std_logic;
             reset      : IN  std_logic;
             filter_in  : IN  std_logic_vector(15 DOWNTO 0); -- sfix16_En15
             filter_out : OUT std_logic_vector(15 DOWNTO 0) -- sfix16_En15
        );
    END component;

    component filter_bp IS
        PORT(clk        : IN  std_logic;
             clk_enable : IN  std_logic;
             reset      : IN  std_logic;
             filter_in  : IN  std_logic_vector(15 DOWNTO 0); -- sfix16_En15
             filter_out : OUT std_logic_vector(15 DOWNTO 0) -- sfix16_En15
        );
    END component;

    component filter_rr IS
        PORT(clk        : IN  std_logic;
             clk_enable : IN  std_logic;
             reset      : IN  std_logic;
             filter_in  : IN  std_logic_vector(31 DOWNTO 0); -- sfix16_En15
             filter_out : OUT std_logic_vector(31 DOWNTO 0) -- sfix16_En15
        );
    END component;

    component pipe IS
        GENERIC(
            DATA_SIZE   : natural;
            PIPE_LENGTH : natural
        );
        PORT(clk        : IN  std_logic;
             clk_enable : IN  std_logic;
             reset      : IN  std_logic;
             pipe_in    : IN  std_logic_vector(DATA_SIZE - 1 DOWNTO 0);
             pipe_out   : OUT std_logic_vector(DATA_SIZE - 1 DOWNTO 0)
        );
    END component;

    component recon_buffer is
        generic(
            OCP_ADDR_WIDTH  : natural;  -- must be 16 (the 2 LSB are not used) the MSB is always the bank_select enable bit
            BRAM_ADDR_WIDTH : natural;  -- this detemines the size of each bank (must be < or = than OCP_ADDR_WIDTH-1)
            BANK_ADDR_WIDTH : natural   -- this detemines the number of banks
        );
        port(
            clk         : in  std_logic;
            rst         : in  std_logic;

            -- OCP interface (slave) for Patmos
            MCmd        : in  std_logic_vector(2 downto 0);
            MAddr       : in  std_logic_vector((OCP_ADDR_WIDTH - 1) downto 0);
            MData       : in  std_logic_vector(31 downto 0);
            MByteEn     : in  std_logic_vector(3 downto 0);
            SResp       : out std_logic_vector(1 downto 0);
            SData       : out std_logic_vector(31 downto 0);

            -- Bram interface for ICAP controller 
            bram_addr   : in  std_logic_vector((BANK_ADDR_WIDTH + BRAM_ADDR_WIDTH - 1) downto 0);
            --bram_addr   : in  std_logic_vector((2 + BRAM_ADDR_WIDTH - 1) downto 0);
            bram_data_o : out std_logic_vector(31 downto 0);
            bram_we     : in  std_logic_vector(3 downto 0);
            bram_data_i : in  std_logic_vector(31 downto 0)
        );
    end component;

    component icap_ctrl is
        port(
            clk        : in  std_logic;
            reset      : in  std_logic;

            -- DMA Configuration Port - OCP
            config_m   : in  ocp_core_m;
            config_s   : out ocp_core_s;

            -- Bram interface for the BRAM buffer 
            ram_addr   : out std_logic_vector(RAM_ADDR_WIDTH - 1 downto 0);
            ram_data_i : in  std_logic_vector(31 downto 0);
            ram_re     : out std_logic;

            -- ICAP interface, the signals of this interface, despite their direction, have the name of the signals of the FPGA interface
            icap_BUSY  : in  std_logic;
            icap_O     : in  std_logic_vector(31 downto 0); -- 32-bit data output
            icap_CE    : out std_logic; -- Clock enable input
            icap_CLK   : out std_logic; -- Clock input
            icap_I     : out std_logic_vector(31 downto 0); -- 32-bit data input
            icap_WRITE : out std_logic  -- Write input
        );
    end component;

    signal clk_int : std_logic;
    signal clk_200 : std_logic;
    signal clk_12  : std_logic;

    -- for generation of internal reset
    signal int_res, int_res_n                     : std_logic;
    signal res_reg1, res_reg2, res_reg3, res_reg4 : std_logic;
    signal locked                                 : std_logic;

    signal sram_burst_m : ocp_burst_m;
    signal sram_burst_s : ocp_burst_s;

    -- signals for the bridge
    signal MCmd_bridge        : std_logic_vector(2 downto 0);
    signal MAddr_bridge       : std_logic_vector(31 downto 0);
    signal MData_bridge       : std_logic_vector(31 downto 0);
    signal MDataValid_bridge  : std_logic;
    signal MDataByteEn_bridge : std_logic_vector(3 downto 0);
    signal SResp_bridge       : std_logic_vector(1 downto 0);
    signal SData_bridge       : std_logic_vector(31 downto 0);
    signal SCmdAccept_bridge  : std_logic;
    signal SDataAccept_bridge : std_logic;

    signal app_addr_bridge          : std_logic_vector(28 downto 0); --
    signal app_cmd_bridge           : std_logic_vector(2 downto 0); --
    signal app_en_bridge            : std_logic;
    signal app_wdf_data_bridge      : std_logic_vector(255 downto 0);
    signal app_wdf_end_bridge       : std_logic;
    signal app_wdf_mask_bridge      : std_logic_vector(31 downto 0);
    signal app_wdf_wren_bridge      : std_logic;
    signal app_rd_data_bridge       : std_logic_vector(255 downto 0); --
    signal app_rd_data_end_bridge   : std_logic; --
    signal app_rd_data_valid_bridge : std_logic;
    signal app_rdy_bridge           : std_logic;
    signal app_wdf_rdy_bridge       : std_logic;

    signal I2CSubAddr_MCmd_bridge    : std_logic_vector(2 downto 0);
    signal I2CSubAddr_MAddr_bridge   : std_logic_vector(15 downto 0);
    signal I2CSubAddr_MData_bridge   : std_logic_vector(31 downto 0);
    signal I2CSubAddr_MByteEn_bridge : std_logic_vector(3 downto 0);
    signal I2CSubAddr_SResp_bridge   : std_logic_vector(1 downto 0);
    signal I2CSubAddr_SData_bridge   : std_logic_vector(31 downto 0);

    signal audioBuffer_MCmd_bridge    : std_logic_vector(2 downto 0);
    signal audioBuffer_MAddr_bridge   : std_logic_vector(15 downto 0);
    signal audioBuffer_MData_bridge   : std_logic_vector(31 downto 0);
    signal audioBuffer_MByteEn_bridge : std_logic_vector(3 downto 0);
    signal audioBuffer_SResp_bridge   : std_logic_vector(1 downto 0);
    signal audioBuffer_SData_bridge   : std_logic_vector(31 downto 0);

    signal audio_adc_sdata_int : std_logic;
    signal audio_bclk_int      : std_logic;
    signal audio_dac_sdata_int : std_logic;
    signal audio_lrclk_int     : std_logic;

    signal adc_valid_int  : STD_LOGIC;
    signal dac_accept_int : STD_LOGIC;

    signal adc_data_int : STD_LOGIC_VECTOR(31 downto 0);
    signal dac_data_int : STD_LOGIC_VECTOR(31 downto 0);
    
    signal dac_data_int_cpu : STD_LOGIC_VECTOR(31 downto 0);
    signal dac_accept_int_cpu : STD_LOGIC;

    signal adc_valid_int_prefil      : STD_LOGIC;
    signal adc_data_int_prefil       : STD_LOGIC_VECTOR(31 downto 0);
    signal adc_data_int_prefil_sw    : STD_LOGIC_VECTOR(31 downto 0);
    --signal adc_data_int_postfil : STD_LOGIC_VECTOR(31 downto 0);
    signal adc_data_int_postfil_lp   : STD_LOGIC_VECTOR(31 downto 0);
    signal adc_data_int_postfil_hp   : STD_LOGIC_VECTOR(31 downto 0);
    signal adc_data_int_postfil_bp   : STD_LOGIC_VECTOR(31 downto 0);
    signal adc_data_int_postfil_pipe : STD_LOGIC_VECTOR(31 downto 0);
    signal adc_data_int_postfil_rr   : STD_LOGIC_VECTOR(31 downto 0);
    signal adc_data_int_bypass   : STD_LOGIC_VECTOR(31 downto 0);

    signal gpio_int : std_logic_vector(31 downto 0);

    signal keys_n, keys_s1, keys_s2  : std_logic_vector(3 downto 0);

    signal sw_s1   : std_logic_vector(7 downto 0);
    signal sw_s2   : std_logic_vector(7 downto 0);
    signal sw_sync : std_logic_vector(7 downto 0);

    signal bRam_MCmd    : std_logic_vector(2 downto 0);
    signal bRam_MAddr   : std_logic_vector(15 downto 0);
    signal bRam_MData   : std_logic_vector(31 downto 0);
    signal bRam_MByteEn : std_logic_vector(3 downto 0);
    signal bRam_SResp   : std_logic_vector(1 downto 0);
    signal bRam_SData   : std_logic_vector(31 downto 0);

    signal icapCtrl_MCmd    : std_logic_vector(2 downto 0);
    signal icapCtrl_MAddr   : std_logic_vector(15 downto 0);
    signal icapCtrl_MData   : std_logic_vector(31 downto 0);
    signal icapCtrl_MByteEn : std_logic_vector(3 downto 0);
    signal icapCtrl_SResp   : std_logic_vector(1 downto 0);
    signal icapCtrl_SData   : std_logic_vector(31 downto 0);

    --signal bram_addr_int   : std_logic_vector(17 downto 0); --original
    --signal bram_addr_int   : std_logic_vector(16 downto 0);
    signal bram_addr_int   : std_logic_vector(19 downto 0);
    signal bram_data_o_int : std_logic_vector(31 downto 0);

    signal icap_BUSY_int  : std_logic;
    signal icap_O_int     : std_logic_vector(31 downto 0); -- 32-bit data output
    signal icap_CE_int    : std_logic;  -- Clock enable input
    signal icap_CLK_int   : std_logic;  -- Clock input
    signal icap_I_int     : std_logic_vector(31 downto 0); -- 32-bit data input
    signal icap_WRITE_int : std_logic;  -- Write input

begin
    led(4 downto 4) <= (others => '0');

    MCmd_bridge                <= sram_burst_m.MCmd;
    MAddr_bridge(31 downto 30) <= (others => '0');
    MAddr_bridge(29 downto 0)  <= sram_burst_m.MAddr;
    MData_bridge               <= sram_burst_m.MData;
    MDataValid_bridge          <= sram_burst_m.MDataValid;
    MDataByteEn_bridge         <= sram_burst_m.MDataByteEn;
    sram_burst_s.SResp         <= SResp_bridge;
    sram_burst_s.SData         <= SData_bridge;
    sram_burst_s.SCmdAccept    <= SCmdAccept_bridge;
    sram_burst_s.SDataAccept   <= SDataAccept_bridge;

    --TMP Audio interface
    audio_adr  <= "00";                 --       : out std_logic_vector(1 downto 0);
    audio_mclk <= clk_12;               --   : out std_logic;

    I2S_seri_deseri_cdc_inst_0 : I2S_seri_deseri_cdc
        generic map(
            ADC_RESOLUTION => 16,       --: natural := 24;
            DAC_RESOLUTION => 16        --: natural := 24
        )
        port map(
            clk           => clk_int,
            reset         => int_res_n,
            adc_valid     => adc_valid_int_prefil, -- : out STD_LOGIC;
            adc_data_l    => adc_data_int_prefil_sw(31 downto 16), -- : out STD_LOGIC_VECTOR (31 downto 0);
            adc_data_r    => adc_data_int_prefil_sw(15 downto 0), -- : out STD_LOGIC_VECTOR (31 downto 0);

            dac_accept    => dac_accept_int, -- : out STD_LOGIC;
            dac_data_l    => dac_data_int(31 downto 16), -- : in STD_LOGIC_VECTOR (31 downto 0);
            dac_data_r    => dac_data_int(15 downto 0), -- : in STD_LOGIC_VECTOR (31 downto 0);

            i2s_bclk      => audio_bclk, -- : in STD_LOGIC;
            i2s_lrclk     => audio_lrclk, -- : in STD_LOGIC;
            i2s_adc_sdata => audio_adc_sdata, -- : in STD_LOGIC;
            i2s_dac_sdata => audio_dac_sdata -- : out STD_LOGIC
        );

    process(clk_int)
    begin
        if rising_edge(clk_int) then
            if (int_res_n = '1') then
                sw_s1   <= (others => '0');
                sw_s2   <= (others => '0');
                sw_sync <= (others => '0');
                keys_s1   <= (others => '0');
                keys_s2   <= (others => '0');
                keys_n   <= (others => '0');
            else
                sw_s1   <= sw;
                sw_s2   <= sw_s1;
                sw_sync <= sw_s2;
                keys_s1 <= keys;
                keys_s2 <= keys_s1;
                keys_n <= not (keys_s2);
            end if;
        end if;
    end process;

    adc_data_int_prefil <= (others => '0') when (sw_sync(0) = '0') else adc_data_int_prefil_sw when (sw_sync(0) = '1');

    adc_data_int <= adc_data_int_postfil_pipe when (gpio_int(2 downto 0) = "000") else 
                    adc_data_int_postfil_lp when (gpio_int(2 downto 0) = "001") else 
                    adc_data_int_postfil_hp when (gpio_int(2 downto 0) = "010") else 
                    adc_data_int_postfil_bp when (gpio_int(2 downto 0) = "011") else
                    adc_data_int_postfil_rr when (gpio_int(2 downto 0) = "100");

    led(7 downto 5) <= gpio_int(2 downto 0);
                       --"000" when (gpio_int(2 downto 0) = "000") else 
                       --"001" when (gpio_int(2 downto 0) = "001") else 
                       --"010" when (gpio_int(2 downto 0) = "010") else 
                       --"011" when (gpio_int(2 downto 0) = "011") else 
                       --"100" when (gpio_int(2 downto 0) = "100");

    pipe_inst_1 : pipe --bypass for noc reconfig
        GENERIC MAP(
            DATA_SIZE   => 32,          --: natural;
            PIPE_LENGTH => 30           --: natural (need to be set properly)
        )
        PORT MAP(clk        => clk_int, --                            :   IN    std_logic; 
                 clk_enable => adc_valid_int_prefil, --                     :   IN    std_logic; 
                 reset      => int_res_n, --                          :   IN    std_logic; 
                 pipe_in    => adc_data_int, --                      :   IN    std_logic_vector(DATA_SIZE-1 DOWNTO 0);
                 pipe_out   => adc_data_int_bypass --                     :   OUT   std_logic_vector(DATA_SIZE-1 DOWNTO 0)
        );

    dac_data_int <= dac_data_int_cpu when (gpio_int(3) = '0') else 
                    adc_data_int_bypass when (gpio_int(3) = '1'); 
                    --adc_data_int_postfil_hp when (gpio_int(2 downto 0) = "010") else 
                    --adc_data_int_postfil_bp when (gpio_int(2 downto 0) = "011") else
                    --adc_data_int_postfil_rr when (gpio_int(2 downto 0) = "100");

    dac_accept_int_cpu <= dac_accept_int when (gpio_int(4) = '0') else 
                          '0' when (gpio_int(4) = '1'); 

    adc_valid_int <= adc_valid_int_prefil when (gpio_int(5) = '0') else 
                          '0' when (gpio_int(5) = '1'); 

    --adc_valid_int <= adc_valid_int_prefil;

    pipe_inst_0 : pipe --bypass for dpr
        GENERIC MAP(
            DATA_SIZE   => 32,          --: natural;
            PIPE_LENGTH => 9           --: natural
        )
        PORT MAP(clk        => clk_int, --                            :   IN    std_logic; 
                 clk_enable => adc_valid_int_prefil, --                     :   IN    std_logic; 
                 reset      => int_res_n, --                          :   IN    std_logic; 
                 pipe_in    => adc_data_int_prefil, --                      :   IN    std_logic_vector(DATA_SIZE-1 DOWNTO 0);
                 pipe_out   => adc_data_int_postfil_pipe --                     :   OUT   std_logic_vector(DATA_SIZE-1 DOWNTO 0)
        );

    filter_rr_inst_0 : filter_rr
        port map(
            clk        => clk_int,      --                             :   IN    std_logic; 
            clk_enable => adc_valid_int_prefil, --                     :   IN    std_logic; 
            reset      => int_res_n,    --                          :   IN    std_logic; 
            filter_in  => adc_data_int_prefil, --                      :   IN    std_logic_vector(15 DOWNTO 0); -- sfix16_En15
            filter_out => adc_data_int_postfil_rr --                     :   OUT   std_logic_vector(15 DOWNTO 0)  -- sfix16_En15
        );

    filter_lp_inst_0 : filter_lp
        port map(
            clk        => clk_int,      --                             :   IN    std_logic; 
            clk_enable => adc_valid_int_prefil, --                     :   IN    std_logic; 
            reset      => int_res_n,    --                          :   IN    std_logic; 
            filter_in  => adc_data_int_prefil(31 downto 16), --                      :   IN    std_logic_vector(15 DOWNTO 0); -- sfix16_En15
            filter_out => adc_data_int_postfil_lp(31 downto 16) --                     :   OUT   std_logic_vector(15 DOWNTO 0)  -- sfix16_En15
        );

    filter_lp_inst_1 : filter_lp
        port map(
            clk        => clk_int,      --                             :   IN    std_logic; 
            clk_enable => adc_valid_int_prefil, --                     :   IN    std_logic; 
            reset      => int_res_n,    --                          :   IN    std_logic; 
            filter_in  => adc_data_int_prefil(15 downto 0), --                      :   IN    std_logic_vector(15 DOWNTO 0); -- sfix16_En15
            filter_out => adc_data_int_postfil_lp(15 downto 0) --                     :   OUT   std_logic_vector(15 DOWNTO 0)  -- sfix16_En15
        );

    -- adc_data_int_postfil_hp <= (others => '0');
    -- adc_data_int_postfil_bp <= (others => '0');

    filter_hp_inst_0 : filter_hp
        port map(
            clk        => clk_int,      --                             :   IN    std_logic; 
            clk_enable => adc_valid_int_prefil, --                     :   IN    std_logic; 
            reset      => int_res_n,    --                          :   IN    std_logic; 
            filter_in  => adc_data_int_prefil(31 downto 16), --                      :   IN    std_logic_vector(15 DOWNTO 0); -- sfix16_En15
            filter_out => adc_data_int_postfil_hp(31 downto 16) --                     :   OUT   std_logic_vector(15 DOWNTO 0)  -- sfix16_En15
        );

    filter_hp_inst_1 : filter_hp
        port map(
            clk        => clk_int,      --                             :   IN    std_logic; 
            clk_enable => adc_valid_int_prefil, --                     :   IN    std_logic; 
            reset      => int_res_n,    --                          :   IN    std_logic; 
            filter_in  => adc_data_int_prefil(15 downto 0), --                      :   IN    std_logic_vector(15 DOWNTO 0); -- sfix16_En15
            filter_out => adc_data_int_postfil_hp(15 downto 0) --                     :   OUT   std_logic_vector(15 DOWNTO 0)  -- sfix16_En15
        );

    filter_bp_inst_0 : filter_bp
        port map(
            clk        => clk_int,      --                             :   IN    std_logic; 
            clk_enable => adc_valid_int_prefil, --                     :   IN    std_logic; 
            reset      => int_res_n,    --                          :   IN    std_logic; 
            filter_in  => adc_data_int_prefil(31 downto 16), --                      :   IN    std_logic_vector(15 DOWNTO 0); -- sfix16_En15
            filter_out => adc_data_int_postfil_bp(31 downto 16) --                     :   OUT   std_logic_vector(15 DOWNTO 0)  -- sfix16_En15
        );

    filter_bp_inst_1 : filter_bp
        port map(
            clk        => clk_int,      --                             :   IN    std_logic; 
            clk_enable => adc_valid_int_prefil, --                     :   IN    std_logic; 
            reset      => int_res_n,    --                          :   IN    std_logic; 
            filter_in  => adc_data_int_prefil(15 downto 0), --                      :   IN    std_logic_vector(15 DOWNTO 0); -- sfix16_En15
            filter_out => adc_data_int_postfil_bp(15 downto 0) --                     :   OUT   std_logic_vector(15 DOWNTO 0)  -- sfix16_En15
        );

    audio_buffer_inst_0 : audio_buffer
        generic map(
            BUFFER_SIZE_WIDTH => 7,     --IN BITS OF ADDRESSING -- 128 entries
            BUFFER_DATA_WIDTH => 32,
            OCP_DATA_WIDTH    => 32,
            OCP_ADDR_WIDTH    => 16
        )
        port map(
            clk      => clk_int,
            reset    => int_res_n,

            --ADC
            --write port
            data_in  => adc_data_int,   --: in  std_logic_vector(BUFFER_DATA_WIDTH - 1 downto 0);
            wr_en    => adc_valid_int,  -- : in  std_logic;

            --DAC
            --read port
            data_out => dac_data_int_cpu,   --: out std_logic_vector(BUFFER_DATA_WIDTH - 1 downto 0);
            rd_en    => dac_accept_int_cpu, --: in  std_logic;

            -- OCP IN (slave)
            MCmd     => audioBuffer_MCmd_bridge, --      : in  std_logic_vector(2 downto 0);
            MAddr    => audioBuffer_MAddr_bridge, --    : in  std_logic_vector((OCP_ADDR_WIDTH - 1) downto 0);
            MData    => audioBuffer_MData_bridge, --    : in  std_logic_vector((OCP_DATA_WIDTH - 1) downto 0);
            MByteEn  => audioBuffer_MByteEn_bridge, --   : in  std_logic_vector(3 downto 0);
            SResp    => audioBuffer_SResp_bridge, -- --    : out std_logic_vector(1 downto 0);
            SData    => audioBuffer_SData_bridge, -- --    : out std_logic_vector((OCP_DATA_WIDTH - 1) downto 0)

            gpio     => gpio_int        --: out  std_logic_vector(31 downto 0)
        );

    clk_manager_inst_0 : clk_manager port map(
            clk_in_p  => clk_in_p,
            clk_in_n  => clk_in_n,
            clk_out_1 => clk_200,
            clk_out_2 => clk_12,
            locked    => locked
        );

    --
    --  internal reset generation
    process(clk_200)
    begin
        if rising_edge(clk_200) then
            res_reg1 <= locked;
            res_reg2 <= res_reg1;
            --int_res_n <= not res_reg2; --reset active high (when 0 patmos is running)
            int_res  <= res_reg2;
        end if;
    end process;

    --
    --  internal reset generation
    process(clk_int)
    begin
        if rising_edge(clk_int) then
            res_reg3  <= int_res;
            res_reg4  <= res_reg3;
            int_res_n <= not res_reg4;  --reset active high (when 0 patmos is running)
        --int_res <= res_reg2;
        end if;
    end process;

    ocp_burst_to_ddr3_ctrl_inst_0 : ocp_burst_to_ddr3_ctrl port map(
            clk               => clk_int,
            rst               => int_res_n, -- --            : in std_logic; -- (=1 is reset)

            -- OCPburst IN (slave)
            MCmd              => MCmd_bridge, --              : in  std_logic_vector(2 downto 0);
            MAddr             => MAddr_bridge, --             : in  std_logic_vector(31 downto 0);
            MData             => MData_bridge, --             : in  std_logic_vector(31 downto 0);
            MDataValid        => MDataValid_bridge, --        : in  std_logic;
            MDataByteEn       => MDataByteEn_bridge, --       : in  std_logic_vector(3 downto 0);

            SResp             => SResp_bridge, --             : out std_logic_vector(1 downto 0);
            SData             => SData_bridge, --             : out std_logic_vector(31 downto 0);
            SCmdAccept        => SCmdAccept_bridge, --        : out std_logic;
            SDataAccept       => SDataAccept_bridge, --       : out std_logic;

            -- Xilinx interface
            app_addr          => app_addr_bridge, --             : out    std_logic_vector(28 downto 0); --
            app_cmd           => app_cmd_bridge, --              : out    std_logic_vector(2 downto 0); --
            app_en            => app_en_bridge, --               : out    std_logic;
            app_wdf_data      => app_wdf_data_bridge, --         : out    std_logic_vector(255 downto 0);
            app_wdf_end       => app_wdf_end_bridge, --          : out    std_logic;
            app_wdf_mask      => app_wdf_mask_bridge, --         : out    std_logic_vector(31 downto 0);
            app_wdf_wren      => app_wdf_wren_bridge, --         : out    std_logic;
            app_rd_data       => app_rd_data_bridge, --          : in   std_logic_vector(255 downto 0);--
            app_rd_data_end   => app_rd_data_end_bridge, --      : in   std_logic;--
            app_rd_data_valid => app_rd_data_valid_bridge, --    : in   std_logic;
            app_rdy           => app_rdy_bridge, --              : in   std_logic;
            app_wdf_rdy       => app_wdf_rdy_bridge --         : in   std_logic
        );

    ddr3_ctrl_inst_0 : ddr3_ctrl port map(
            ddr3_dq             => ddr3_dq, --: inout std_logic_vector(31 downto 0);
            ddr3_dqs_p          => ddr3_dqs_p, --    --: inout std_logic_vector(3 downto 0);
            ddr3_dqs_n          => ddr3_dqs_n, --    --: inout std_logic_vector(3 downto 0);

            ddr3_addr           => ddr3_addr, --     : out   std_logic_vector(14 downto 0);
            ddr3_ba             => ddr3_ba, --       : out   std_logic_vector(2 downto 0);
            ddr3_ras_n          => ddr3_ras_n, --    : out   std_logic;
            ddr3_cas_n          => ddr3_cas_n, --    : out   std_logic;
            ddr3_we_n           => ddr3_we_n, --     : out   std_logic;
            ddr3_reset_n        => ddr3_reset_n, --  : out   std_logic;
            ddr3_ck_p           => ddr3_ck_p, --     : out   std_logic_vector(0 downto 0);
            ddr3_ck_n           => ddr3_ck_n, --     : out   std_logic_vector(0 downto 0);
            ddr3_cke            => ddr3_cke, --      : out   std_logic_vector(0 downto 0);
            ddr3_cs_n           => ddr3_cs_n, --     : out   std_logic_vector(0 downto 0);
            ddr3_dm             => ddr3_dm, --       : out   std_logic_vector(3 downto 0);
            ddr3_odt            => ddr3_odt, --      : out   std_logic_vector(0 downto 0);

            app_addr            => app_addr_bridge, --                  : in    std_logic_vector(28 downto 0);
            app_cmd             => app_cmd_bridge, --                   : in    std_logic_vector(2 downto 0);
            app_en              => app_en_bridge, --                    : in    std_logic;
            app_wdf_data        => app_wdf_data_bridge, --              : in    std_logic_vector(255 downto 0);
            app_wdf_end         => app_wdf_end_bridge, --               : in    std_logic;
            app_wdf_mask        => app_wdf_mask_bridge, --         : in    std_logic_vector(31 downto 0);
            app_wdf_wren        => app_wdf_wren_bridge, --              : in    std_logic;
            app_rd_data         => app_rd_data_bridge, --              : out   std_logic_vector(255 downto 0);
            app_rd_data_end     => app_rd_data_end_bridge, --           : out   std_logic;
            app_rd_data_valid   => app_rd_data_valid_bridge, --         : out   std_logic;
            app_rdy             => app_rdy_bridge, --                   : out   std_logic;
            app_wdf_rdy         => app_wdf_rdy_bridge, --               : out   std_logic;

            app_sr_req          => '0', --                : in    std_logic;
            app_ref_req         => '0', --               : in    std_logic;
            app_zq_req          => '0', --                : in    std_logic;
            app_sr_active       => open, --             : out   std_logic;
            app_ref_ack         => open, --               : out   std_logic;
            app_zq_ack          => open, --                : out   std_logic;

            ui_clk              => clk_int, --                   : out   std_logic;
            ui_clk_sync_rst     => open, --           : out   std_logic;
            init_calib_complete => open, --       : out   std_logic;
            device_temp         => open,
            -- System Clock Ports
            sys_clk_i           => clk_200, --                      : in    std_logic;
            --device_temp_o => open,    --                    : out std_logic_vector(11 downto 0);
            sys_rst             => int_res -- reset active low                    : in    std_logic
        );

    ADAU1761_i2c_bridge_int_0 : ADAU1761_i2c_bridge
        generic map(
            OCP_DATA_WIDTH => 32,       --: integer := 32;
            OCP_ADDR_WIDTH => 16,       -- : integer := 16;
            input_clk      => 100_000_000, --      : integer := 100_000_000; --input clock speed from user logic in Hz
            bus_clk        => 400_000)  --        : integer := 400_000); --speed the i2c bus (scl) will run at in Hz
        port map(
            clk     => clk_int,         --     : in    std_logic;
            reset   => int_res_n,       --   : in    std_logic;

            -- OCP IN (slave)
            MCmd    => I2CSubAddr_MCmd_bridge, --    : in    std_logic_vector(2 downto 0);
            MAddr   => I2CSubAddr_MAddr_bridge, --   : in    std_logic_vector((OCP_ADDR_WIDTH - 1) downto 0);
            MData   => I2CSubAddr_MData_bridge, --   : in    std_logic_vector((OCP_DATA_WIDTH - 1) downto 0);
            MByteEn => I2CSubAddr_MByteEn_bridge, -- : in    std_logic_vector(3 downto 0);
            SResp   => I2CSubAddr_SResp_bridge, --   : out   std_logic_vector(1 downto 0);
            SData   => I2CSubAddr_SData_bridge, --   : out   std_logic_vector((OCP_DATA_WIDTH - 1) downto 0);

            sda     => audio_sda,       --     : inout std_logic;      --serial data output of i2c bus
            scl     => audio_scl        --     : inout std_logic       --serial clock output of i2c bus
        );

    cmp : entity work.aegean
        port map(
            clk                         => clk_int,
            reset                       => int_res_n,
            sram_burst_m                => sram_burst_m,
            sram_burst_s                => sram_burst_s,
            io_uartPins_rx0             => uart_txd, --TXD, RXD naming uses terminal-centric naming convention
            io_uartPins_tx0             => uart_rxd, --TXD, RXD naming uses terminal-centric naming convention
            io_keysPins_key0            => keys_n,
            io_ledsPins_led0            => led(0),
            io_i2CSubAddrPins_MCmd0     => I2CSubAddr_MCmd_bridge, -- : out std_logic_vector(2 downto 0);
            io_i2CSubAddrPins_MAddr0    => I2CSubAddr_MAddr_bridge, -- : out std_logic_vector(15 downto 0);
            io_i2CSubAddrPins_MData0    => I2CSubAddr_MData_bridge, -- : out std_logic_vector(31 downto 0);
            io_i2CSubAddrPins_MByteEn0  => I2CSubAddr_MByteEn_bridge, -- : out std_logic_vector(3 downto 0);
            io_i2CSubAddrPins_SResp0    => I2CSubAddr_SResp_bridge, -- : in std_logic_vector(1 downto 0);
            io_i2CSubAddrPins_SData0    => I2CSubAddr_SData_bridge, -- : in std_logic_vector(31 downto 0);       
            io_audioBufferPins_MCmd0    => audioBuffer_MCmd_bridge, -- : out std_logic_vector(2 downto 0);
            io_audioBufferPins_MAddr0   => audioBuffer_MAddr_bridge, -- : out std_logic_vector(15 downto 0);
            io_audioBufferPins_MData0   => audioBuffer_MData_bridge, -- : out std_logic_vector(31 downto 0);
            io_audioBufferPins_MByteEn0 => audioBuffer_MByteEn_bridge, -- : out std_logic_vector(3 downto 0);
            io_audioBufferPins_SResp0   => audioBuffer_SResp_bridge, -- : in std_logic_vector(1 downto 0);
            io_audioBufferPins_SData0   => audioBuffer_SData_bridge, -- : in std_logic_vector(31 downto 0);

            io_bRamCtrlPins_MCmd0       => bRam_MCmd,
            io_bRamCtrlPins_MAddr0      => bRam_MAddr,
            io_bRamCtrlPins_MData0      => bRam_MData,
            io_bRamCtrlPins_MByteEn0    => bRam_MByteEn,
            io_bRamCtrlPins_SResp0      => bRam_SResp,
            io_bRamCtrlPins_SData0      => bRam_SData,
            io_icapCtrlPins_MCmd0       => icapCtrl_MCmd,
            io_icapCtrlPins_MAddr0      => icapCtrl_MAddr,
            io_icapCtrlPins_MData0      => icapCtrl_MData,
            io_icapCtrlPins_MByteEn0    => icapCtrl_MByteEn,
            io_icapCtrlPins_SResp0      => icapCtrl_SResp,
            io_icapCtrlPins_SData0      => icapCtrl_SData,
            io_ledsPins_led1            => led(1),
            io_ledsPins_led2            => led(2),
            io_ledsPins_led3            => led(3));

    recon_buffer_comp : recon_buffer
        generic map(
            OCP_ADDR_WIDTH  => 16,      -- must be 16 (the 2 LSB are not used) the MSB is always the bank_select enable bit
            BRAM_ADDR_WIDTH => 15,      -- this detemines the size of each bank (must be < or = than OCP_ADDR_WIDTH-1)
            BANK_ADDR_WIDTH => 5        -- this detemines the number of banks (3 is 8 banks) /// it was 3
        )
        port map(
            clk         => clk_int,
            rst         => int_res_n,

            -- OCP interface (slave) for Patmos
            MCmd        => bRam_MCmd,
            MAddr       => bRam_MAddr,
            MData       => bRam_MData,
            MByteEn     => bRam_MByteEn,
            SResp       => bRam_SResp,
            SData       => bRam_SData,

            -- Bram interface for ICAP controller 
            bram_addr   => bram_addr_int,
            bram_data_o => bram_data_o_int,
            bram_we     => "0000",
            bram_data_i => (others => '0')
        );

    icap_ctrl_comp : icap_ctrl
        port map(
            clk              => clk_int, --  : in  std_logic;
            reset            => int_res_n, --     : in  std_logic;

            -- DMA Configuration Port - OCP
            config_m.MCmd    => icapCtrl_MCmd, --  : in  ocp_core_m;
            config_m.MAddr   => icapCtrl_MAddr, --  : in  ocp_core_m;
            config_m.MData   => icapCtrl_MData, --  : in  ocp_core_m;
            config_m.MByteEn => icapCtrl_MByteEn, --  : in  ocp_core_m;
            config_s.SResp   => icapCtrl_SResp, --  : out ocp_core_s;
            config_s.SData   => icapCtrl_SData, --  : out ocp_core_s;

            -- Bram interface for the BRAM buffer 
            ram_addr         => bram_addr_int, --  : out std_logic_vector(RAM_ADDR_WIDTH - 1 downto 0);
            ram_data_i       => bram_data_o_int, --: in  std_logic_vector(31 downto 0);
            ram_re           => open,   --    : out std_logic;

            -- ICAP interface, the signals of this interface, despite their direction, have the name of the signals of the FPGA interface
            icap_BUSY        => icap_BUSY_int, -- : in  std_logic;
            icap_O           => icap_O_int, --  : in  std_logic_vector(31 downto 0); -- 32-bit data output
            icap_CE          => icap_CE_int, --   : out std_logic;     -- Clock enable input
            icap_CLK         => icap_CLK_int, --  : out std_logic;     -- Clock input
            icap_I           => icap_I_int, --    : out std_logic_vector(31 downto 0); -- 32-bit data input
            icap_WRITE       => icap_WRITE_int --: out std_logic      -- Write input
        );

    -- ICAPE2: Internal Configuration Access Port
    --         Artix-7
    -- Xilinx HDL Language Template, version 2016.4

    icap_BUSY_int <= '1';

    ICAPE2_inst : ICAPE2
        generic map(
            DEVICE_ID         => X"3651093", -- Specifies the pre-programmed Device ID value to be used for simulation
            -- purposes.
            ICAP_WIDTH        => "X32", -- Specifies the input and output data width.
            SIM_CFG_FILE_NAME => "None" -- Specifies the Raw Bitstream (RBT) file to be parsed by the simulation
        -- model.
        )
        port map(
            O     => icap_O_int,        -- 32-bit output: Configuration data output bus
            CLK   => clk_int,           -- 1-bit input: Clock Input
            CSIB  => icap_CE_int,       -- 1-bit input: Active-Low ICAP Enable
            I     => icap_I_int,        -- 32-bit input: Configuration data input bus
            RDWRB => icap_WRITE_int     -- 1-bit input: Read/Write Select input
        );

-- End of ICAPE2_inst instantiation

end struct;
