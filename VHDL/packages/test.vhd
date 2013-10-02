library ieee;
use ieee.std_logic_1164.all;

package test is
	procedure clock_gen (signal clk : out std_logic; constant period : in time);
	procedure reset_gen (signal reset : out std_logic ; constant reset_time : in time);

end package test;

package body test is
	procedure clock_gen (signal clk : out std_logic; constant period : in time) is
	variable clk_int : std_logic := '0';
	begin -- Careful this process runs forever:
		loop
			clk_int := not clk_int;
			clk <= clk_int;
			wait for period/2;
		end loop;
	end;

	procedure reset_gen (signal reset : out std_logic ; constant reset_time : in time) is
	begin -- Careful this process runs forever:
		reset <= '1';
		wait for reset_time;
		reset <= '0';
		wait;
	end;


	--procedure test_function (signal clk : in std_logic;
	--						signal sc_out : out sc_out_type;
	--						signal sc_in : in sc_in_type;
	--						constant addr : in natural;
	--						constant period : in time) is
	--variable result : natural;
	--begin
	--	report "-------- Testing " & addr'simple_name & " --------";
	--	for i in 0 to 10 loop
	--		wait until rising_edge(clk);
	--		sc_write(clk,addr+i,i,sc_out,sc_in,5);
	--		wait for period;
	--	end loop;
	--
	--	for i in 0 to 10 loop
	--		wait until rising_edge(clk);
	--		sc_read(clk,addr+i,result,sc_out,sc_in,6);
	--		assert result = i report "Wrong result read out!" severity failure;
	--		wait for period;
	--	end loop;
	--	report "-------- " & addr'simple_name & " test passed --------";
	--end;

end package body test;
