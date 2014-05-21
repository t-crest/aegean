
library std;
use std.textio.all;

library modelsim_lib;
use modelsim_lib.util.all;

library work;
use work.test.all;
use work.ocp.all;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity aegean_testbench is

end entity;

architecture struct of aegean_testbench is
	signal pat0_uart_tx_reg : std_logic_vector(7 downto 0);
	signal pat0_uart_tx_status_reg : std_logic;
	signal pat1_uart_tx_reg : std_logic_vector(7 downto 0);
	signal pat1_uart_tx_status_reg : std_logic_vector(0 downto 0);
	signal pat2_uart_tx_reg : std_logic_vector(7 downto 0);
	signal pat2_uart_tx_status_reg : std_logic_vector(0 downto 0);
	signal pat3_uart_tx_reg : std_logic_vector(7 downto 0);
	signal pat3_uart_tx_status_reg : std_logic_vector(0 downto 0);
	signal clk : std_logic;
	constant PERIOD : time := 12.5 ns;
	constant RESET_TIME : time := 40 ns;
	signal pull_down : std_logic;

    file OUTPUT: TEXT open WRITE_MODE is "STD_OUTPUT";

begin


    clock_gen(clk,PERIOD);

	top : entity work.aegean_top port map(
		clk	=>	clk,
		iUartPins_rxd	=>	'0',
		oUartPins_txd	=>	open,
		oLedPins_led	=>	open	);

    pat0_uart_spy : process
        variable buf: LINE;
        constant CORE_ID : STRING (10 downto 1):="PAT0: at: ";
        variable i : integer := 0;
    begin
        init_signal_spy("/aegean_testbench/top/cmp/pat0/iocomp/ml605ocmUart/tx_empty_0/O","/aegean_testbench/pat0_uart_tx_status_reg");
        init_signal_spy("/aegean_testbench/top/cmp/pat0/iocomp/ml605ocmUart/tx_data_0/O","/aegean_testbench/pat0_uart_tx_reg(0)");
        init_signal_spy("/aegean_testbench/top/cmp/pat0/iocomp/ml605ocmUart/tx_data_1/O","/aegean_testbench/pat0_uart_tx_reg(1)");
        init_signal_spy("/aegean_testbench/top/cmp/pat0/iocomp/ml605ocmUart/tx_data_2/O","/aegean_testbench/pat0_uart_tx_reg(2)");
        init_signal_spy("/aegean_testbench/top/cmp/pat0/iocomp/ml605ocmUart/tx_data_3/O","/aegean_testbench/pat0_uart_tx_reg(3)");
        init_signal_spy("/aegean_testbench/top/cmp/pat0/iocomp/ml605ocmUart/tx_data_4/O","/aegean_testbench/pat0_uart_tx_reg(4)");
        init_signal_spy("/aegean_testbench/top/cmp/pat0/iocomp/ml605ocmUart/tx_data_5/O","/aegean_testbench/pat0_uart_tx_reg(5)");
        init_signal_spy("/aegean_testbench/top/cmp/pat0/iocomp/ml605ocmUart/tx_data_6/O","/aegean_testbench/pat0_uart_tx_reg(6)");
        init_signal_spy("/aegean_testbench/top/cmp/pat0/iocomp/ml605ocmUart/tx_data_7/O","/aegean_testbench/pat0_uart_tx_reg(7)");
        write(buf,CORE_ID);
        loop
            wait until falling_edge(pat0_uart_tx_status_reg);
            if i = 0 then
                write(buf,time'image(NOW) & " : ");
                --write(buf,real'image(real(NOW/time'val(1000000))/1000.0) & " us : ");
            end if;
            write(buf,character'val(to_integer(unsigned(pat0_uart_tx_reg))));
            i := i + 1;
            --writeline(OUTPUT,buf);
            if to_integer(unsigned(pat0_uart_tx_reg)) = 10 then
                writeline(OUTPUT,buf);
                i := 0;
                write(buf,CORE_ID);
            end if;
        end loop;
    end process ; -- pat0_uart_spy





    -- Add uart ticker to increase the UART speed to reduce simulation time
    baud_inc : process
    begin
        loop
            wait until rising_edge(clk);
            signal_force("/aegean_testbench/top/cmp/pat0/iocomp/ml605ocmUart/tx_baud_tick_0/O", "1", 0 ns, freeze, open, 0);
            wait until rising_edge(clk);
            signal_force("/aegean_testbench/top/cmp/pat0/iocomp/ml605ocmUart/tx_baud_tick_0/O", "0", 0 ns, freeze, open, 0);
            wait for 3*PERIOD;
        end loop;
    end process ; -- baud_inc

end struct;
