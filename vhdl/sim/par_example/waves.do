set NumericStdNoWarnings 1
view *
onerror {resume}
quietly WaveActivateNextPane {} 0
add log -r /*
TreeUpdate [SetDefaultTree]
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
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_3/Mram_mem/genblk1/INT_RAMB_TDP/mem[0]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_2/Mram_mem/genblk1/INT_RAMB_TDP/mem[0]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_1/Mram_mem/genblk1/INT_RAMB_TDP/mem[0]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_0/Mram_mem/genblk1/INT_RAMB_TDP/mem[0]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_3/Mram_mem/genblk1/INT_RAMB_TDP/mem[0]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_2/Mram_mem/genblk1/INT_RAMB_TDP/mem[0]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_1/Mram_mem/genblk1/INT_RAMB_TDP/mem[0]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_0/Mram_mem/genblk1/INT_RAMB_TDP/mem[0]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_3/Mram_mem/genblk1/INT_RAMB_TDP/mem[1]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_2/Mram_mem/genblk1/INT_RAMB_TDP/mem[1]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_1/Mram_mem/genblk1/INT_RAMB_TDP/mem[1]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_0/Mram_mem/genblk1/INT_RAMB_TDP/mem[1]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_3/Mram_mem/genblk1/INT_RAMB_TDP/mem[1]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_2/Mram_mem/genblk1/INT_RAMB_TDP/mem[1]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_1/Mram_mem/genblk1/INT_RAMB_TDP/mem[1]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_0/Mram_mem/genblk1/INT_RAMB_TDP/mem[1]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_3/Mram_mem/genblk1/INT_RAMB_TDP/mem[2]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_2/Mram_mem/genblk1/INT_RAMB_TDP/mem[2]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_1/Mram_mem/genblk1/INT_RAMB_TDP/mem[2]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_0/Mram_mem/genblk1/INT_RAMB_TDP/mem[2]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_3/Mram_mem/genblk1/INT_RAMB_TDP/mem[2]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_2/Mram_mem/genblk1/INT_RAMB_TDP/mem[2]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_1/Mram_mem/genblk1/INT_RAMB_TDP/mem[2]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_0/Mram_mem/genblk1/INT_RAMB_TDP/mem[2]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_3/Mram_mem/genblk1/INT_RAMB_TDP/mem[8]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_2/Mram_mem/genblk1/INT_RAMB_TDP/mem[8]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_1/Mram_mem/genblk1/INT_RAMB_TDP/mem[8]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_0/Mram_mem/genblk1/INT_RAMB_TDP/mem[8]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_3/Mram_mem/genblk1/INT_RAMB_TDP/mem[8]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_2/Mram_mem/genblk1/INT_RAMB_TDP/mem[8]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_1/Mram_mem/genblk1/INT_RAMB_TDP/mem[8]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_0/Mram_mem/genblk1/INT_RAMB_TDP/mem[8]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_3/Mram_mem/genblk1/INT_RAMB_TDP/mem[9]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_2/Mram_mem/genblk1/INT_RAMB_TDP/mem[9]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_1/Mram_mem/genblk1/INT_RAMB_TDP/mem[9]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_0/Mram_mem/genblk1/INT_RAMB_TDP/mem[9]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_3/Mram_mem/genblk1/INT_RAMB_TDP/mem[9]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_2/Mram_mem/genblk1/INT_RAMB_TDP/mem[9]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_1/Mram_mem/genblk1/INT_RAMB_TDP/mem[9]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_0/Mram_mem/genblk1/INT_RAMB_TDP/mem[9]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_3/Mram_mem/genblk1/INT_RAMB_TDP/mem[10]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_2/Mram_mem/genblk1/INT_RAMB_TDP/mem[10]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_1/Mram_mem/genblk1/INT_RAMB_TDP/mem[10]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_h_0/Mram_mem/genblk1/INT_RAMB_TDP/mem[10]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_3/Mram_mem/genblk1/INT_RAMB_TDP/mem[10]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_2/Mram_mem/genblk1/INT_RAMB_TDP/mem[10]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_1/Mram_mem/genblk1/INT_RAMB_TDP/mem[10]}
add wave -position insertpoint {sim:/aegean_testbench/top/cmp/\spms[0].spm /spm_l_0/Mram_mem/genblk1/INT_RAMB_TDP/mem[10]}
