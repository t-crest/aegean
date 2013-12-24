mem save -startaddress 0 -endaddress 127 -format hex -wordsperline 1 -outfile m0_h0.txt /aegean_testbench/aegean/spms(0)/spm/spm_h_0/mem
mem save -startaddress 0 -endaddress 127 -format hex -wordsperline 1 -outfile m0_h1.txt /aegean_testbench/aegean/spms(0)/spm/spm_h_1/mem
mem save -startaddress 0 -endaddress 127 -format hex -wordsperline 1 -outfile m0_h2.txt /aegean_testbench/aegean/spms(0)/spm/spm_h_2/mem
mem save -startaddress 0 -endaddress 127 -format hex -wordsperline 1 -outfile m0_h3.txt /aegean_testbench/aegean/spms(0)/spm/spm_h_3/mem
mem save -startaddress 0 -endaddress 127 -format hex -wordsperline 1 -outfile m0_l0.txt /aegean_testbench/aegean/spms(0)/spm/spm_l_0/mem
mem save -startaddress 0 -endaddress 127 -format hex -wordsperline 1 -outfile m0_l1.txt /aegean_testbench/aegean/spms(0)/spm/spm_l_1/mem
mem save -startaddress 0 -endaddress 127 -format hex -wordsperline 1 -outfile m0_l2.txt /aegean_testbench/aegean/spms(0)/spm/spm_l_2/mem
mem save -startaddress 0 -endaddress 127 -format hex -wordsperline 1 -outfile m0_l3.txt /aegean_testbench/aegean/spms(0)/spm/spm_l_3/mem


#mem save -startaddress 0 -endaddress 15 -format hex -wordsperline 1 -outfile m1n1_l.txt /test2_noc2x2/spm_m(1)/spm_n(1)/spm_l/mem
#
#mem save -startaddress 0 -endaddress 15 -format hex -wordsperline 1 -outfile m1n0_h.txt /test2_noc2x2/spm_m(1)/spm_n(0)/spm_h/mem
#mem save -startaddress 0 -endaddress 15 -format hex -wordsperline 1 -outfile m1n0_l.txt /test2_noc2x2/spm_m(1)/spm_n(0)/spm_l/mem
#
#mem save -startaddress 0 -endaddress 15 -format hex -wordsperline 1 -outfile m0n1_h.txt /test2_noc2x2/spm_m(0)/spm_n(1)/spm_h/mem
#mem save -startaddress 0 -endaddress 15 -format hex -wordsperline 1 -outfile m0n1_l.txt /test2_noc2x2/spm_m(0)/spm_n(1)/spm_l/mem
#
#mem save -startaddress 0 -endaddress 15 -format hex -wordsperline 1 -outfile m0n0_h.txt /test2_noc2x2/spm_m(0)/spm_n(0)/spm_h/mem
#mem save -startaddress 0 -endaddress 15 -format hex -wordsperline 1 -outfile m0n0_l.txt /test2_noc2x2/spm_m(0)/spm_n(0)/spm_l/mem

exec paste m0_h3.txt m0_h2.txt m0_h1.txt m0_h0.txt m0_l3.txt m0_l2.txt m0_l1.txt m0_l0.txt | grep @ | awk "{print \$1\":\"\$2\$4\$6\$8\$10\$12\$14\$16\; }" > spm_[exec echo $1]_[expr $now].txt


#exec paste m0_h3.txt m0_h2.txt m0_h1.txt m0_h0.txt m0_l3.txt m0_l2.txt m0_l1.txt m0_l0.txt | grep @ > mem_dump_[expr $now].combined
#exec awk "{print \$1\":\"\$2\$4\$6\$8\$10\$12\$14\$16\; }" mem_dump_[expr $now].combined > nice_mem_dump_[expr $now].txt
