from codeGen.Component import Component

def getTop():
    top = Component('aegean_top_de2_70')
    top.addPackage('ieee','std_logic_1164')
    top.addPackage('ieee','numeric_std')
    top.addPackage('work','config')

    top.entity.addPort('clk')

    return top


def writeTriStateSig(top,name,dataWidth):
    if dataWidth > 1:
        strDataWidth = '('+str(dataWidth-1)+' downto 0)'
    else:
        strDataWidth = ''
    top.arch.declSignal(name+'_out_dout_ena','std_logic')
    top.arch.declSignal(name+'_out_dout','std_logic_vector'+strDataWidth)
    top.arch.declSignal(name+'_in_din','std_logic_vector'+strDataWidth)
    top.arch.declSignal(name+'_in_din_reg','std_logic_vector'+strDataWidth)


def attr(top):
    top.arch.decl('''
    attribute altera_attribute : string;
    attribute altera_attribute of res_cnt : signal is "POWER_UP_LEVEL=LOW";
''')

def pll_reset(top):
    top.arch.addToBody('''
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

def writeTriState(top,name,dataSig):
    top.arch.addToBody('''
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

def bindAegean(aegean):
    aegean.entity.bindPort('clk','clk_int')
    aegean.entity.bindPort('reset','int_res')
    aegean.entity.bindPort('led','oLedPins_led')
    aegean.entity.bindPort('txd','oUartPins_txd')
    aegean.entity.bindPort('rxd','iUartPins_rxd')
    aegean.entity.bindPort('io_sramPins_ram_out_addr','oSRAM_A')
    aegean.entity.bindPort('io_sramPins_ram_out_dout_ena','sram_out_dout_ena')
    aegean.entity.bindPort('io_sramPins_ram_out_nadsc','oSRAM_ADSC_N')
    aegean.entity.bindPort('io_sramPins_ram_out_noe','oSRAM_OE_N')
    aegean.entity.bindPort('io_sramPins_ram_out_nbwe','oSRAM_WE_N')
    aegean.entity.bindPort('io_sramPins_ram_out_nbw','oSRAM_BE_N')
    aegean.entity.bindPort('io_sramPins_ram_out_ngw','oSRAM_GW_N')
    aegean.entity.bindPort('io_sramPins_ram_out_nce1','oSRAM_CE1_N')
    aegean.entity.bindPort('io_sramPins_ram_out_ce2','oSRAM_CE2')
    aegean.entity.bindPort('io_sramPins_ram_out_nce3','oSRAM_CE3_N')
    aegean.entity.bindPort('io_sramPins_ram_out_nadsp','oSRAM_ADSP_N')
    aegean.entity.bindPort('io_sramPins_ram_out_nadv','oSRAM_ADV_N')
    aegean.entity.bindPort('io_sramPins_ram_out_dout','sram_out_dout')
    aegean.entity.bindPort('io_sramPins_ram_in_din','sram_in_din')
