
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library work;
use work.config.all;
use work.ocp.all;

entity aegean_top is
	port(
		clk	: in std_logic;
		iUart0Pins_rxd	: in std_logic;
		oUart0Pins_txd	: out std_logic;
		oLed0Pins_led	: out std_logic;
		oLed1Pins_led	: out std_logic;
		oLed2Pins_led	: out std_logic;
		oLed3Pins_led	: out std_logic;
		oLed4Pins_led	: out std_logic;
		oLed5Pins_led	: out std_logic;
		oLed6Pins_led	: out std_logic;
		oLed7Pins_led	: out std_logic;
		oLed8Pins_led	: out std_logic;

		-- memory interface
		dram_CLK   : out   std_logic;   -- Clock
		dram_CKE   : out   std_logic;   -- Clock Enable
		dram_RAS_n : out   std_logic;   -- Row Address Strobe
		dram_CAS_n : out   std_logic;   -- Column Address Strobe
		dram_WE_n  : out   std_logic;   -- Write Enable
		dram_CS_n  : out   std_logic;   -- Chip Select
		dram_BA_0  : out   std_logic;   -- Bank Address
		dram_BA_1  : out   std_logic;   -- Bank Address
		dram_ADDR  : out   std_logic_vector(12 downto 0); -- SDRAM Address
		-- SDRAM interface lower chip
		dram0_UDQM : out   std_logic;   -- Data mask Upper Byte
		dram0_LDQM : out   std_logic;   -- Data mask Lower Byte
		-- SDRAM interface highier chip
		dram1_UDQM : out   std_logic;   -- Data mask Upper Byte
		dram1_LDQM : out   std_logic;   -- Data mask Lower Byte
		-- data bus from both chips
		dram_DQ    : inout std_logic_vector(31 downto 0) -- Data
	);

end entity;

architecture struct of aegean_top is

	component sc_sdram_top is
		port(
			clk, rst        : in    std_logic;

			pll_locked      : in    std_logic;
			dram_clk_skewed : in    std_logic;

			-- User interface
			M_Cmd           : in    std_logic_vector(2 downto 0);
			M_Addr          : in    std_logic_vector(26 downto 0);
			M_Data          : in    std_logic_vector(31 downto 0);
			M_DataValid     : in    std_logic;
			M_DataByteEn    : in    std_logic_vector(3 downto 0);
			S_Resp          : out   std_logic_vector(1 downto 0);
			S_Data          : out   std_logic_vector(31 downto 0);
			S_CmdAccept     : out   std_logic;
			S_DataAccept    : out   std_logic;
			M_CmdRefresh    : in    std_logic;
			S_RefreshAccept : out   std_logic;

			-- memory interface
			dram_CLK        : out   std_logic; -- Clock
			dram_CKE        : out   std_logic; -- Clock Enable
			dram_RAS_n      : out   std_logic; -- Row Address Strobe
			dram_CAS_n      : out   std_logic; -- Column Address Strobe
			dram_WE_n       : out   std_logic; -- Write Enable
			dram_CS_n       : out   std_logic; -- Chip Select
			dram_BA_0       : out   std_logic; -- Bank Address
			dram_BA_1       : out   std_logic; -- Bank Address
			dram_ADDR       : out   std_logic_vector(12 downto 0); -- SDRAM Address
			-- SDRAM interface lower chip
			dram0_UDQM      : out   std_logic; -- Data mask Upper Byte
			dram0_LDQM      : out   std_logic; -- Data mask Lower Byte
			-- SDRAM interface highier chip
			dram1_UDQM      : out   std_logic; -- Data mask Upper Byte
			dram1_LDQM      : out   std_logic; -- Data mask Lower Byte
			-- data bus from both chips
			dram_DQ         : inout std_logic_vector(31 downto 0) -- Data
		);
	end component;

	component de2_115_sdram_pll is
		port(
			inclk0 : IN  STD_LOGIC := '0';
			c0     : OUT STD_LOGIC;
			c1     : OUT STD_LOGIC;
			c2     : OUT STD_LOGIC;
			locked : OUT STD_LOGIC
		);
	end component;

	signal sys_clk, dram_clk_int, dram_clk_skew : std_logic;

	-- for generation of internal reset
	signal pll_locked : std_logic;
	signal rst, rst_n : std_logic;
	signal res_cnt    : unsigned(2 downto 0) := "000"; -- for the simulation
	signal ref_cnt    : unsigned(9 downto 0);

	signal MCmd_int        : std_logic_vector(2 downto 0);
	signal MAddr_int       : std_logic_vector(26 downto 0);
	signal MData_int       : std_logic_vector(31 downto 0);
	signal MDataByteEn_int : std_logic_vector(3 downto 0);
	signal MDataValid_int  : std_logic;
	signal SResp_int       : std_logic_vector(1 downto 0);
	signal SData_int       : std_logic_vector(31 downto 0);
	signal SCmdAccept_int  : std_logic;
	signal SDataAccept_int : std_logic;

	signal M_CmdRefresh_int, S_RefreshAccept_int : std_logic;		

	attribute altera_attribute : string;
	attribute altera_attribute of res_cnt : signal is "POWER_UP_LEVEL=LOW";


begin

