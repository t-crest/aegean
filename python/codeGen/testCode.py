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

def getTest():
    test = Component('aegean_testbench')
    test.addPackage('ieee','std_logic_1164')
    test.addPackage('ieee','numeric_std')
    test.addPackage('std','textio')
    test.addPackage('modelsim_lib','util')
    test.addPackage('work','test')
    test.addPackage('work','ocp')

    return test

def declareSignals(test,sramName):
    test.arch.declSignal('clk','std_logic')

    test.arch.declConstant('PERIOD','time',1,'12.5 ns')
    test.arch.declConstant('RESET_TIME','time',1,'40 ns')

    if sramName == 'Ssram32':
        test.arch.declSignal('oSRAM_A','std_logic_vector',19)
        test.arch.declSignal('oSRAM_ADSC_N','std_logic')
        test.arch.declSignal('oSRAM_OE_N','std_logic')
        test.arch.declSignal('oSRAM_WE_N','std_logic')
        test.arch.declSignal('oSRAM_BE_N','std_logic_vector',4)
        test.arch.declSignal('oSRAM_GW_N','std_logic')
        test.arch.declSignal('oSRAM_CE1_N','std_logic')
        test.arch.declSignal('oSRAM_CE2','std_logic')
        test.arch.declSignal('oSRAM_CE3_N','std_logic')
        test.arch.declSignal('oSRAM_ADSP_N','std_logic')
        test.arch.declSignal('oSRAM_ADV_N','std_logic')
        test.arch.declSignal('SRAM_DQ','std_logic_vector',32)
        test.arch.declSignal('oSRAM_CLK','std_logic')
    elif sramName == 'Ssram16':
        test.arch.declSignal('oSRAM_A','std_logic_vector',20)
        test.arch.declSignal('oSRAM_OE_N','std_logic')
        test.arch.declSignal('oSRAM_WE_N','std_logic')
        test.arch.declSignal('oSRAM_CE_N','std_logic')
        test.arch.declSignal('oSRAM_LB_N','std_logic')
        test.arch.declSignal('oSRAM_UB_N','std_logic')
        test.arch.declSignal('SRAM_DQ','std_logic_vector',16)

    test.arch.declSignal('pull_down','std_logic')
    test.arch.decl('''
    file OUTPUT: TEXT open WRITE_MODE is "STD_OUTPUT";
''')

    test.arch.addToBody('''

    clock_gen(clk,PERIOD);
''')


def writeSignalSpySignals(test,label):
    test.arch.declSignal(label+'_uart_tx_reg','std_logic_vector',8)
    test.arch.declSignal(label+'_uart_tx_status_reg','std_logic_vector(0 downto 0)')

def bindTop(top,sramName):
    top.entity.bindPort('clk','clk')
    if sramName == 'Ssram32':
        top.entity.bindPort('oSRAM_A','oSRAM_A')
        top.entity.bindPort('oSRAM_ADSC_N','oSRAM_ADSC_N')
        top.entity.bindPort('oSRAM_OE_N','oSRAM_OE_N')
        top.entity.bindPort('oSRAM_WE_N','oSRAM_WE_N')
        top.entity.bindPort('oSRAM_BE_N','oSRAM_BE_N')
        top.entity.bindPort('oSRAM_GW_N','oSRAM_GW_N')
        top.entity.bindPort('oSRAM_CE1_N','oSRAM_CE1_N')
        top.entity.bindPort('oSRAM_CE2','oSRAM_CE2')
        top.entity.bindPort('oSRAM_CE3_N','oSRAM_CE3_N')
        top.entity.bindPort('oSRAM_ADSP_N','oSRAM_ADSP_N')
        top.entity.bindPort('oSRAM_ADV_N','oSRAM_ADV_N')
        top.entity.bindPort('SRAM_DQ','SRAM_DQ')
        top.entity.bindPort('oSRAM_CLK','oSRAM_CLK')
    elif sramName == 'Ssram16':
        top.entity.bindPort('oSRAM_A','oSRAM_A')
        top.entity.bindPort('oSRAM_OE_N','oSRAM_OE_N')
        top.entity.bindPort('oSRAM_WE_N','oSRAM_WE_N')
        top.entity.bindPort('oSRAM_CE_N','oSRAM_CE_N')
        top.entity.bindPort('oSRAM_LB_N','oSRAM_LB_N')
        top.entity.bindPort('oSRAM_UB_N','oSRAM_UB_N')
        top.entity.bindPort('SRAM_DQ','SRAM_DQ')


