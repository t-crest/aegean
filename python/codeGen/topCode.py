def beginEntity(f):
    f.write('''\
--------------------------------------------------------------------------------
-- Auto generated entity for the aegean top level
--------------------------------------------------------------------------------
--
-- VHDL top level for the Aegean multi processor platform
--

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.config.all;

entity aegean_top_de2_70 is
    port(
        clk : in  std_logic;
''')

def writePort(f,name,direction,width,last):
    end = ''
    if not last:
        end = ';'

    if width > 1:
        strwidth = '_vector('+str(width-1)+' downto 0)'
    else:
        strwidth = ''

    f.write('''
        '''+name+''' : '''+direction+''' std_logic'''+strwidth+end)

def endEntity(f):
    f.write('''
    );
end entity ; -- aegean_top_de2_70
''')

def arch(f):
    f.write('''
architecture struct of aegean_top_de2_70 is

    -- DE2-70: 50 MHz clock => 80 MHz
    -- BeMicro: 16 MHz clock => 25.6 MHz
    constant pll_mult : natural := 8;
    constant pll_div  : natural := 5;

    signal clk_int : std_logic;

    -- for generation of internal reset
    signal int_res            : std_logic;
    signal res_reg1, res_reg2 : std_logic;
    signal res_cnt            : unsigned(2 downto 0) := "000"; -- for the simulation
''')

def writeTriStateSig(f,name,dataWidth):
    if dataWidth > 1:
        strDataWidth = '_vector('+str(dataWidth-1)+' downto 0)'
    else:
        strDataWidth = ''
    f.write('''
    -- '''+name+''' signals for tristate inout
    signal '''+name+'''_out_dout_ena : std_logic;
    signal '''+name+'''_out_dout : std_logic'''+strDataWidth+''';
    signal '''+name+'''_in_din : std_logic'''+strDataWidth+''';
    signal '''+name+'''_in_din_reg : std_logic'''+strDataWidth+''';
''')

def beginArch(f):
    f.write('''
    attribute altera_attribute : string;
    attribute altera_attribute of res_cnt : signal is "POWER_UP_LEVEL=LOW";

begin
    pll_inst : entity work.pll generic map(
            multiply_by => pll_mult,
            divide_by   => pll_div
        )
        port map(
            inclk0 => clk,
            c0     => clk_int,
            c1     => oSRAM_CLK
        );
    -- we use a PLL
    -- clk_int <= clk;

    --
    --  internal reset generation
    --  should include the PLL lock signal
    --
    process(clk_int)
    begin
        if rising_edge(clk_int) then
            if (res_cnt /= "111") then
                res_cnt <= res_cnt + 1;
            end if;
            res_reg1 <= not res_cnt(0) or not res_cnt(1) or not res_cnt(2);
            res_reg2 <= res_reg1;
            int_res  <= res_reg2;
        end if;
    end process;
''')

def writeTriState(f,name,dataSig):
    f.write('''
    -- capture input from '''+name+''' on falling clk edge
    process(clk_int, int_res)
    begin
        if int_res='1' then
            '''+name+'''_in_din_reg <= (others => '0');
        elsif falling_edge(clk_int) then
            '''+name+'''_in_din_reg <= '''+dataSig+''';
        end if;
    end process;

    -- tristate output to '''+name+'''
    process('''+name+'''_out_dout_ena, '''+name+'''_out_dout)
    begin
        if '''+name+'''_out_dout_ena='1' then
            '''+dataSig+''' <= '''+name+'''_out_dout;
        else
            '''+dataSig+''' <= (others => 'Z');
        end if;
    end process;

    -- input of tristate on positive clk edge
    process(clk_int)
    begin
        if rising_edge(clk_int) then
            '''+name+'''_in_din <= '''+name+'''_in_din_reg;
        end if;
    end process;
''')

def aegean(f):
    f.write('''
    cmp : entity work.aegean port map(
        clk => clk_int,
        reset => int_res,
        led => led,
        txd => txd,
        rxd => rxd,
        io_sramPins_ram_out_addr    => oSRAM_A,
        io_sramPins_ram_out_dout_ena=> sram_out_dout_ena,
        io_sramPins_ram_out_nadsc   => oSRAM_ADSC_N,
        io_sramPins_ram_out_noe     => oSRAM_OE_N,
        io_sramPins_ram_out_nbwe    => oSRAM_WE_N,
        io_sramPins_ram_out_nbw     => oSRAM_BE_N,
        io_sramPins_ram_out_ngw     => oSRAM_GW_N,
        io_sramPins_ram_out_nce1    => oSRAM_CE1_N,
        io_sramPins_ram_out_ce2     => oSRAM_CE2,
        io_sramPins_ram_out_nce3    => oSRAM_CE3_N,
        io_sramPins_ram_out_nadsp   => oSRAM_ADSP_N,
        io_sramPins_ram_out_nadv    => oSRAM_ADV_N,
        io_sramPins_ram_out_dout    => sram_out_dout,
        io_sramPins_ram_in_din      => sram_in_din
        );
''')

def endArch(f):
    f.write('''
end architecture ; -- struct
''')
