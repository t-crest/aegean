
library work;
use work.test.all;
use work.ocp.all;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library std;
use std.textio.all;

library modelsim_lib;
use modelsim_lib.util.all;

entity aegean_testbench is

end entity;

architecture struct of aegean_testbench is
	signal pat0_uart_tx_reg : std_logic_vector(7 downto 0);
	signal pat0_uart_tx_status_reg : std_logic;
	signal pat1_uart_tx_reg : std_logic_vector(7 downto 0);
	signal pat1_uart_tx_status_reg : std_logic;
	signal pat2_uart_tx_reg : std_logic_vector(7 downto 0);
	signal pat2_uart_tx_status_reg : std_logic;
	signal pat3_uart_tx_reg : std_logic_vector(7 downto 0);
	signal pat3_uart_tx_status_reg : std_logic;
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
        init_signal_spy("/aegean_testbench/top/cmp/pat0/iocomp/ml605ocmUart/txQueue/io_enq_valid","/aegean_testbench/pat0_uart_tx_status_reg");
        init_signal_spy("/aegean_testbench/top/cmp/pat0/iocomp/ml605ocmUart/txQueue/io_enq_bits","/aegean_testbench/pat0_uart_tx_reg");
        write(buf,CORE_ID);
        loop
            wait until rising_edge(pat0_uart_tx_status_reg);
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


    pat1_uart_spy : process
        variable buf: LINE;
        constant CORE_ID : STRING (10 downto 1):="PAT1: at: ";
        variable i : integer := 0;
    begin
        init_signal_spy("/aegean_testbench/top/cmp/pat1/iocomp/ml605ocsUart/txQueue/io_enq_valid","/aegean_testbench/pat1_uart_tx_status_reg");
        init_signal_spy("/aegean_testbench/top/cmp/pat1/iocomp/ml605ocsUart/txQueue/io_enq_bits","/aegean_testbench/pat1_uart_tx_reg");
        write(buf,CORE_ID);
        loop
            wait until rising_edge(pat1_uart_tx_status_reg);
            if i = 0 then
                write(buf,time'image(NOW) & " : ");
                --write(buf,real'image(real(NOW/time'val(1000000))/1000.0) & " us : ");
            end if;
            write(buf,character'val(to_integer(unsigned(pat1_uart_tx_reg))));
            i := i + 1;
            --writeline(OUTPUT,buf);
            if to_integer(unsigned(pat1_uart_tx_reg)) = 10 then
                writeline(OUTPUT,buf);
                i := 0;
                write(buf,CORE_ID);
            end if;
        end loop;
    end process ; -- pat1_uart_spy


    pat2_uart_spy : process
        variable buf: LINE;
        constant CORE_ID : STRING (10 downto 1):="PAT2: at: ";
        variable i : integer := 0;
    begin
        init_signal_spy("/aegean_testbench/top/cmp/pat2/iocomp/ml605ocsUart/txQueue/io_enq_valid","/aegean_testbench/pat2_uart_tx_status_reg");
        init_signal_spy("/aegean_testbench/top/cmp/pat2/iocomp/ml605ocsUart/txQueue/io_enq_bits","/aegean_testbench/pat2_uart_tx_reg");
        write(buf,CORE_ID);
        loop
            wait until rising_edge(pat2_uart_tx_status_reg);
            if i = 0 then
                write(buf,time'image(NOW) & " : ");
                --write(buf,real'image(real(NOW/time'val(1000000))/1000.0) & " us : ");
            end if;
            write(buf,character'val(to_integer(unsigned(pat2_uart_tx_reg))));
            i := i + 1;
            --writeline(OUTPUT,buf);
            if to_integer(unsigned(pat2_uart_tx_reg)) = 10 then
                writeline(OUTPUT,buf);
                i := 0;
                write(buf,CORE_ID);
            end if;
        end loop;
    end process ; -- pat2_uart_spy


    pat3_uart_spy : process
        variable buf: LINE;
        constant CORE_ID : STRING (10 downto 1):="PAT3: at: ";
        variable i : integer := 0;
    begin
        init_signal_spy("/aegean_testbench/top/cmp/pat3/iocomp/ml605ocsUart/txQueue/io_enq_valid","/aegean_testbench/pat3_uart_tx_status_reg");
        init_signal_spy("/aegean_testbench/top/cmp/pat3/iocomp/ml605ocsUart/txQueue/io_enq_bits","/aegean_testbench/pat3_uart_tx_reg");
        write(buf,CORE_ID);
        loop
            wait until rising_edge(pat3_uart_tx_status_reg);
            if i = 0 then
                write(buf,time'image(NOW) & " : ");
                --write(buf,real'image(real(NOW/time'val(1000000))/1000.0) & " us : ");
            end if;
            write(buf,character'val(to_integer(unsigned(pat3_uart_tx_reg))));
            i := i + 1;
            --writeline(OUTPUT,buf);
            if to_integer(unsigned(pat3_uart_tx_reg)) = 10 then
                writeline(OUTPUT,buf);
                i := 0;
                write(buf,CORE_ID);
            end if;
        end loop;
    end process ; -- pat3_uart_spy


    -- Add uart ticker to increase the UART speed to reduce simulation time
    baud_inc : process
    begin
        loop
            wait until rising_edge(clk);
            signal_force("/aegean_testbench/top/cmp/pat0/iocomp/ml605ocmUart/tx_baud_tick_0_5808", "1", 0 ns, freeze, open, 0);
            --signal_force("/aegean_testbench/top/cmp/pat1/iocomp/ml605ocsUart/tx_baud_tick", "1", 0 ns, freeze, open, 0);
            --signal_force("/aegean_testbench/top/cmp/pat2/iocomp/ml605ocsUart/tx_baud_tick", "1", 0 ns, freeze, open, 0);
            --signal_force("/aegean_testbench/top/cmp/pat3/iocomp/ml605ocsUart/tx_baud_tick", "1", 0 ns, freeze, open, 0);
            wait until rising_edge(clk);
            signal_force("/aegean_testbench/top/cmp/pat0/iocomp/ml605ocmUart/tx_baud_tick_0_5808", "0", 0 ns, freeze, open, 0);
            --signal_force("/aegean_testbench/top/cmp/pat1/iocomp/ml605ocsUart/tx_baud_tick", "0", 0 ns, freeze, open, 0);
            --signal_force("/aegean_testbench/top/cmp/pat2/iocomp/ml605ocsUart/tx_baud_tick", "0", 0 ns, freeze, open, 0);
            --signal_force("/aegean_testbench/top/cmp/pat3/iocomp/ml605ocsUart/tx_baud_tick", "0", 0 ns, freeze, open, 0);
            wait for 3*PERIOD;
        end loop;
    end process ; -- baud_inc

end struct;
