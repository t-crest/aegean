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

end architecture ; -- arch

''')

        f.close()
