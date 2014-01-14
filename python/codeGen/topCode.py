#
# Copyright Technical University of Denmark. All rights reserved.
# This file is part of the T-CREST project.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN
# NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of the copyright holder.
#
###############################################################################
# Authors:
#    Rasmus Bo Soerensen (rasmus@rbscloud.dk)
#
###############################################################################

from codeGen.Component import Component

def getTop():
    top = Component('aegean_top')
    top.addPackage('ieee','std_logic_1164')
    top.addPackage('ieee','numeric_std')
    top.addPackage('work','config')
    top.addPackage('work','ocp')

    top.entity.addPort('clk')

    return top

def getSram():
    sram = Component('SsramBurstRW')
    sram.entity.addPort('clk')
    sram.entity.addPort('reset')
    sram.entity.addPort('io_ocp_M_Cmd','in','std_logic_vector',3)
    sram.entity.addPort('io_ocp_M_Addr','in','std_logic_vector',21)
    sram.entity.addPort('io_ocp_M_Data','in','std_logic_vector',32)
    sram.entity.addPort('io_ocp_M_DataValid','in','std_logic')
    sram.entity.addPort('io_ocp_M_DataByteEn','in','std_logic_vector',4)
    sram.entity.addPort('io_ocp_S_Resp','out','std_logic_vector',2)
    sram.entity.addPort('io_ocp_S_Data','out','std_logic_vector',32)
    sram.entity.addPort('io_ocp_S_CmdAccept','out','std_logic')
    sram.entity.addPort('io_ocp_S_DataAccept','out','std_logic')
    sram.entity.addPort('io_ssramBurstRWPins_ramOut_addr','out','std_logic_vector',19)
    sram.entity.addPort('io_ssramBurstRWPins_ramOut_doutEna','out','std_logic')
    sram.entity.addPort('io_ssramBurstRWPins_ramOut_nadsc','out','std_logic')
    sram.entity.addPort('io_ssramBurstRWPins_ramOut_noe','out','std_logic')
    sram.entity.addPort('io_ssramBurstRWPins_ramOut_nbwe','out','std_logic')
    sram.entity.addPort('io_ssramBurstRWPins_ramOut_nbw','out','std_logic_vector',4)
    sram.entity.addPort('io_ssramBurstRWPins_ramOut_ngw','out','std_logic')
    sram.entity.addPort('io_ssramBurstRWPins_ramOut_nce1','out','std_logic')
    sram.entity.addPort('io_ssramBurstRWPins_ramOut_ce2','out','std_logic')
    sram.entity.addPort('io_ssramBurstRWPins_ramOut_nce3','out','std_logic')
    sram.entity.addPort('io_ssramBurstRWPins_ramOut_nadsp','out','std_logic')
    sram.entity.addPort('io_ssramBurstRWPins_ramOut_nadv','out','std_logic')
    sram.entity.addPort('io_ssramBurstRWPins_ramOut_dout','out','std_logic_vector',32)
    sram.entity.addPort('io_ssramBurstRWPins_ramIn_din','in','std_logic_vector',32)
    return sram

def bindSram(sram):
    sram.entity.bindPort('clk','clk')
    sram.entity.bindPort('reset','int_res')
    sram.entity.bindPort('io_ocp_M_Cmd','sram_burst_m.MCmd')
    sram.entity.bindPort('io_ocp_M_Addr','sram_burst_m.MAddr')
    sram.entity.bindPort('io_ocp_M_Data','sram_burst_m.MData')
    sram.entity.bindPort('io_ocp_M_DataValid','sram_burst_m.MDataValid')
    sram.entity.bindPort('io_ocp_M_DataByteEn','sram_burst_m.MDataByteEn')
    sram.entity.bindPort('io_ocp_S_Resp','sram_burst_s.SResp')
    sram.entity.bindPort('io_ocp_S_Data','sram_burst_s.SData')
    sram.entity.bindPort('io_ocp_S_CmdAccept','sram_burst_s.SCmdAccept')
    sram.entity.bindPort('io_ocp_S_DataAccept','sram_burst_s.SDataAccept')
    sram.entity.bindPort('io_ssramBurstRWPins_ramOut_addr','oSRAM_A')
    sram.entity.bindPort('io_ssramBurstRWPins_ramOut_doutEna','sram_out_dout_ena')
    sram.entity.bindPort('io_ssramBurstRWPins_ramOut_nadsc','oSRAM_ADSC_N')
    sram.entity.bindPort('io_ssramBurstRWPins_ramOut_noe','oSRAM_OE_N')
    sram.entity.bindPort('io_ssramBurstRWPins_ramOut_nbwe','oSRAM_WE_N')
    sram.entity.bindPort('io_ssramBurstRWPins_ramOut_nbw','oSRAM_BE_N')
    sram.entity.bindPort('io_ssramBurstRWPins_ramOut_ngw','oSRAM_GW_N')
    sram.entity.bindPort('io_ssramBurstRWPins_ramOut_nce1','oSRAM_CE1_N')
    sram.entity.bindPort('io_ssramBurstRWPins_ramOut_ce2','oSRAM_CE2')
    sram.entity.bindPort('io_ssramBurstRWPins_ramOut_nce3','oSRAM_CE3_N')
    sram.entity.bindPort('io_ssramBurstRWPins_ramOut_nadsp','oSRAM_ADSP_N')
    sram.entity.bindPort('io_ssramBurstRWPins_ramOut_nadv','oSRAM_ADV_N')
    sram.entity.bindPort('io_ssramBurstRWPins_ramOut_dout','sram_out_dout')
    sram.entity.bindPort('io_ssramBurstRWPins_ramIn_din','sram_in_din')

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
    aegean.entity.bindPort('sram_burst_m','sram_burst_m')
    aegean.entity.bindPort('sram_burst_s','sram_burst_s')
