#! /usr/bin/env python3
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
from codeGen import ocp

def getTop():
    top = Component('aegean_top')
    top.addPackage('ieee','std_logic_1164')
    top.addPackage('ieee','numeric_std')
    top.addPackage('work','config')
    top.addPackage('work','ocp')

    return top


def bindSram(sram,name,ocpMSignal,ocpSSignal):
    sram.entity.bindPort('clk','clk_int')
    sram.entity.bindPort('reset','int_res')
    ocp.bindPort(sram,'OcpBurst',ocpMSignal,ocpSSignal)

    if name == 'SSRam32Ctrl':
        sram.entity.bindPort('io_sSRam32CtrlPins_ramOut_addr','oSRAM_A')
        sram.entity.bindPort('io_sSRam32CtrlPins_ramOut_doutEna','sram_out_dout_ena')
        sram.entity.bindPort('io_sSRam32CtrlPins_ramOut_nadsc','oSRAM_ADSC_N')
        sram.entity.bindPort('io_sSRam32CtrlPins_ramOut_noe','oSRAM_OE_N')
        sram.entity.bindPort('io_sSRam32CtrlPins_ramOut_nbwe','oSRAM_WE_N')
        sram.entity.bindPort('io_sSRam32CtrlPins_ramOut_nbw','oSRAM_BE_N')
        sram.entity.bindPort('io_sSRam32CtrlPins_ramOut_ngw','oSRAM_GW_N')
        sram.entity.bindPort('io_sSRam32CtrlPins_ramOut_nce1','oSRAM_CE1_N')
        sram.entity.bindPort('io_sSRam32CtrlPins_ramOut_ce2','oSRAM_CE2')
        sram.entity.bindPort('io_sSRam32CtrlPins_ramOut_nce3','oSRAM_CE3_N')
        sram.entity.bindPort('io_sSRam32CtrlPins_ramOut_nadsp','oSRAM_ADSP_N')
        sram.entity.bindPort('io_sSRam32CtrlPins_ramOut_nadv','oSRAM_ADV_N')
        sram.entity.bindPort('io_sSRam32CtrlPins_ramOut_dout','sram_out_dout')
        sram.entity.bindPort('io_sSRam32CtrlPins_ramIn_din','sram_in_din')
    elif name == 'SRamCtrl':
        sram.entity.bindPort('io_sRamCtrlPins_ramOut_addr','oSRAM_A')
        sram.entity.bindPort('io_sRamCtrlPins_ramOut_doutEna','sram_out_dout_ena')
        sram.entity.bindPort('io_sRamCtrlPins_ramOut_noe','oSRAM_OE_N')
        sram.entity.bindPort('io_sRamCtrlPins_ramOut_nwe','oSRAM_WE_N')
        sram.entity.bindPort('io_sRamCtrlPins_ramOut_nce','oSRAM_CE_N')
        sram.entity.bindPort('io_sRamCtrlPins_ramOut_nlb','oSRAM_LB_N')
        sram.entity.bindPort('io_sRamCtrlPins_ramOut_nub','oSRAM_UB_N')
        sram.entity.bindPort('io_sRamCtrlPins_ramOut_dout','sram_out_dout')
        sram.entity.bindPort('io_sRamCtrlPins_ramIn_din','sram_in_din')
    elif name == 'OCRamCtrl':
        pass
    else:
        raise SystemError(__file__ +': Error: SramEntity "'+name+'" not supported.')





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

def pll(top,vendor,clkPin):
    if vendor == 'Altera':
        top.arch.addToBody('''
    pll_inst : entity work.pll generic map(
            multiply_by => pll_mult,
            divide_by   => pll_div
        )
        port map(
            inclk0 => clk,
            c0     => clk_int,
            c1     => '''+clkPin+'''
        );
''')
    elif vendor == 'Xilinx':
        top.arch.addToBody('''
    clk_int <= clk;
''')
    else:
        raise SystemExit(__file__ +': Error: Unsupported vendor: ' + vendor)

def reset(top):
    top.arch.addToBody('''
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

def writeTriState(top,name,sram,dataSig):
    if sram == 'SSRam32Ctrl':
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
    elif sram == 'SRamCtrl':
        top.arch.addToBody('''
    '''+name+'''_in_din <= '''+dataSig+''';

    -- tristate output to '''+name+'''
    process('''+name+'''_out_dout_ena, '''+name+'''_out_dout)
    begin
        if '''+name+'''_out_dout_ena='1' then
            '''+dataSig+''' <= '''+name+'''_out_dout;
        else
            '''+dataSig+''' <= (others => 'Z');
        end if;
    end process;
''')


def bindAegean(aegean,nodes=0):
    aegean.entity.bindPort('clk','clk_int')
    aegean.entity.bindPort('reset','int_res')
    aegean.entity.bindPort('txd0','oUart0Pins_txd')
    aegean.entity.bindPort('rxd0','iUart0Pins_rxd')
    for p in range(0,nodes):
        aegean.entity.bindPort('led' + str(p),'oLed' + str(p) + 'Pins_led')
    aegean.entity.bindPort('sram_burst_m','sram_burst_m')
    aegean.entity.bindPort('sram_burst_s','sram_burst_s')
