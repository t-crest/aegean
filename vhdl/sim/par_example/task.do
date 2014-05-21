vlib work
vmap work work
vmap simprims_ver /home/lestat/Programs/Xilinx/14.7/ISE_DS/ISE/verilog/mti_se/10.1b/lin64/simprims_ver
vlog -quiet -work work /home/lestat/Programs/Xilinx/14.7/ISE_DS/ISE/verilog/src/glbl.v ise/netgen/par/aegean_top_timesim.v
vcom -quiet -93 -work work /home/lestat/t-crest/argo/src/ocp/ocp_config.vhd /home/lestat/t-crest/argo/src/ocp/ocp.vhd
vcom -quiet -93 -work work /home/lestat/t-crest/aegean/vhdl/packages/test.vhd aegean_testbench_POST.vhd
vsim -novopt -L simprims_ver -sdftyp /aegean_testbench/top=ise/netgen/par/aegean_top_timesim.sdf -do waves.do work.aegean_testbench work.glbl

