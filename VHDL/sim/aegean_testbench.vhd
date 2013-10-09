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
    signal txd, rxd : std_logic;

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

    signal uart_tx_reg : std_logic_vector(7 downto 0);
    signal uart_tx_status_reg : std_logic_vector(0 downto 0);

    file OUTPUT: TEXT open WRITE_MODE is "STD_OUTPUT";


begin
    aegean : entity work.aegean port map (
        clk => clk,
        reset => reset,
        led => led,
        txd => txd,
        rxd => rxd,

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

    clock_gen(clk,20 ns);
    reset_gen(reset,40 ns);

    uart_spy : process
        variable buf: LINE;
    begin
        init_signal_spy("/aegean_testbench/aegean/patmoss(0)/l0/patmos_p/iocomp/uart/tx_empty","/aegean_testbench/uart_tx_status_reg");
        init_signal_spy("/aegean_testbench/aegean/patmoss(0)/l0/patmos_p/iocomp/uart/tx_data","/aegean_testbench/uart_tx_reg");
--      init_signal_spy("/aegean_testbench/aegean/patmoss(0)/l0/patmos_p/InOut/UART/rx_empty","/aegean_testbench/uart_rx_status_reg");
--      init_signal_spy("/aegean_testbench/aegean/patmoss(0)/l0/patmos_p/InOut/UART/rx_data","/aegean_testbench/uart_rx_reg");

        loop
            wait until falling_edge(uart_tx_status_reg(0));
            write(buf,character'val(to_integer(unsigned(uart_tx_reg))));
            writeline(OUTPUT,buf);
        end loop;

    end process ; -- uart_spy

   -- uart : process
   -- begin
   --     wait for 2 ns;
   --     if not <<signal .aegean_testbench.aegean.reset : std_logic>> then
   --         report "2008 support" severity failure;
   --     end if ;
   --     wait;
   -- end process ; -- uart

end architecture ; -- arch
