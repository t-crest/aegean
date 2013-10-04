###########################################################################
# SDC file for Aegean platform on DE2-70 board
###########################################################################
 
 
# Clock in input pin (50 MHz)
create_clock -period 20 [get_ports clk]

derive_clock_uncertainty
# Create generated clocks based on PLLs
derive_pll_clocks -use_tan_name

# Use FPGA-centric constraints (general pins)
# Tsu 5 ns
set_max_delay -from [all_inputs] -to [all_registers] 5
set_min_delay -from [all_inputs] -to [all_registers] -0.0
# Tco 10 ns
set_max_delay -from [all_registers] -to [all_outputs] 10
set_min_delay -from [all_registers] -to [all_outputs] -0.0

# Use FPGA-centric constraints (SRAM pins)
# Tsu 2 ns
set_max_delay -from [get_ports *RAM*] -to [get_registers {*}] 2.2
# Tco 3 ns
set_max_delay -from [get_registers *] -to [get_ports {*RAM*}] 3

# ssram clk derived from clk1 of pll_inst
set_min_delay 0 -from [get_clocks {*pll:pll_inst*_clk1}] -to [get_ports {oSRAM_CLK}]
set_max_delay 3 -from [get_clocks {*pll:pll_inst*_clk1}] -to [get_ports {oSRAM_CLK}]