process(sys_clk, pll_locked)
	begin
		if pll_locked = '0' then
			res_cnt <= "000";
			rst     <= '1';
		elsif rising_edge(sys_clk) then
			if (res_cnt /= "111") then
				res_cnt <= res_cnt + 1;
			end if;
			rst <= not res_cnt(0) or not res_cnt(1) or not res_cnt(2);
		end if;
	end process;
	--rst_n  <= not rst;

	pll : de2_115_sdram_pll
		port map(
			inclk0 => clk,
			c0     => sys_clk,
			c1     => open,--dram_clk_int,
			c2     => dram_clk_skew,
			locked => pll_locked);

	dram_clk_int <= sys_clk;

	--Temporarely project that mananges the refresh of the of the memory once every 512CC (max 624 @ 80MHZ)
	process(sys_clk)
	begin
		if rising_edge(sys_clk) then
			if rst = '1' then
				M_CmdRefresh_int <= '0';
				ref_cnt <= "0000000000";
			else
				if (ref_cnt = "1000000000") then
					M_CmdRefresh_int <= '1';--time to refresh
					ref_cnt <= "1111111111";
				elsif(ref_cnt = "1111111111") then
					M_CmdRefresh_int <= '1';
					if (S_RefreshAccept_int = '1') then
						M_CmdRefresh_int <= '0';
						ref_cnt <= "0000000000";
					end if;
				else
					ref_cnt <= ref_cnt + 1;
				end if;
			end if;
		end if;
	end process;
			
	sc_sdram_top_inst0 : sc_sdram_top port map(
			clk             => dram_clk_int, --
			rst             => rst,     --        : in    std_logic;

			pll_locked      => pll_locked, --      : in    std_logic;
			dram_clk_skewed => dram_clk_skew, -- : in    std_logic;

			-- User interface
			M_Cmd           => MCmd_int, --   : in    SDRAM_controller_master_type;
			M_Addr          => MAddr_int, --
			M_Data          => MData_int, --
			M_DataByteEn    => MDataByteEn_int, --
			M_DataValid     => MDataValid_int,
			S_CmdAccept     => SCmdAccept_int, --    : out   SDRAM_controller_slave_type;
			S_DataAccept    => SDataAccept_int, --
			S_Data          => SData_int, --
			S_Resp          => SResp_int, --
			M_CmdRefresh    => M_CmdRefresh_int, --: in    std_logic;
			S_RefreshAccept => S_RefreshAccept_int, --: out   std_logic;
			
			-- memory interface
			dram_CLK        => dram_CLK, --       : out   std_logic; -- Clock
			dram_CKE        => dram_CKE, --       : out   std_logic; -- Clock Enable
			dram_RAS_n      => dram_RAS_n, --     : out   std_logic; -- Row Address Strobe
			dram_CAS_n      => dram_CAS_n, --     : out   std_logic; -- Column Address Strobe
			dram_WE_n       => dram_WE_n, --      : out   std_logic; -- Write Enable
			dram_CS_n       => dram_CS_n, --      : out   std_logic; -- Chip Select
			dram_BA_0       => dram_BA_0, --      : out   std_logic; -- Bank Address
			dram_BA_1       => dram_BA_1, --      : out   std_logic; -- Bank Address
			dram_ADDR       => dram_ADDR, --      : out   std_logic_vector(12 downto 0); -- SDRAM Address
			-- SDRAM interface lower chip
			dram0_UDQM      => dram0_UDQM, --      : out   std_logic; -- Data mask Upper Byte
			dram0_LDQM      => dram0_LDQM, --      : out   std_logic; -- Data mask Lower Byte
			-- SDRAM interface highier chip
			dram1_UDQM      => dram1_UDQM, --      : out   std_logic; -- Data mask Upper Byte
			dram1_LDQM      => dram1_LDQM, --      : out   std_logic; -- Data mask Lower Byte
			-- data bus from both chips
			dram_DQ         => dram_DQ  --         : inout std_logic_vector(31 downto 0) -- Data
		);

	cmp : entity work.aegean
	port map(
		clk	=>	sys_clk,
		reset	=>	rst,
		--sram_burst_m	=>	--needs connection
		sram_burst_m.MCmd => MCmd_int,
		sram_burst_m.MAddr => MAddr_int,
		sram_burst_m.MData => MData_int,
		sram_burst_m.MDataValid => MDataValid_int,
		sram_burst_m.MDataByteEn => MDataByteEn_int,

		--sram_burst_s	=>	--needs connection
		sram_burst_s.SResp => SResp_int,
		sram_burst_s.SData => SData_int,
		sram_burst_s.SCmdAccept => SCmdAccept_int,
		sram_burst_s.SDataAccept => SDataAccept_int,

		io_uartPins_rx0	=>	iUart0Pins_rxd,
		io_uartPins_tx0	=>	oUart0Pins_txd,
		io_ledsPins_led0	=>	oLed0Pins_led,
		io_ledsPins_led1	=>	oLed1Pins_led,
		io_ledsPins_led2	=>	oLed2Pins_led,
		io_ledsPins_led3	=>	oLed3Pins_led,
		io_ledsPins_led4	=>	oLed4Pins_led,
		io_ledsPins_led5	=>	oLed5Pins_led,
		io_ledsPins_led6	=>	oLed6Pins_led,
		io_ledsPins_led7	=>	oLed7Pins_led,
		io_ledsPins_led8	=>	oLed8Pins_led	);		

end struct;
