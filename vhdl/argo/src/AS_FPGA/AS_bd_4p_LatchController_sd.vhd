-- -----------------------------------------------------------------------------
--  Title      :  4 phase latch controllers with reset.
--
--  Notes      :  To avoid optimization of the synthesis tool
--                (Xilinx ISE), this code forces the values of the LUT.
--                This description is specifically written for the Xilinx
--                Spartan-IIE FPGA. It should synthesize on Xilinx Virtex, Virtex-E,
--                Virtex-II, Virtex-II Pro, Virtex-II Pro X, Spartan-II,
--                Spartan-IIE, and Spartan-3, but this has not been tested.
--
--                By using the UNISIM lib, ModelSim or any other VHDL simulator
--                can be used to verify the funcionality of the design.
--
--  Developer  :  Mikkel Stensgaard  -- s001434@student.dtu.dk
--
--  Revision   :  1.0    09-06-04     Initial version
-- -----------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

LIBRARY UNISIM;
USE UNISIM.Vcomponents.all;

entity AS_bd_4p_LatchController_sd is
Generic (reset_value : bit := '0');
Port ( req_in:  in  std_logic;
      ack_in:  out std_logic;
      req_out: out std_logic;
      ack_out: in  std_logic;
      reset:   in  std_logic; --active low
      lt:      out std_logic);--active high
end entity;

architecture semi_decoupled of AS_bd_4p_LatchController_sd is


-----------------------
-- XILINX COMPONENTS --
-----------------------
-- 4-Bit Look-Up-Table with Local Output
component LUT4_L
generic (INIT : bit_vector(15 downto 0));
port (
      I0 : in  std_ulogic;
      I1 : in  std_ulogic;
      I2 : in  std_ulogic;
      I3 : in  std_ulogic;
      lO : out std_ulogic);
end component;

-- 2 input MUX, which can be used to mux between the outputs
-- of the 2 LUTS in a Slice. (Each CLB is divided into 2 slices
                              -- of each 2 LUTS)
component MUXF5_L
port (
      LO : out std_ulogic;
      I0 : in  std_ulogic;
      I1 : in  std_ulogic;
      S  : in  std_ulogic);
end component;
----------------------------------------------------

-- Constant using the generic "reset_value"
constant rv : bit := reset_value;
constant reset_vector : bit_vector(7 downto 0) := rv&rv&rv&rv&rv&rv&rv&rv;

-- Internal signals
signal s_A_int,s_A,s_out : std_ulogic;

--ATTRIBUTE KEEP: STRING;
--ATTRIBUTE KEEP OF s_A: SIGNAL IS "true";
--ATTRIBUTE KEEP OF s_LA: SIGNAL IS "true";
--ATTRIBUTE KEEP OF s_out: SIGNAL IS "true";
begin

--------------
-- A
--------------
-- [A] = A (Rin + Rout' + Aout') + Rin Rout';
lut_a : LUT4_L
generic map(INIT => "1011111100001010")
port map (I0 => req_in, I1 => ack_out, I2 => s_out, I3 => s_A, LO => s_A_int);

-- Unfortunately we need to reset the A signal by using the F5 mux in the same CLB slice.
-- This takes up another lut, but should be very fast.
muxf5_reset : MUXF5_L
port map(S => reset, I0 => To_StdULogic(reset_value), I1 => s_A_int, LO => s_A);

--------------
-- Rout
--------------
lut_out : LUT4_L
generic map(INIT => "10100010"&reset_vector)
port map (I0 => s_A, I1 => ack_out, I2 => s_out, I3 => reset, LO => s_out);

--------------
-- Connect the outputs to the correct signals
--------------
req_out <= s_out;
lt <= s_A;
ack_in <= s_A;

end architecture; --sd