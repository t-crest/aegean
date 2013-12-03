from codeGen.Component import Component

def getTest():
    test = Component('aegean_testbench')
    test.addPackage('ieee','std_logic_1164')
    test.addPackage('ieee','numeric_std')
    test.addPackage('std','textio')
    test.addPackage('modelsim_lib','util')
    test.addPackage('work','test')
    declareSignals(test)
    return test

def declareSignals(test):
    test.arch.declSignal('clk','std_logic')
    test.arch.declSignal('reset','std_logic')
    test.arch.declSignal('led','std_logic_vector',9)

    test.arch.declConstant('PERIOD','time',1,'10 ns')
    test.arch.declConstant('RESET_TIME','time',1,'40 ns')

    test.arch.declSignal('io_sramPins_ram_out_addr','std_logic_vector',19)
    test.arch.declSignal('io_sramPins_ram_out_dout_ena','std_logic')
    test.arch.declSignal('io_sramPins_ram_out_nadsc','std_logic')
    test.arch.declSignal('io_sramPins_ram_out_noe','std_logic')
    test.arch.declSignal('io_sramPins_ram_out_nbwe','std_logic')
    test.arch.declSignal('io_sramPins_ram_out_nbw','std_logic_vector',4)
    test.arch.declSignal('io_sramPins_ram_out_ngw','std_logic')
    test.arch.declSignal('io_sramPins_ram_out_nce1','std_logic')
    test.arch.declSignal('io_sramPins_ram_out_ce2','std_logic')
    test.arch.declSignal('io_sramPins_ram_out_nce3','std_logic')
    test.arch.declSignal('io_sramPins_ram_out_nadsp','std_logic')
    test.arch.declSignal('io_sramPins_ram_out_nadv','std_logic')
    test.arch.declSignal('io_sramPins_ram_out_dout','std_logic_vector',32)
    test.arch.declSignal('io_sramPins_ram_in_din','std_logic_vector',32)
    test.arch.declSignal('io_sramPins_ram_inout_d','std_logic_vector',32)
    test.arch.declSignal('io_sramPins_ram_in_din_reg','std_logic_vector',32)
    test.arch.declSignal('pull_down','std_logic')



def writeSignalSpySignals(test,label):
    test.arch.declSignal(label+'_uart_tx_reg','std_logic_vector',8)
    test.arch.declSignal(label+'_uart_tx_status_reg','std_logic_vector(0 downto 0)')


def writeAegeanInst(test):
    test.arch.decl('''
    file OUTPUT: TEXT open WRITE_MODE is "STD_OUTPUT";
''')
    test.arch.addToBody('''

    clock_gen(clk,PERIOD);
    reset_gen(reset,RESET_TIME);
''')

def bindAegean(aegean):
    aegean.entity.bindPort('clk','clk')
    aegean.entity.bindPort('reset','reset')
    aegean.entity.bindPort('led','led')
    aegean.entity.bindPort('txd','open')
    aegean.entity.bindPort('rxd',"'0'")
    aegean.entity.bindPort('io_sramPins_ram_out_addr','io_sramPins_ram_out_addr')
    aegean.entity.bindPort('io_sramPins_ram_out_dout_ena','io_sramPins_ram_out_dout_ena')
    aegean.entity.bindPort('io_sramPins_ram_out_nadsc','io_sramPins_ram_out_nadsc')
    aegean.entity.bindPort('io_sramPins_ram_out_noe','io_sramPins_ram_out_noe')
    aegean.entity.bindPort('io_sramPins_ram_out_nbwe','io_sramPins_ram_out_nbwe')
    aegean.entity.bindPort('io_sramPins_ram_out_nbw','io_sramPins_ram_out_nbw')
    aegean.entity.bindPort('io_sramPins_ram_out_ngw','io_sramPins_ram_out_ngw')
    aegean.entity.bindPort('io_sramPins_ram_out_nce1','io_sramPins_ram_out_nce1')
    aegean.entity.bindPort('io_sramPins_ram_out_ce2','io_sramPins_ram_out_ce2')
    aegean.entity.bindPort('io_sramPins_ram_out_nce3','io_sramPins_ram_out_nce3')
    aegean.entity.bindPort('io_sramPins_ram_out_nadsp','io_sramPins_ram_out_nadsp')
    aegean.entity.bindPort('io_sramPins_ram_out_nadv','io_sramPins_ram_out_nadv')
    aegean.entity.bindPort('io_sramPins_ram_out_dout','io_sramPins_ram_out_dout')
    aegean.entity.bindPort('io_sramPins_ram_in_din','io_sramPins_ram_in_din')

