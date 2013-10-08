onerror {resume}
quietly WaveActivateNextPane {} 0

add wave /aegean_testbench/clk
add wave /aegean_testbench/reset

add wave /aegean_testbench/aegean/ocp_core_ms(0)
add wave /aegean_testbench/aegean/ocp_core_ss(0)

add wave -hexadecimal /aegean_testbench/aegean/ocp_io_ms(0)
add wave -hexadecimal /aegean_testbench/aegean/ocp_io_ss(0)

add wave -hexadecimal aegean_testbench/aegean/patmoss(0)/l0/patmos_p/fetch/pcReg

add wave /aegean_testbench/aegean/noc/nodes_m(0)/nodes_n(0)/node/na/ocp_cmd_write
add wave /aegean_testbench/aegean/noc/nodes_m(0)/nodes_n(0)/node/na/response_ld_control
add wave /aegean_testbench/aegean/noc/nodes_m(0)/nodes_n(0)/node/na/ocp_write_control
add wave /aegean_testbench/aegean/noc/nodes_m(0)/nodes_n(0)/node/na/resp_ld

add wave /aegean_testbench/aegean/spms(0)/spm/wr_h
add wave /aegean_testbench/aegean/spms(0)/spm/wr_l
add wave /aegean_testbench/aegean/spms(0)/spm/select_high
add wave /aegean_testbench/aegean/spms(0)/spm/select_low

add wave -hexadecimal /aegean_testbench/aegean/spms(0)/spm/spm_h_0/mem
add wave -hexadecimal /aegean_testbench/aegean/spms(0)/spm/spm_l_0/mem

add wave -hexadecimal /aegean_testbench/aegean/spms(1)/spm/spm_h_0/mem
add wave -hexadecimal /aegean_testbench/aegean/spms(1)/spm/spm_l_0/mem



TreeUpdate [SetDefaultTree]
WaveRestoreCursors {{Cursor 1} {509818 ps} 0}
configure wave -namecolwidth 380
configure wave -valuecolwidth 100
configure wave -justifyvalue left
configure wave -signalnamewidth 0
configure wave -snapdistance 10
configure wave -datasetprefix 0
configure wave -rowmargin 4
configure wave -childrowmargin 2
configure wave -gridoffset 0
configure wave -gridperiod 1
configure wave -griddelta 40
configure wave -timeline 0
configure wave -timelineunits ns
update
WaveRestoreZoom {169397 ps} {579393 ps}