def writeUartSpy(test,label,hwprefix):
    test.arch.addToBody('''
    '''+label+'''_uart_spy : process
        variable buf: LINE;
        constant CORE_ID : STRING ('''+str(len(label)+6)+''' downto 1):="'''+label.upper()+''': at: ";
        variable i : integer := 0;
    begin
        init_signal_spy("/aegean_testbench/top/cmp/'''+label+'''/iocomp/'''+hwprefix+'''Uart/tx_empty","/aegean_testbench/'''+label+'''_uart_tx_status_reg");
        init_signal_spy("/aegean_testbench/top/cmp/'''+label+'''/iocomp/'''+hwprefix+'''Uart/tx_data","/aegean_testbench/'''+label+'''_uart_tx_reg");
        write(buf,CORE_ID);
        loop
            wait until falling_edge('''+label+'''_uart_tx_status_reg(0));
            if i = 0 then
                write(buf,time'image(NOW) & " : ");
                --write(buf,real'image(real(NOW/time'val(1000000))/1000.0) & " us : ");
            end if;
            write(buf,character'val(to_integer(unsigned('''+label+'''_uart_tx_reg))));
            i := i + 1;
            --writeline(OUTPUT,buf);
            if to_integer(unsigned('''+label+'''_uart_tx_reg)) = 10 then
                writeline(OUTPUT,buf);
                i := 0;
                write(buf,CORE_ID);
            end if;
        end loop;
    end process ; -- '''+label+'''_uart_spy

''')

def writeBaudIncBegin():
    return '''
    -- Add uart ticker to increase the UART speed to reduce simulation time
    baud_inc : process
    begin
        loop'''

def writeWait():
    return '''
            wait until rising_edge(clk);'''

def writeUartForce(label,value,hwprefix):
    return '''
            signal_force("/aegean_testbench/top/cmp/'''+label+'''/iocomp/'''+hwprefix+'''Uart/tx_baud_tick", "'''+str(value)+'''", 0 ns, freeze, open, 0);'''


def writeBaudIncEnd():
    return '''
            wait for 3*PERIOD;
        end loop;
    end process ; -- baud_inc
'''

