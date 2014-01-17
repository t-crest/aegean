--
-- Copyright: 2013, Technical University of Denmark, DTU Compute
-- Author: Rasmus Bo Soerensen (rasmus@rbscloud.dk)
-- License: Simplified BSD License
--

LIBRARY ieee;
USE ieee.std_logic_1164.all;

ENTITY pll IS
    generic (multiply_by : natural; divide_by : natural);
    PORT
    (
        inclk0      : IN STD_LOGIC  := '0';
        c0      : OUT STD_LOGIC ;
        c1      : OUT STD_LOGIC ;
        locked      : OUT STD_LOGIC
    );
END pll;

ARCHITECTURE SYN OF pll IS


BEGIN
    c0 <= inclk0;
    c1 <= not inclk0;
    locked <= '1';

END SYN;

