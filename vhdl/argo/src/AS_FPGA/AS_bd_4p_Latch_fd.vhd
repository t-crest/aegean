-- -----------------------------------------------------------------------------
--  4-phase bundled-data latch
--             
--  Developer  :  Mikkel Stensgaard  -- mikkel@stensgaard.org
--                Student: s001434
--                DTU, Technical University of Denmark
--              
--  Initial:      Intitial work by
--                   Knud Hansen  -- s020922@student.dtu.dk
--                   Guillaume Saoutieff  -- s021368@student.dtu.dk
--
--  Notes      :  The latch is actually an edge-triggered flip-flop
--                for FPGA implementation, it does not consume more resources
--
--  Revision   :  1.0    18 June 2004     Initial version--             :
-- -----------------------------------------------------------------------------

LIBRARY IEEE;
USE IEEE.std_logic_1164.ALL;
USE IEEE.std_logic_arith.ALL;

use work.AS_FPGA.all;

entity AS_bd_4p_Latch_fd is
  generic (width        : positive := 8;
           reset_status : bit := '0';
           reset_value  : natural := 0;
           delay        : natural := 0);
  port    (ack_out: in  std_logic;
           req_in:  in  std_logic;
           dat_in:  in  std_logic_vector((width-1) downto 0);
           reset:   in  std_logic;
           ack_in : out std_logic;
           req_out: out std_logic;
           dat_out: out std_logic_vector((width-1) downto 0));
end entity;

-- -----------------------------------------------------------------------------


ARCHITECTURE rtl OF AS_bd_4p_Latch_fd IS

-- Latch Controller
component AS_bd_4p_LatchController_fd
  Generic (reset_value : bit := '0');
    Port  (req_in:   in  std_logic;
           ack_out:  in  std_logic;
           req_out:  out std_logic;
           ack_in:   out std_logic;
           reset:    in  std_logic; --Active low
           lt:       out std_logic); -- active high
end component;

signal s_y, s_lt: std_logic;

begin

latch_controller: AS_bd_4p_LatchController_fd
  generic map (reset_value => reset_status)
  port map (reset => reset, req_in => req_in, ack_out => ack_out, 
            ack_in => ack_in, req_out => s_y, lt=>s_lt);

--The number of delay elements are specified as a generic
delay_element: AS_Delay
  generic map (size => delay)
  port map (d => s_y, z => req_out);
  
latching_process: process(dat_in, s_lt, reset)
begin
   if reset='0' then
      dat_out <= conv_std_logic_vector(reset_value,width);
   elsif s_lt = '0' then
      dat_out <= dat_in; 
   end if;
end process Latching_Process;
end rtl; --architecture