def writeSimMem(test,sramName,MAIN_MEM):
    if sramName == 'Ssram16':
        test.arch.addToBody('''
    main_mem : entity work.cy7c10612dv33 port map(
        CE_b  => oSRAM_CE_N,
        WE_b  => oSRAM_WE_N,
        OE_b  => oSRAM_OE_N,
        BHE_b => oSRAM_UB_N,
        BLE_b => oSRAM_LB_N,
        A     => oSRAM_A,
        DQ    => SRAM_DQ);
''')
    elif sramName == 'Ssram32':
        test.arch.addToBody('''

    pull_down <= SRAM_DQ(0);

    main_mem: entity work.memory
        generic map (
            TimingChecksOn => true,
            mem_file_name  => "'''+MAIN_MEM+'''",

            tperiod_CLK_posedge => 5.0 ns,
            tpw_CLK_posedge => 2.0 ns,
            tpw_CLK_negedge => 2.0 ns,

            tpd_CLK_DQA0 => (others => 3.1 ns),
            tpd_OENeg_DQA0 => (others => 3.1 ns),

            tsetup_A0_CLK => 1.4 ns,
            tsetup_DQA0_CLK => 1.4 ns,
            tsetup_ADVNeg_CLK => 1.4 ns,
            tsetup_ADSCNeg_CLK => 1.4 ns,
            tsetup_CE2_CLK => 1.4 ns,
            tsetup_BWANeg_CLK => 1.4 ns,

            thold_A0_CLK => 0.4 ns,
            thold_DQA0_CLK => 0.4 ns,
            thold_ADVNeg_CLK => 0.4 ns,
            thold_ADSCNeg_CLK => 0.4 ns,
            thold_CE2_CLK => 0.4 ns,
            thold_BWANeg_CLK => 0.4 ns,

            tipd_A0 => (3 ns, 3 ns),
            tipd_A1 => (3 ns, 3 ns),
            tipd_A2 => (3 ns, 3 ns),
            tipd_A3 => (3 ns, 3 ns),
            tipd_A4 => (3 ns, 3 ns),
            tipd_A5 => (3 ns, 3 ns),
            tipd_A6 => (3 ns, 3 ns),
            tipd_A7 => (3 ns, 3 ns),
            tipd_A8 => (3 ns, 3 ns),
            tipd_A9 => (3 ns, 3 ns),
            tipd_A10 => (3 ns, 3 ns),
            tipd_A11 => (3 ns, 3 ns),
            tipd_A12 => (3 ns, 3 ns),
            tipd_A13 => (3 ns, 3 ns),
            tipd_A14 => (3 ns, 3 ns),
            tipd_A15 => (3 ns, 3 ns),
            tipd_A16 => (3 ns, 3 ns),
            tipd_A17 => (3 ns, 3 ns),
            tipd_A18 => (3 ns, 3 ns),

            tipd_DQA0 => (3 ns, 3 ns),
            tipd_DQA1 => (3 ns, 3 ns),
            tipd_DQA2 => (3 ns, 3 ns),
            tipd_DQA3 => (3 ns, 3 ns),
            tipd_DQA4 => (3 ns, 3 ns),
            tipd_DQA5 => (3 ns, 3 ns),
            tipd_DQA6 => (3 ns, 3 ns),
            tipd_DQA7 => (3 ns, 3 ns),
            tipd_DPA  => (3 ns, 3 ns),
            tipd_DQB0 => (3 ns, 3 ns),
            tipd_DQB1 => (3 ns, 3 ns),
            tipd_DQB2 => (3 ns, 3 ns),
            tipd_DQB3 => (3 ns, 3 ns),
            tipd_DQB4 => (3 ns, 3 ns),
            tipd_DQB5 => (3 ns, 3 ns),
            tipd_DQB6 => (3 ns, 3 ns),
            tipd_DQB7 => (3 ns, 3 ns),
            tipd_DPB  => (3 ns, 3 ns),
            tipd_DQC0 => (3 ns, 3 ns),
            tipd_DQC1 => (3 ns, 3 ns),
            tipd_DQC2 => (3 ns, 3 ns),
            tipd_DQC3 => (3 ns, 3 ns),
            tipd_DQC4 => (3 ns, 3 ns),
            tipd_DQC5 => (3 ns, 3 ns),
            tipd_DQC6 => (3 ns, 3 ns),
            tipd_DQC7 => (3 ns, 3 ns),
            tipd_DPC  => (3 ns, 3 ns),
            tipd_DQD0 => (3 ns, 3 ns),
            tipd_DQD1 => (3 ns, 3 ns),
            tipd_DQD2 => (3 ns, 3 ns),
            tipd_DQD3 => (3 ns, 3 ns),
            tipd_DQD4 => (3 ns, 3 ns),
            tipd_DQD5 => (3 ns, 3 ns),
            tipd_DQD6 => (3 ns, 3 ns),
            tipd_DQD7 => (3 ns, 3 ns),
            tipd_DPD  => (3 ns, 3 ns),

            tipd_BWANeg  => (3 ns, 3 ns),
            tipd_BWBNeg  => (3 ns, 3 ns),
            tipd_BWCNeg  => (3 ns, 3 ns),
            tipd_BWDNeg  => (3 ns, 3 ns),
            tipd_GWNeg   => (3 ns, 3 ns),
            tipd_BWENeg  => (3 ns, 3 ns),
            tipd_CLK     => (3 ns, 3 ns),
            tipd_CE1Neg  => (3 ns, 3 ns),
            tipd_CE2     => (3 ns, 3 ns),
            tipd_CE3Neg  => (3 ns, 3 ns),
            tipd_OENeg   => (3 ns, 3 ns),
            tipd_ADVNeg  => (3 ns, 3 ns),
            tipd_ADSPNeg => (3 ns, 3 ns),
            tipd_ADSCNeg => (3 ns, 3 ns)
            )
        port map (
            A0 => oSRAM_A(0),
            A1 => oSRAM_A(1),
            A2 => oSRAM_A(2),
            A3 => oSRAM_A(3),
            A4 => oSRAM_A(4),
            A5 => oSRAM_A(5),
            A6 => oSRAM_A(6),
            A7 => oSRAM_A(7),
            A8 => oSRAM_A(8),
            A9 => oSRAM_A(9),
            A10 => oSRAM_A(10),
            A11 => oSRAM_A(11),
            A12 => oSRAM_A(12),
            A13 => oSRAM_A(13),
            A14 => oSRAM_A(14),
            A15 => oSRAM_A(15),
            A16 => oSRAM_A(16),
            A17 => oSRAM_A(17),
            A18 => oSRAM_A(18),

            DQA0 => SRAM_DQ(0),
            DQA1 => SRAM_DQ(1),
            DQA2 => SRAM_DQ(2),
            DQA3 => SRAM_DQ(3),
            DQA4 => SRAM_DQ(4),
            DQA5 => SRAM_DQ(5),
            DQA6 => SRAM_DQ(6),
            DQA7 => SRAM_DQ(7),
            DPA => pull_down,
            DQB0 => SRAM_DQ(8),
            DQB1 => SRAM_DQ(9),
            DQB2 => SRAM_DQ(10),
            DQB3 => SRAM_DQ(11),
            DQB4 => SRAM_DQ(12),
            DQB5 => SRAM_DQ(13),
            DQB6 => SRAM_DQ(14),
            DQB7 => SRAM_DQ(15),
            DPB => pull_down,
            DQC0 => SRAM_DQ(16),
            DQC1 => SRAM_DQ(17),
            DQC2 => SRAM_DQ(18),
            DQC3 => SRAM_DQ(19),
            DQC4 => SRAM_DQ(20),
            DQC5 => SRAM_DQ(21),
            DQC6 => SRAM_DQ(22),
            DQC7 => SRAM_DQ(23),
            DPC => pull_down,
            DQD0 => SRAM_DQ(24),
            DQD1 => SRAM_DQ(25),
            DQD2 => SRAM_DQ(26),
            DQD3 => SRAM_DQ(27),
            DQD4 => SRAM_DQ(28),
            DQD5 => SRAM_DQ(29),
            DQD6 => SRAM_DQ(30),
            DQD7 => SRAM_DQ(31),
            DPD => pull_down,

            BWANeg => oSRAM_BE_N(0),
            BWBNeg => oSRAM_BE_N(1),
            BWCNeg => oSRAM_BE_N(2),
            BWDNeg => oSRAM_BE_N(3),
            GWNeg => oSRAM_GW_N,
            BWENeg => oSRAM_WE_N,
            CLK => oSRAM_CLK,
            CE1Neg => oSRAM_CE1_N,
            CE2 => oSRAM_CE2,
            CE3Neg =>  oSRAM_CE3_N,
            OENeg => oSRAM_OE_N,
            ADVNeg => oSRAM_ADV_N,
            ADSPNeg => oSRAM_ADSP_N,
            ADSCNeg => oSRAM_ADSC_N,
            MODE => '1',
            ZZ => '0'
            );

''')
