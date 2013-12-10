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

    signal core0_uart_tx_reg : std_logic_vector(7 downto 0);
    signal core0_uart_tx_status_reg : std_logic_vector(0 downto 0);
    signal core1_uart_tx_reg : std_logic_vector(7 downto 0);
    signal core1_uart_tx_status_reg : std_logic_vector(0 downto 0);
    signal core2_uart_tx_reg : std_logic_vector(7 downto 0);
    signal core2_uart_tx_status_reg : std_logic_vector(0 downto 0);
    signal core3_uart_tx_reg : std_logic_vector(7 downto 0);
    signal core3_uart_tx_status_reg : std_logic_vector(0 downto 0);

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

    core0_uart_spy : process
        variable buf: LINE;
        constant CORE_ID : STRING (7 downto 1):="Core0: ";
    begin
        init_signal_spy("/aegean_testbench/aegean/pat0/iocomp/uart/tx_empty","/aegean_testbench/core0_uart_tx_status_reg");
        init_signal_spy("/aegean_testbench/aegean/pat0/iocomp/uart/tx_data","/aegean_testbench/core0_uart_tx_reg");
        write(buf,CORE_ID);
        loop
            wait until falling_edge(core0_uart_tx_status_reg(0));
            write(buf,character'val(to_integer(unsigned(core0_uart_tx_reg))));
            --writeline(OUTPUT,buf);
            if to_integer(unsigned(core0_uart_tx_reg)) = 10 then
                writeline(OUTPUT,buf);
                write(buf,CORE_ID);
            end if;
        end loop;
    end process ; -- core0_uart_spy

    core1_uart_spy : process
        variable buf: LINE;
        constant CORE_ID : STRING (7 downto 1):="Core1: ";
    begin
        init_signal_spy("/aegean_testbench/aegean/pat1/iocomp/uart/tx_empty","/aegean_testbench/core1_uart_tx_status_reg");
        init_signal_spy("/aegean_testbench/aegean/pat1/iocomp/uart/tx_data","/aegean_testbench/core1_uart_tx_reg");
        write(buf,CORE_ID);
        loop
            wait until falling_edge(core1_uart_tx_status_reg(0));
            write(buf,character'val(to_integer(unsigned(core1_uart_tx_reg))));
            --writeline(OUTPUT,buf);
            if to_integer(unsigned(core1_uart_tx_reg)) = 10 then
                writeline(OUTPUT,buf);
                write(buf,CORE_ID);
            end if;
        end loop;
    end process ; -- core1_uart_spy

    core2_uart_spy : process
        variable buf: LINE;
        constant CORE_ID : STRING (7 downto 1):="Core2: ";
    begin
        init_signal_spy("/aegean_testbench/aegean/pat2/iocomp/uart/tx_empty","/aegean_testbench/core2_uart_tx_status_reg");
        init_signal_spy("/aegean_testbench/aegean/pat2/iocomp/uart/tx_data","/aegean_testbench/core2_uart_tx_reg");
        write(buf,CORE_ID);
        loop
            wait until falling_edge(core2_uart_tx_status_reg(0));
            write(buf,character'val(to_integer(unsigned(core2_uart_tx_reg))));
            --writeline(OUTPUT,buf);
            if to_integer(unsigned(core2_uart_tx_reg)) = 10 then
                writeline(OUTPUT,buf);
                write(buf,CORE_ID);
            end if;
        end loop;
    end process ; -- core2_uart_spy

    core3_uart_spy : process
        variable buf: LINE;
        constant CORE_ID : STRING (7 downto 1):="Core3: ";
    begin
        init_signal_spy("/aegean_testbench/aegean/pat3/iocomp/uart/tx_empty","/aegean_testbench/core3_uart_tx_status_reg");
        init_signal_spy("/aegean_testbench/aegean/pat3/iocomp/uart/tx_data","/aegean_testbench/core3_uart_tx_reg");
        write(buf,CORE_ID);
        loop
            wait until falling_edge(core3_uart_tx_status_reg(0));
            write(buf,character'val(to_integer(unsigned(core3_uart_tx_reg))));
            --writeline(OUTPUT,buf);
            if to_integer(unsigned(core3_uart_tx_reg)) = 10 then
                writeline(OUTPUT,buf);
                write(buf,CORE_ID);
            end if;
        end loop;
    end process ; -- core3_uart_spy


    baud_inc : process
    begin
        signal_force("/aegean_testbench/aegean/pat0/iocomp/uart/tx_baud_tick", "0", 0 ns, freeze, open, 0);
        signal_force("/aegean_testbench/aegean/pat1/iocomp/uart/tx_baud_tick", "0", 0 ns, freeze, open, 0);
        signal_force("/aegean_testbench/aegean/pat2/iocomp/uart/tx_baud_tick", "0", 0 ns, freeze, open, 0);
        signal_force("/aegean_testbench/aegean/pat3/iocomp/uart/tx_baud_tick", "0", 0 ns, freeze, open, 0);
        loop
            wait until rising_edge(clk);
            signal_force("/aegean_testbench/aegean/pat0/iocomp/uart/tx_baud_tick", "1", 0 ns, freeze, open, 0);
            signal_force("/aegean_testbench/aegean/pat1/iocomp/uart/tx_baud_tick", "1", 0 ns, freeze, open, 0);
            signal_force("/aegean_testbench/aegean/pat2/iocomp/uart/tx_baud_tick", "1", 0 ns, freeze, open, 0);
            signal_force("/aegean_testbench/aegean/pat3/iocomp/uart/tx_baud_tick", "1", 0 ns, freeze, open, 0);
            wait until rising_edge(clk);
            signal_force("/aegean_testbench/aegean/pat0/iocomp/uart/tx_baud_tick", "0", 0 ns, freeze, open, 0);
            signal_force("/aegean_testbench/aegean/pat1/iocomp/uart/tx_baud_tick", "0", 0 ns, freeze, open, 0);
            signal_force("/aegean_testbench/aegean/pat2/iocomp/uart/tx_baud_tick", "0", 0 ns, freeze, open, 0);
            signal_force("/aegean_testbench/aegean/pat3/iocomp/uart/tx_baud_tick", "0", 0 ns, freeze, open, 0);
            wait for 3*PERIOD;
        end loop;
    end process ; -- baud_inc

end architecture ; -- arch
