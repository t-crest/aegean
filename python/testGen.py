class TestGen(object):
    """
    The TestGen class handles the generation of a testbench for the Aegean hardware platform
    """
    def __init__(self,p,platform):
        self.p = p
        self.platform = platform
        self.IPCores = list(self.platform)[2]
        self.nodes = list(self.platform)[1]


    def generate(self):
        f = open(self.p.TestFile, 'w')
        f.write('''\
--------------------------------------------------------------------------------
-- Auto generated entity for the aegean_testbench.
--------------------------------------------------------------------------------
library ieee;
library ieee;
library modelsim_lib;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
use modelsim_lib.util.all;
use work.test.all;

entity aegean_testbench is
end entity ; -- aegean_testbench

architecture arch of aegean_testbench is
    signal clk : std_logic;
    signal reset : std_logic;
    signal led : std_logic_vector(8 downto 0);

    signal io_sramPins_ram_out_addr    : std_logic_vector(18 downto 0);
    signal io_sramPins_ram_out_dout_ena: std_logic;
    signal io_sramPins_ram_out_nadsc   : std_logic;
    signal io_sramPins_ram_out_noe     : std_logic;
    signal io_sramPins_ram_out_nbwe    : std_logic;
    signal io_sramPins_ram_out_nbw     : std_logic_vector(3 downto 0);
    signal io_sramPins_ram_out_ngw     : std_logic;
    signal io_sramPins_ram_out_nce1    : std_logic;
    signal io_sramPins_ram_out_ce2     : std_logic;
    signal io_sramPins_ram_out_nce3    : std_logic;
    signal io_sramPins_ram_out_nadsp   : std_logic;
    signal io_sramPins_ram_out_nadv    : std_logic;
    signal io_sramPins_ram_out_dout    : std_logic_vector(31 downto 0);
    signal io_sramPins_ram_in_din      : std_logic_vector(31 downto 0);
    signal io_sramPins_ram_inout_d     : std_logic_vector(31 downto 0);
    signal io_sramPins_ram_in_din_reg  : std_logic_vector(31 downto 0);
    signal pull_down                   : std_logic;

    -- Add signals for uart spy''')
        for p in range(0,len(self.nodes)):
            patmos = self.nodes[p]
            label = patmos.get('id')
            f.write('''
    signal '''+label+'''_uart_tx_reg : std_logic_vector(7 downto 0);
    signal '''+label+'''_uart_tx_status_reg : std_logic_vector(0 downto 0);''')

        f.write('''
    file OUTPUT: TEXT open WRITE_MODE is "STD_OUTPUT";

    constant PERIOD : time := 10 ns;
    constant RESET_TIME : time := 40 ns;

begin
    aegean : entity work.aegean port map (
        clk => clk,
        reset => reset,
        led => led,
        txd => open,
        rxd => '0',

        io_sramPins_ram_out_addr     => io_sramPins_ram_out_addr    ,
        io_sramPins_ram_out_dout_ena => io_sramPins_ram_out_dout_ena,
        io_sramPins_ram_out_nadsc    => io_sramPins_ram_out_nadsc   ,
        io_sramPins_ram_out_noe      => io_sramPins_ram_out_noe     ,
        io_sramPins_ram_out_nbwe     => io_sramPins_ram_out_nbwe    ,
        io_sramPins_ram_out_nbw      => io_sramPins_ram_out_nbw     ,
        io_sramPins_ram_out_ngw      => io_sramPins_ram_out_ngw     ,
        io_sramPins_ram_out_nce1     => io_sramPins_ram_out_nce1    ,
        io_sramPins_ram_out_ce2      => io_sramPins_ram_out_ce2     ,
        io_sramPins_ram_out_nce3     => io_sramPins_ram_out_nce3    ,
        io_sramPins_ram_out_nadsp    => io_sramPins_ram_out_nadsp   ,
        io_sramPins_ram_out_nadv     => io_sramPins_ram_out_nadv    ,
        io_sramPins_ram_out_dout     => io_sramPins_ram_out_dout    ,
        io_sramPins_ram_in_din       => io_sramPins_ram_in_din
        );

    clock_gen(clk,PERIOD);
    reset_gen(reset,RESET_TIME);

    -- Add processes for writing output from each core uart
''')
        for p in range(0,len(self.nodes)):
            patmos = self.nodes[p]
            label = patmos.get('id')
            f.write('''
    '''+label+'''_uart_spy : process
        variable buf: LINE;
        constant CORE_ID : STRING ('''+str(len(label)+2)+''' downto 1):="'''+label.upper()+''': ";
    begin
        init_signal_spy("/aegean_testbench/aegean/'''+label+'''/iocomp/uart/tx_empty","/aegean_testbench/'''+label+'''_uart_tx_status_reg");
        init_signal_spy("/aegean_testbench/aegean/'''+label+'''/iocomp/uart/tx_data","/aegean_testbench/'''+label+'''_uart_tx_reg");
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
        f.write('''
    -- Add uart ticker to increase the UART speed to reduce simulation time
    baud_inc : process
    begin''')
        for p in range(0,len(self.nodes)):
            patmos = self.nodes[p]
            label = patmos.get('id')
            f.write('''
        signal_force("/aegean_testbench/aegean/'''+label+'''/iocomp/uart/tx_baud_tick", "0", 0 ns, freeze, open, 0);''')

        f.write('''
        loop
            wait until rising_edge(clk);''')
        for p in range(0,len(self.nodes)):
            patmos = self.nodes[p]
            label = patmos.get('id')
            f.write('''
            signal_force("/aegean_testbench/aegean/'''+label+'''/iocomp/uart/tx_baud_tick", "1", 0 ns, freeze, open, 0);''')

        f.write('''
            wait until rising_edge(clk);''')
        for p in range(0,len(self.nodes)):
            patmos = self.nodes[p]
            label = patmos.get('id')
            f.write('''
            signal_force("/aegean_testbench/aegean/'''+label+'''/iocomp/uart/tx_baud_tick", "0", 0 ns, freeze, open, 0);''')

        f.write('''
            wait for 3*PERIOD;
        end loop;
    end process ; -- baud_inc
''')
        f.write('''

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
            mem_file_name  => "'''+self.p.MAIN_MEM+'''",

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

end architecture ; -- arch

''')

        f.close()