def writeUartSpy(test,label):
    test.arch.addToBody('''
    '''+label+'''_uart_spy : process
        variable buf: LINE;
        constant CORE_ID : STRING ('''+str(len(label)+2)+''' downto 1):="'''+label.upper()+''': ";
    begin
        init_signal_spy("/aegean_testbench/aegean/'''+label+'''/iocomp/Uart/tx_empty","/aegean_testbench/'''+label+'''_uart_tx_status_reg");
        init_signal_spy("/aegean_testbench/aegean/'''+label+'''/iocomp/Uart/tx_data","/aegean_testbench/'''+label+'''_uart_tx_reg");
        write(buf,CORE_ID);
        loop
            wait until falling_edge('''+label+'''_uart_tx_status_reg(0));
            write(buf,character'val(to_integer(unsigned('''+label+'''_uart_tx_reg))));
            --writeline(OUTPUT,buf);
            if to_integer(unsigned('''+label+'''_uart_tx_reg)) = 10 then
                writeline(OUTPUT,buf);
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

def writeUartForce(label,value):
    return '''
            signal_force("/aegean_testbench/aegean/'''+label+'''/iocomp/Uart/tx_baud_tick", "'''+str(value)+'''", 0 ns, freeze, open, 0);'''


def writeBaudIncEnd():
    return '''
            wait for 3*PERIOD;
        end loop;
    end process ; -- baud_inc
'''

def writeSimMem(test,MAIN_MEM):
    test.arch.addToBody('''

    -- capture input from ssram on falling clk edge
    process(clk, reset)
    begin
        if reset='1' then
            io_sramPins_ram_in_din_reg <= (others => '0');
        elsif falling_edge(clk) then
            io_sramPins_ram_in_din_reg <= io_sramPins_ram_inout_d;
        end if;
    end process;

    -- tristate output to ssram
    process(io_sramPins_ram_out_dout_ena, io_sramPins_ram_out_dout)
    begin
        if io_sramPins_ram_out_dout_ena='1' then
            io_sramPins_ram_inout_d <= io_sramPins_ram_out_dout;
        else
            io_sramPins_ram_inout_d <= (others => 'Z');
        end if;
    end process;

    -- input of tristate on positive clk edge
    process(clk)
    begin
        if rising_edge(clk) then
            io_sramPins_ram_in_din <= io_sramPins_ram_in_din_reg;
        end if;
    end process;

    pull_down <= io_sramPins_ram_inout_d(0);

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
            A0 => io_sramPins_ram_out_addr(0),
            A1 => io_sramPins_ram_out_addr(1),
            A2 => io_sramPins_ram_out_addr(2),
            A3 => io_sramPins_ram_out_addr(3),
            A4 => io_sramPins_ram_out_addr(4),
            A5 => io_sramPins_ram_out_addr(5),
            A6 => io_sramPins_ram_out_addr(6),
            A7 => io_sramPins_ram_out_addr(7),
            A8 => io_sramPins_ram_out_addr(8),
            A9 => io_sramPins_ram_out_addr(9),
            A10 => io_sramPins_ram_out_addr(10),
            A11 => io_sramPins_ram_out_addr(11),
            A12 => io_sramPins_ram_out_addr(12),
            A13 => io_sramPins_ram_out_addr(13),
            A14 => io_sramPins_ram_out_addr(14),
            A15 => io_sramPins_ram_out_addr(15),
            A16 => io_sramPins_ram_out_addr(16),
            A17 => io_sramPins_ram_out_addr(17),
            A18 => io_sramPins_ram_out_addr(18),

            DQA0 => io_sramPins_ram_inout_d(0),
            DQA1 => io_sramPins_ram_inout_d(1),
            DQA2 => io_sramPins_ram_inout_d(2),
            DQA3 => io_sramPins_ram_inout_d(3),
            DQA4 => io_sramPins_ram_inout_d(4),
            DQA5 => io_sramPins_ram_inout_d(5),
            DQA6 => io_sramPins_ram_inout_d(6),
            DQA7 => io_sramPins_ram_inout_d(7),
            DPA => pull_down,
            DQB0 => io_sramPins_ram_inout_d(8),
            DQB1 => io_sramPins_ram_inout_d(9),
            DQB2 => io_sramPins_ram_inout_d(10),
            DQB3 => io_sramPins_ram_inout_d(11),
            DQB4 => io_sramPins_ram_inout_d(12),
            DQB5 => io_sramPins_ram_inout_d(13),
            DQB6 => io_sramPins_ram_inout_d(14),
            DQB7 => io_sramPins_ram_inout_d(15),
            DPB => pull_down,
            DQC0 => io_sramPins_ram_inout_d(16),
            DQC1 => io_sramPins_ram_inout_d(17),
            DQC2 => io_sramPins_ram_inout_d(18),
            DQC3 => io_sramPins_ram_inout_d(19),
            DQC4 => io_sramPins_ram_inout_d(20),
            DQC5 => io_sramPins_ram_inout_d(21),
            DQC6 => io_sramPins_ram_inout_d(22),
            DQC7 => io_sramPins_ram_inout_d(23),
            DPC => pull_down,
            DQD0 => io_sramPins_ram_inout_d(24),
            DQD1 => io_sramPins_ram_inout_d(25),
            DQD2 => io_sramPins_ram_inout_d(26),
            DQD3 => io_sramPins_ram_inout_d(27),
            DQD4 => io_sramPins_ram_inout_d(28),
            DQD5 => io_sramPins_ram_inout_d(29),
            DQD6 => io_sramPins_ram_inout_d(30),
            DQD7 => io_sramPins_ram_inout_d(31),
            DPD => pull_down,

            BWANeg => io_sramPins_ram_out_nbw(0),
            BWBNeg => io_sramPins_ram_out_nbw(1),
            BWCNeg => io_sramPins_ram_out_nbw(2),
            BWDNeg => io_sramPins_ram_out_nbw(3),
            GWNeg => io_sramPins_ram_out_ngw,
            BWENeg => io_sramPins_ram_out_nbwe,
            CLK => clk,
            CE1Neg => io_sramPins_ram_out_nce1,
            CE2 => io_sramPins_ram_out_ce2,
            CE3Neg =>  io_sramPins_ram_out_nce3,
            OENeg => io_sramPins_ram_out_noe,
            ADVNeg => io_sramPins_ram_out_nadv,
            ADSPNeg => io_sramPins_ram_out_nadsp,
            ADSCNeg => io_sramPins_ram_out_nadsc,
            MODE => '1',
            ZZ => '0'
            );

''')
