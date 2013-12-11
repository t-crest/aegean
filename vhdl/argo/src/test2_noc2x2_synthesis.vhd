-- 
-- Copyright Technical University of Denmark. All rights reserved.
-- This file is part of the T-CREST project.
-- 
-- Redistribution and use in source and binary forms, with or without
-- modification, are permitted provided that the following conditions are met:
-- 
--    1. Redistributions of source code must retain the above copyright notice,
--       this list of conditions and the following disclaimer.
-- 
--    2. Redistributions in binary form must reproduce the above copyright
--       notice, this list of conditions and the following disclaimer in the
--       documentation and/or other materials provided with the distribution.
-- 
-- THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ``AS IS'' AND ANY EXPRESS
-- OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
-- OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN
-- NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
-- DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
-- (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
-- LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
-- ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
-- (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
-- THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
-- 
-- The views and conclusions contained in the software and documentation are
-- those of the authors and should not be interpreted as representing official
-- policies, either expressed or implied, of the copyright holder.
-- 


--------------------------------------------------------------------------------
-- Testbench for a 2x2 TDM NoC, with 8 slot period and 4 DMAs,
-- with the following configuration:
-- all-to-all communication
-- all nodes
-- DMA0:  Channel1: north
-- DMA1:  Channel2: east
-- DMA2:  Channel3: east -> north
--
-- SCHEDULE
-- 0:DMA0
-- 1:DMA1
-- 2:DMA2
-- 3:invalid
-- 4:DMA0
-- 5:DMA1
-- 6:DMA2
-- 7:invalid
--
-- Author: Evangelia Kasapaki
--------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use ieee.std_logic_textio.all;
use ieee.numeric_std.all;
use std.textio.all;
use work.txt_util.all;
use work.cmd_util.all;
use work.config.all;
use work.noc_defs.all;
use work.ocp.all;
use work.noc_interface.all;


entity test2_noc2x2_synthesis is
end test2_noc2x2_synthesis;


architecture behav of test2_noc2x2_synthesis is

-----------------------component declarations------------------------------
--component noc is
--port (
--	--p_clk		: in std_logic;
--	n_clk		: in std_logic;
--    n_clk_skd	: in std_logic;
--	reset		: in std_logic;
--
--	ocp_io_ms	: in ocp_io_m_a;
--	ocp_io_ss	: out ocp_io_s_a;
--
--	spm_ports_s	: in spm_slaves;
--	spm_ports_m	: out spm_masters
--
--);
--end component;


component bram_tdp is

generic (
    DATA    : integer := 32;
    ADDR    : integer := 14
);

port (
-- Port A
    a_clk   : in  std_logic;
    a_wr    : in  std_logic;
    a_addr  : in  std_logic_vector(ADDR-1 downto 0);
    a_din   : in  std_logic_vector(DATA-1 downto 0);
    a_dout  : out std_logic_vector(DATA-1 downto 0);
     
-- Port B
    b_clk   : in  std_logic;
    b_wr    : in  std_logic;
    b_addr  : in  std_logic_vector(ADDR-1 downto 0);
    b_din   : in  std_logic_vector(DATA-1 downto 0);
    b_dout  : out std_logic_vector(DATA-1 downto 0)
);
end component;

-------------------------signal declarations-------------------------------
signal n_clk		: std_logic := '1';
signal p_clk		: std_logic := '1';
signal n_clk_sk		: std_logic := '1';
signal p_clk_sk		: std_logic := '1';
signal reset		: std_logic := '1';

signal p_masters	: ocp_io_m_a;
signal p_slaves		: ocp_io_s_a;
signal p_spm_masters	: spm_masters;
signal P_spm_slaves	: spm_slaves;
signal n_spm_masters	: spm_masters;
signal n_spm_slaves	: spm_slaves;

constant SCHED_FILE     : string (87 downto 1) := "D:\Users\Dean\Dropbox\DTU\2013 E\FPGA NoC\Testing\tb_noc\noc_async\sim/all_to_all.sched";
file schedule0          : text open READ_MODE is SCHED_FILE;
file schedule1          : text open READ_MODE is SCHED_FILE;
file schedule2          : text open READ_MODE is SCHED_FILE;
file schedule3          : text open READ_MODE is SCHED_FILE;

constant SPM_INIT_SIZE : integer := 4;

begin


	spm_m : for i in N-1 downto 0 generate
		spm_n : for j in N-1 downto 0 generate
                  
                        skewed: if i=0 and j=0 generate        
			-- High SPM instance
                        spm_h : bram_tdp
                          generic map (DATA=>DATA_WIDTH, ADDR => SPM_ADDR_WIDTH)
                          port map (a_clk => p_clk_sk, 
                                    a_wr => p_spm_masters((i*N)+j).MCmd(0), 
                                    a_addr => p_spm_masters((i*N)+j).MAddr(SPM_ADDR_WIDTH-1 downto 0), 
                                    a_din => p_spm_masters((i*N)+j).MData(63 downto 32), 
                                    a_dout => p_spm_slaves((i*N)+j).SData(63 downto 32), 
                                    b_clk => n_clk_sk,
                                    b_wr => n_spm_masters((i*N)+j).MCmd(0), 
                                    b_addr => n_spm_masters((i*N)+j).MAddr(SPM_ADDR_WIDTH-1 downto 0), 
                                    b_din => n_spm_masters((i*N)+j).MData(63 downto 32), 
                                    b_dout => n_spm_slaves((i*N)+j).SData(63 downto 32));

                        -- Low SPM instance
                        spm_l : bram_tdp
                          generic map (DATA => DATA_WIDTH, ADDR => SPM_ADDR_WIDTH)
                          port map (a_clk => p_clk_sk, 
                                    a_wr => p_spm_masters((i*N)+j).MCmd(0), 
                                    a_addr => p_spm_masters((i*N)+j).MAddr(SPM_ADDR_WIDTH-1 downto 0), 
                                    a_din => p_spm_masters((i*N)+j).MData(31 downto 0), 
                                    a_dout => p_spm_slaves((i*N)+j).SData(31 downto 0), 
                                    b_clk => n_clk_sk,
                                    b_wr => n_spm_masters((i*N)+j).MCmd(0), 
                                    b_addr => n_spm_masters((i*N)+j).MAddr(SPM_ADDR_WIDTH-1 downto 0), 
                                    b_din => n_spm_masters((i*N)+j).MData(31 downto 0), 
                                    b_dout => n_spm_slaves((i*N)+j).SData(31 downto 0));

                        end generate skewed;

                        not_skewed: if not(i=0) or not(j=0) generate
                        -- High SPM instance
                        spm_h : bram_tdp
                          generic map (DATA=>DATA_WIDTH, ADDR => SPM_ADDR_WIDTH)
                          port map (a_clk => p_clk, 
                                    a_wr => p_spm_masters((i*N)+j).MCmd(0), 
                                    a_addr => p_spm_masters((i*N)+j).MAddr(SPM_ADDR_WIDTH-1 downto 0), 
                                    a_din => p_spm_masters((i*N)+j).MData(63 downto 32), 
                                    a_dout => p_spm_slaves((i*N)+j).SData(63 downto 32), 
                                    b_clk => n_clk,
                                    b_wr => n_spm_masters((i*N)+j).MCmd(0), 
                                    b_addr => n_spm_masters((i*N)+j).MAddr(SPM_ADDR_WIDTH-1 downto 0), 
                                    b_din => n_spm_masters((i*N)+j).MData(63 downto 32), 
                                    b_dout => n_spm_slaves((i*N)+j).SData(63 downto 32));

                        -- Low SPM instance
                        spm_l : bram_tdp
                          generic map (DATA => DATA_WIDTH, ADDR => SPM_ADDR_WIDTH)
                          port map (a_clk => p_clk, 
                                    a_wr => p_spm_masters((i*N)+j).MCmd(0), 
                                    a_addr => p_spm_masters((i*N)+j).MAddr(SPM_ADDR_WIDTH-1 downto 0), 
                                    a_din => p_spm_masters((i*N)+j).MData(31 downto 0), 
                                    a_dout => p_spm_slaves((i*N)+j).SData(31 downto 0), 
                                    b_clk => n_clk,
                                    b_wr => n_spm_masters((i*N)+j).MCmd(0), 
                                    b_addr => n_spm_masters((i*N)+j).MAddr(SPM_ADDR_WIDTH-1 downto 0), 
                                    b_din => n_spm_masters((i*N)+j).MData(31 downto 0), 
                                    b_dout => n_spm_slaves((i*N)+j).SData(31 downto 0));
                        
                        end generate not_skewed;

                          
                end generate spm_n;
        end generate spm_m;
  

noc2x2 : entity work.noc_synthesis
	port map(ocp_io_ms_3_MRespAccept  => p_masters(3).MRespAccept,
		     n_clk                    => n_clk,
		     reset                    => reset,
		     ocp_io_ss_1_SCmdAccept   => p_slaves(1).SCmdAccept,
		     ocp_io_ms_2_MRespAccept  => p_masters(2).MRespAccept,
		     ocp_io_ss_0_SCmdAccept   => p_slaves(0).SCmdAccept,
		     ocp_io_ms_0_MRespAccept  => p_masters(0).MRespAccept,
		     ocp_io_ss_2_SCmdAccept   => p_slaves(2).SCmdAccept,
		     n_clk_skd                => n_clk_sk,
		     ocp_io_ms_1_MRespAccept  => p_masters(1).MRespAccept,
		     ocp_io_ss_3_SCmdAccept   => p_slaves(3).SCmdAccept,
		     ocp_io_ss_0_SData_31_Q   => p_slaves(0).SData(31),
		     ocp_io_ss_0_SData_30_Q   => p_slaves(0).SData(30),
		     ocp_io_ss_0_SData_29_Q   => p_slaves(0).SData(29),
		     ocp_io_ss_0_SData_28_Q   => p_slaves(0).SData(28),
		     ocp_io_ss_0_SData_27_Q   => p_slaves(0).SData(27),
		     ocp_io_ss_0_SData_26_Q   => p_slaves(0).SData(26),
		     ocp_io_ss_0_SData_25_Q   => p_slaves(0).SData(25),
		     ocp_io_ss_0_SData_24_Q   => p_slaves(0).SData(24),
		     ocp_io_ss_0_SData_23_Q   => p_slaves(0).SData(23),
		     ocp_io_ss_0_SData_22_Q   => p_slaves(0).SData(22),
		     ocp_io_ss_0_SData_21_Q   => p_slaves(0).SData(21),
		     ocp_io_ss_0_SData_20_Q   => p_slaves(0).SData(20),
		     ocp_io_ss_0_SData_19_Q   => p_slaves(0).SData(19),
		     ocp_io_ss_0_SData_18_Q   => p_slaves(0).SData(18),
		     ocp_io_ss_0_SData_17_Q   => p_slaves(0).SData(17),
		     ocp_io_ss_0_SData_16_Q   => p_slaves(0).SData(16),
		     ocp_io_ss_0_SData_15_Q   => p_slaves(0).SData(15),
		     ocp_io_ss_0_SData_14_Q   => p_slaves(0).SData(14),
		     ocp_io_ss_0_SData_13_Q   => p_slaves(0).SData(13),
		     ocp_io_ss_0_SData_12_Q   => p_slaves(0).SData(12),
		     ocp_io_ss_0_SData_11_Q   => p_slaves(0).SData(11),
		     ocp_io_ss_0_SData_10_Q   => p_slaves(0).SData(10),
		     ocp_io_ss_0_SData_9_Q    => p_slaves(0).SData(9),
		     ocp_io_ss_0_SData_8_Q    => p_slaves(0).SData(8),
		     ocp_io_ss_0_SData_7_Q    => p_slaves(0).SData(7),
		     ocp_io_ss_0_SData_6_Q    => p_slaves(0).SData(6),
		     ocp_io_ss_0_SData_5_Q    => p_slaves(0).SData(5),
		     ocp_io_ss_0_SData_4_Q    => p_slaves(0).SData(4),
		     ocp_io_ss_0_SData_3_Q    => p_slaves(0).SData(3),
		     ocp_io_ss_0_SData_2_Q    => p_slaves(0).SData(2),
		     ocp_io_ss_0_SData_1_Q    => p_slaves(0).SData(1),
		     ocp_io_ss_0_SData_0_Q    => p_slaves(0).SData(0),
		     ocp_io_ss_3_SResp_1_Q    => p_slaves(3).SResp(1),
		     ocp_io_ss_3_SResp_0_Q    => p_slaves(3).SResp(0),
		     spm_ports_m_0_MAddr_15_Q => n_spm_masters(0).MAddr(15),
		     spm_ports_m_0_MAddr_14_Q => n_spm_masters(0).MAddr(14),
		     spm_ports_m_0_MAddr_13_Q => n_spm_masters(0).MAddr(13),
		     spm_ports_m_0_MAddr_12_Q => n_spm_masters(0).MAddr(12),
		     spm_ports_m_0_MAddr_11_Q => n_spm_masters(0).MAddr(11),
		     spm_ports_m_0_MAddr_10_Q => n_spm_masters(0).MAddr(10),
		     spm_ports_m_0_MAddr_9_Q  => n_spm_masters(0).MAddr(9),
		     spm_ports_m_0_MAddr_8_Q  => n_spm_masters(0).MAddr(8),
		     spm_ports_m_0_MAddr_7_Q  => n_spm_masters(0).MAddr(7),
		     spm_ports_m_0_MAddr_6_Q  => n_spm_masters(0).MAddr(6),
		     spm_ports_m_0_MAddr_5_Q  => n_spm_masters(0).MAddr(5),
		     spm_ports_m_0_MAddr_4_Q  => n_spm_masters(0).MAddr(4),
		     spm_ports_m_0_MAddr_3_Q  => n_spm_masters(0).MAddr(3),
		     spm_ports_m_0_MAddr_2_Q  => n_spm_masters(0).MAddr(2),
		     spm_ports_m_0_MAddr_1_Q  => n_spm_masters(0).MAddr(1),
		     spm_ports_m_0_MAddr_0_Q  => n_spm_masters(0).MAddr(0),
		     spm_ports_m_3_MCmd_0_Q   => n_spm_masters(3).MCmd(0),
		     spm_ports_m_2_MCmd_0_Q   => n_spm_masters(2).MCmd(0),
		     ocp_io_ss_2_SResp_1_Q    => p_slaves(2).SResp(1),
		     ocp_io_ss_2_SResp_0_Q    => p_slaves(2).SResp(0),
		     spm_ports_m_1_MCmd_0_Q   => n_spm_masters(1).MCmd(0),
		     spm_ports_m_0_MCmd_0_Q   => n_spm_masters(0).MCmd(0),
		     spm_ports_m_3_MData_63_Q => n_spm_masters(3).MData(63),
		     spm_ports_m_3_MData_62_Q => n_spm_masters(3).MData(62),
		     spm_ports_m_3_MData_61_Q => n_spm_masters(3).MData(61),
		     spm_ports_m_3_MData_60_Q => n_spm_masters(3).MData(60),
		     spm_ports_m_3_MData_59_Q => n_spm_masters(3).MData(59),
		     spm_ports_m_3_MData_58_Q => n_spm_masters(3).MData(58),
		     spm_ports_m_3_MData_57_Q => n_spm_masters(3).MData(57),
		     spm_ports_m_3_MData_56_Q => n_spm_masters(3).MData(56),
		     spm_ports_m_3_MData_55_Q => n_spm_masters(3).MData(55),
		     spm_ports_m_3_MData_54_Q => n_spm_masters(3).MData(54),
		     spm_ports_m_3_MData_53_Q => n_spm_masters(3).MData(53),
		     spm_ports_m_3_MData_52_Q => n_spm_masters(3).MData(52),
		     spm_ports_m_3_MData_51_Q => n_spm_masters(3).MData(51),
		     spm_ports_m_3_MData_50_Q => n_spm_masters(3).MData(50),
		     spm_ports_m_3_MData_49_Q => n_spm_masters(3).MData(49),
		     spm_ports_m_3_MData_48_Q => n_spm_masters(3).MData(48),
		     spm_ports_m_3_MData_47_Q => n_spm_masters(3).MData(47),
		     spm_ports_m_3_MData_46_Q => n_spm_masters(3).MData(46),
		     spm_ports_m_3_MData_45_Q => n_spm_masters(3).MData(45),
		     spm_ports_m_3_MData_44_Q => n_spm_masters(3).MData(44),
		     spm_ports_m_3_MData_43_Q => n_spm_masters(3).MData(43),
		     spm_ports_m_3_MData_42_Q => n_spm_masters(3).MData(42),
		     spm_ports_m_3_MData_41_Q => n_spm_masters(3).MData(41),
		     spm_ports_m_3_MData_40_Q => n_spm_masters(3).MData(40),
		     spm_ports_m_3_MData_39_Q => n_spm_masters(3).MData(39),
		     spm_ports_m_3_MData_38_Q => n_spm_masters(3).MData(38),
		     spm_ports_m_3_MData_37_Q => n_spm_masters(3).MData(37),
		     spm_ports_m_3_MData_36_Q => n_spm_masters(3).MData(36),
		     spm_ports_m_3_MData_35_Q => n_spm_masters(3).MData(35),
		     spm_ports_m_3_MData_34_Q => n_spm_masters(3).MData(34),
		     spm_ports_m_3_MData_33_Q => n_spm_masters(3).MData(33),
		     spm_ports_m_3_MData_32_Q => n_spm_masters(3).MData(32),
		     spm_ports_m_3_MData_31_Q => n_spm_masters(3).MData(31),
		     spm_ports_m_3_MData_30_Q => n_spm_masters(3).MData(30),
		     spm_ports_m_3_MData_29_Q => n_spm_masters(3).MData(29),
		     spm_ports_m_3_MData_28_Q => n_spm_masters(3).MData(28),
		     spm_ports_m_3_MData_27_Q => n_spm_masters(3).MData(27),
		     spm_ports_m_3_MData_26_Q => n_spm_masters(3).MData(26),
		     spm_ports_m_3_MData_25_Q => n_spm_masters(3).MData(25),
		     spm_ports_m_3_MData_24_Q => n_spm_masters(3).MData(24),
		     spm_ports_m_3_MData_23_Q => n_spm_masters(3).MData(23),
		     spm_ports_m_3_MData_22_Q => n_spm_masters(3).MData(22),
		     spm_ports_m_3_MData_21_Q => n_spm_masters(3).MData(21),
		     spm_ports_m_3_MData_20_Q => n_spm_masters(3).MData(20),
		     spm_ports_m_3_MData_19_Q => n_spm_masters(3).MData(19),
		     spm_ports_m_3_MData_18_Q => n_spm_masters(3).MData(18),
		     spm_ports_m_3_MData_17_Q => n_spm_masters(3).MData(17),
		     spm_ports_m_3_MData_16_Q => n_spm_masters(3).MData(16),
		     spm_ports_m_3_MData_15_Q => n_spm_masters(3).MData(15),
		     spm_ports_m_3_MData_14_Q => n_spm_masters(3).MData(14),
		     spm_ports_m_3_MData_13_Q => n_spm_masters(3).MData(13),
		     spm_ports_m_3_MData_12_Q => n_spm_masters(3).MData(12),
		     spm_ports_m_3_MData_11_Q => n_spm_masters(3).MData(11),
		     spm_ports_m_3_MData_10_Q => n_spm_masters(3).MData(10),
		     spm_ports_m_3_MData_9_Q  => n_spm_masters(3).MData(9),
		     spm_ports_m_3_MData_8_Q  => n_spm_masters(3).MData(8),
		     spm_ports_m_3_MData_7_Q  => n_spm_masters(3).MData(7),
		     spm_ports_m_3_MData_6_Q  => n_spm_masters(3).MData(6),
		     spm_ports_m_3_MData_5_Q  => n_spm_masters(3).MData(5),
		     spm_ports_m_3_MData_4_Q  => n_spm_masters(3).MData(4),
		     spm_ports_m_3_MData_3_Q  => n_spm_masters(3).MData(3),
		     spm_ports_m_3_MData_2_Q  => n_spm_masters(3).MData(2),
		     spm_ports_m_3_MData_1_Q  => n_spm_masters(3).MData(1),
		     spm_ports_m_3_MData_0_Q  => n_spm_masters(3).MData(0),
		     ocp_io_ss_3_SData_31_Q   => p_slaves(3).SData(31),
		     ocp_io_ss_3_SData_30_Q   => p_slaves(3).SData(30),
		     ocp_io_ss_3_SData_29_Q   => p_slaves(3).SData(29),
		     ocp_io_ss_3_SData_28_Q   => p_slaves(3).SData(28),
		     ocp_io_ss_3_SData_27_Q   => p_slaves(3).SData(27),
		     ocp_io_ss_3_SData_26_Q   => p_slaves(3).SData(26),
		     ocp_io_ss_3_SData_25_Q   => p_slaves(3).SData(25),
		     ocp_io_ss_3_SData_24_Q   => p_slaves(3).SData(24),
		     ocp_io_ss_3_SData_23_Q   => p_slaves(3).SData(23),
		     ocp_io_ss_3_SData_22_Q   => p_slaves(3).SData(22),
		     ocp_io_ss_3_SData_21_Q   => p_slaves(3).SData(21),
		     ocp_io_ss_3_SData_20_Q   => p_slaves(3).SData(20),
		     ocp_io_ss_3_SData_19_Q   => p_slaves(3).SData(19),
		     ocp_io_ss_3_SData_18_Q   => p_slaves(3).SData(18),
		     ocp_io_ss_3_SData_17_Q   => p_slaves(3).SData(17),
		     ocp_io_ss_3_SData_16_Q   => p_slaves(3).SData(16),
		     ocp_io_ss_3_SData_15_Q   => p_slaves(3).SData(15),
		     ocp_io_ss_3_SData_14_Q   => p_slaves(3).SData(14),
		     ocp_io_ss_3_SData_13_Q   => p_slaves(3).SData(13),
		     ocp_io_ss_3_SData_12_Q   => p_slaves(3).SData(12),
		     ocp_io_ss_3_SData_11_Q   => p_slaves(3).SData(11),
		     ocp_io_ss_3_SData_10_Q   => p_slaves(3).SData(10),
		     ocp_io_ss_3_SData_9_Q    => p_slaves(3).SData(9),
		     ocp_io_ss_3_SData_8_Q    => p_slaves(3).SData(8),
		     ocp_io_ss_3_SData_7_Q    => p_slaves(3).SData(7),
		     ocp_io_ss_3_SData_6_Q    => p_slaves(3).SData(6),
		     ocp_io_ss_3_SData_5_Q    => p_slaves(3).SData(5),
		     ocp_io_ss_3_SData_4_Q    => p_slaves(3).SData(4),
		     ocp_io_ss_3_SData_3_Q    => p_slaves(3).SData(3),
		     ocp_io_ss_3_SData_2_Q    => p_slaves(3).SData(2),
		     ocp_io_ss_3_SData_1_Q    => p_slaves(3).SData(1),
		     ocp_io_ss_3_SData_0_Q    => p_slaves(3).SData(0),
		     ocp_io_ss_1_SResp_1_Q    => p_slaves(1).SResp(1),
		     ocp_io_ss_1_SResp_0_Q    => p_slaves(1).SResp(0),
		     spm_ports_m_3_MAddr_15_Q => n_spm_masters(3).MAddr(15),
		     spm_ports_m_3_MAddr_14_Q => n_spm_masters(3).MAddr(14),
		     spm_ports_m_3_MAddr_13_Q => n_spm_masters(3).MAddr(13),
		     spm_ports_m_3_MAddr_12_Q => n_spm_masters(3).MAddr(12),
		     spm_ports_m_3_MAddr_11_Q => n_spm_masters(3).MAddr(11),
		     spm_ports_m_3_MAddr_10_Q => n_spm_masters(3).MAddr(10),
		     spm_ports_m_3_MAddr_9_Q  => n_spm_masters(3).MAddr(9),
		     spm_ports_m_3_MAddr_8_Q  => n_spm_masters(3).MAddr(8),
		     spm_ports_m_3_MAddr_7_Q  => n_spm_masters(3).MAddr(7),
		     spm_ports_m_3_MAddr_6_Q  => n_spm_masters(3).MAddr(6),
		     spm_ports_m_3_MAddr_5_Q  => n_spm_masters(3).MAddr(5),
		     spm_ports_m_3_MAddr_4_Q  => n_spm_masters(3).MAddr(4),
		     spm_ports_m_3_MAddr_3_Q  => n_spm_masters(3).MAddr(3),
		     spm_ports_m_3_MAddr_2_Q  => n_spm_masters(3).MAddr(2),
		     spm_ports_m_3_MAddr_1_Q  => n_spm_masters(3).MAddr(1),
		     spm_ports_m_3_MAddr_0_Q  => n_spm_masters(3).MAddr(0),
		     spm_ports_m_2_MData_63_Q => n_spm_masters(2).MData(63),
		     spm_ports_m_2_MData_62_Q => n_spm_masters(2).MData(62),
		     spm_ports_m_2_MData_61_Q => n_spm_masters(2).MData(61),
		     spm_ports_m_2_MData_60_Q => n_spm_masters(2).MData(60),
		     spm_ports_m_2_MData_59_Q => n_spm_masters(2).MData(59),
		     spm_ports_m_2_MData_58_Q => n_spm_masters(2).MData(58),
		     spm_ports_m_2_MData_57_Q => n_spm_masters(2).MData(57),
		     spm_ports_m_2_MData_56_Q => n_spm_masters(2).MData(56),
		     spm_ports_m_2_MData_55_Q => n_spm_masters(2).MData(55),
		     spm_ports_m_2_MData_54_Q => n_spm_masters(2).MData(54),
		     spm_ports_m_2_MData_53_Q => n_spm_masters(2).MData(53),
		     spm_ports_m_2_MData_52_Q => n_spm_masters(2).MData(52),
		     spm_ports_m_2_MData_51_Q => n_spm_masters(2).MData(51),
		     spm_ports_m_2_MData_50_Q => n_spm_masters(2).MData(50),
		     spm_ports_m_2_MData_49_Q => n_spm_masters(2).MData(49),
		     spm_ports_m_2_MData_48_Q => n_spm_masters(2).MData(48),
		     spm_ports_m_2_MData_47_Q => n_spm_masters(2).MData(47),
		     spm_ports_m_2_MData_46_Q => n_spm_masters(2).MData(46),
		     spm_ports_m_2_MData_45_Q => n_spm_masters(2).MData(45),
		     spm_ports_m_2_MData_44_Q => n_spm_masters(2).MData(44),
		     spm_ports_m_2_MData_43_Q => n_spm_masters(2).MData(43),
		     spm_ports_m_2_MData_42_Q => n_spm_masters(2).MData(42),
		     spm_ports_m_2_MData_41_Q => n_spm_masters(2).MData(41),
		     spm_ports_m_2_MData_40_Q => n_spm_masters(2).MData(40),
		     spm_ports_m_2_MData_39_Q => n_spm_masters(2).MData(39),
		     spm_ports_m_2_MData_38_Q => n_spm_masters(2).MData(38),
		     spm_ports_m_2_MData_37_Q => n_spm_masters(2).MData(37),
		     spm_ports_m_2_MData_36_Q => n_spm_masters(2).MData(36),
		     spm_ports_m_2_MData_35_Q => n_spm_masters(2).MData(35),
		     spm_ports_m_2_MData_34_Q => n_spm_masters(2).MData(34),
		     spm_ports_m_2_MData_33_Q => n_spm_masters(2).MData(33),
		     spm_ports_m_2_MData_32_Q => n_spm_masters(2).MData(32),
		     spm_ports_m_2_MData_31_Q => n_spm_masters(2).MData(31),
		     spm_ports_m_2_MData_30_Q => n_spm_masters(2).MData(30),
		     spm_ports_m_2_MData_29_Q => n_spm_masters(2).MData(29),
		     spm_ports_m_2_MData_28_Q => n_spm_masters(2).MData(28),
		     spm_ports_m_2_MData_27_Q => n_spm_masters(2).MData(27),
		     spm_ports_m_2_MData_26_Q => n_spm_masters(2).MData(26),
		     spm_ports_m_2_MData_25_Q => n_spm_masters(2).MData(25),
		     spm_ports_m_2_MData_24_Q => n_spm_masters(2).MData(24),
		     spm_ports_m_2_MData_23_Q => n_spm_masters(2).MData(23),
		     spm_ports_m_2_MData_22_Q => n_spm_masters(2).MData(22),
		     spm_ports_m_2_MData_21_Q => n_spm_masters(2).MData(21),
		     spm_ports_m_2_MData_20_Q => n_spm_masters(2).MData(20),
		     spm_ports_m_2_MData_19_Q => n_spm_masters(2).MData(19),
		     spm_ports_m_2_MData_18_Q => n_spm_masters(2).MData(18),
		     spm_ports_m_2_MData_17_Q => n_spm_masters(2).MData(17),
		     spm_ports_m_2_MData_16_Q => n_spm_masters(2).MData(16),
		     spm_ports_m_2_MData_15_Q => n_spm_masters(2).MData(15),
		     spm_ports_m_2_MData_14_Q => n_spm_masters(2).MData(14),
		     spm_ports_m_2_MData_13_Q => n_spm_masters(2).MData(13),
		     spm_ports_m_2_MData_12_Q => n_spm_masters(2).MData(12),
		     spm_ports_m_2_MData_11_Q => n_spm_masters(2).MData(11),
		     spm_ports_m_2_MData_10_Q => n_spm_masters(2).MData(10),
		     spm_ports_m_2_MData_9_Q  => n_spm_masters(2).MData(9),
		     spm_ports_m_2_MData_8_Q  => n_spm_masters(2).MData(8),
		     spm_ports_m_2_MData_7_Q  => n_spm_masters(2).MData(7),
		     spm_ports_m_2_MData_6_Q  => n_spm_masters(2).MData(6),
		     spm_ports_m_2_MData_5_Q  => n_spm_masters(2).MData(5),
		     spm_ports_m_2_MData_4_Q  => n_spm_masters(2).MData(4),
		     spm_ports_m_2_MData_3_Q  => n_spm_masters(2).MData(3),
		     spm_ports_m_2_MData_2_Q  => n_spm_masters(2).MData(2),
		     spm_ports_m_2_MData_1_Q  => n_spm_masters(2).MData(1),
		     spm_ports_m_2_MData_0_Q  => n_spm_masters(2).MData(0),
		     ocp_io_ss_2_SData_31_Q   => p_slaves(2).SData(31),
		     ocp_io_ss_2_SData_30_Q   => p_slaves(2).SData(30),
		     ocp_io_ss_2_SData_29_Q   => p_slaves(2).SData(29),
		     ocp_io_ss_2_SData_28_Q   => p_slaves(2).SData(28),
		     ocp_io_ss_2_SData_27_Q   => p_slaves(2).SData(27),
		     ocp_io_ss_2_SData_26_Q   => p_slaves(2).SData(26),
		     ocp_io_ss_2_SData_25_Q   => p_slaves(2).SData(25),
		     ocp_io_ss_2_SData_24_Q   => p_slaves(2).SData(24),
		     ocp_io_ss_2_SData_23_Q   => p_slaves(2).SData(23),
		     ocp_io_ss_2_SData_22_Q   => p_slaves(2).SData(22),
		     ocp_io_ss_2_SData_21_Q   => p_slaves(2).SData(21),
		     ocp_io_ss_2_SData_20_Q   => p_slaves(2).SData(20),
		     ocp_io_ss_2_SData_19_Q   => p_slaves(2).SData(19),
		     ocp_io_ss_2_SData_18_Q   => p_slaves(2).SData(18),
		     ocp_io_ss_2_SData_17_Q   => p_slaves(2).SData(17),
		     ocp_io_ss_2_SData_16_Q   => p_slaves(2).SData(16),
		     ocp_io_ss_2_SData_15_Q   => p_slaves(2).SData(15),
		     ocp_io_ss_2_SData_14_Q   => p_slaves(2).SData(14),
		     ocp_io_ss_2_SData_13_Q   => p_slaves(2).SData(13),
		     ocp_io_ss_2_SData_12_Q   => p_slaves(2).SData(12),
		     ocp_io_ss_2_SData_11_Q   => p_slaves(2).SData(11),
		     ocp_io_ss_2_SData_10_Q   => p_slaves(2).SData(10),
		     ocp_io_ss_2_SData_9_Q    => p_slaves(2).SData(9),
		     ocp_io_ss_2_SData_8_Q    => p_slaves(2).SData(8),
		     ocp_io_ss_2_SData_7_Q    => p_slaves(2).SData(7),
		     ocp_io_ss_2_SData_6_Q    => p_slaves(2).SData(6),
		     ocp_io_ss_2_SData_5_Q    => p_slaves(2).SData(5),
		     ocp_io_ss_2_SData_4_Q    => p_slaves(2).SData(4),
		     ocp_io_ss_2_SData_3_Q    => p_slaves(2).SData(3),
		     ocp_io_ss_2_SData_2_Q    => p_slaves(2).SData(2),
		     ocp_io_ss_2_SData_1_Q    => p_slaves(2).SData(1),
		     ocp_io_ss_2_SData_0_Q    => p_slaves(2).SData(0),
		     ocp_io_ss_0_SResp_1_Q    => p_slaves(0).SResp(1),
		     ocp_io_ss_0_SResp_0_Q    => p_slaves(0).SResp(0),
		     spm_ports_m_2_MAddr_15_Q => n_spm_masters(2).MAddr(15),
		     spm_ports_m_2_MAddr_14_Q => n_spm_masters(2).MAddr(14),
		     spm_ports_m_2_MAddr_13_Q => n_spm_masters(2).MAddr(13),
		     spm_ports_m_2_MAddr_12_Q => n_spm_masters(2).MAddr(12),
		     spm_ports_m_2_MAddr_11_Q => n_spm_masters(2).MAddr(11),
		     spm_ports_m_2_MAddr_10_Q => n_spm_masters(2).MAddr(10),
		     spm_ports_m_2_MAddr_9_Q  => n_spm_masters(2).MAddr(9),
		     spm_ports_m_2_MAddr_8_Q  => n_spm_masters(2).MAddr(8),
		     spm_ports_m_2_MAddr_7_Q  => n_spm_masters(2).MAddr(7),
		     spm_ports_m_2_MAddr_6_Q  => n_spm_masters(2).MAddr(6),
		     spm_ports_m_2_MAddr_5_Q  => n_spm_masters(2).MAddr(5),
		     spm_ports_m_2_MAddr_4_Q  => n_spm_masters(2).MAddr(4),
		     spm_ports_m_2_MAddr_3_Q  => n_spm_masters(2).MAddr(3),
		     spm_ports_m_2_MAddr_2_Q  => n_spm_masters(2).MAddr(2),
		     spm_ports_m_2_MAddr_1_Q  => n_spm_masters(2).MAddr(1),
		     spm_ports_m_2_MAddr_0_Q  => n_spm_masters(2).MAddr(0),
		     spm_ports_m_1_MData_63_Q => n_spm_masters(1).MData(63),
		     spm_ports_m_1_MData_62_Q => n_spm_masters(1).MData(62),
		     spm_ports_m_1_MData_61_Q => n_spm_masters(1).MData(61),
		     spm_ports_m_1_MData_60_Q => n_spm_masters(1).MData(60),
		     spm_ports_m_1_MData_59_Q => n_spm_masters(1).MData(59),
		     spm_ports_m_1_MData_58_Q => n_spm_masters(1).MData(58),
		     spm_ports_m_1_MData_57_Q => n_spm_masters(1).MData(57),
		     spm_ports_m_1_MData_56_Q => n_spm_masters(1).MData(56),
		     spm_ports_m_1_MData_55_Q => n_spm_masters(1).MData(55),
		     spm_ports_m_1_MData_54_Q => n_spm_masters(1).MData(54),
		     spm_ports_m_1_MData_53_Q => n_spm_masters(1).MData(53),
		     spm_ports_m_1_MData_52_Q => n_spm_masters(1).MData(52),
		     spm_ports_m_1_MData_51_Q => n_spm_masters(1).MData(51),
		     spm_ports_m_1_MData_50_Q => n_spm_masters(1).MData(50),
		     spm_ports_m_1_MData_49_Q => n_spm_masters(1).MData(49),
		     spm_ports_m_1_MData_48_Q => n_spm_masters(1).MData(48),
		     spm_ports_m_1_MData_47_Q => n_spm_masters(1).MData(47),
		     spm_ports_m_1_MData_46_Q => n_spm_masters(1).MData(46),
		     spm_ports_m_1_MData_45_Q => n_spm_masters(1).MData(45),
		     spm_ports_m_1_MData_44_Q => n_spm_masters(1).MData(44),
		     spm_ports_m_1_MData_43_Q => n_spm_masters(1).MData(43),
		     spm_ports_m_1_MData_42_Q => n_spm_masters(1).MData(42),
		     spm_ports_m_1_MData_41_Q => n_spm_masters(1).MData(41),
		     spm_ports_m_1_MData_40_Q => n_spm_masters(1).MData(40),
		     spm_ports_m_1_MData_39_Q => n_spm_masters(1).MData(39),
		     spm_ports_m_1_MData_38_Q => n_spm_masters(1).MData(38),
		     spm_ports_m_1_MData_37_Q => n_spm_masters(1).MData(37),
		     spm_ports_m_1_MData_36_Q => n_spm_masters(1).MData(36),
		     spm_ports_m_1_MData_35_Q => n_spm_masters(1).MData(35),
		     spm_ports_m_1_MData_34_Q => n_spm_masters(1).MData(34),
		     spm_ports_m_1_MData_33_Q => n_spm_masters(1).MData(33),
		     spm_ports_m_1_MData_32_Q => n_spm_masters(1).MData(32),
		     spm_ports_m_1_MData_31_Q => n_spm_masters(1).MData(31),
		     spm_ports_m_1_MData_30_Q => n_spm_masters(1).MData(30),
		     spm_ports_m_1_MData_29_Q => n_spm_masters(1).MData(29),
		     spm_ports_m_1_MData_28_Q => n_spm_masters(1).MData(28),
		     spm_ports_m_1_MData_27_Q => n_spm_masters(1).MData(27),
		     spm_ports_m_1_MData_26_Q => n_spm_masters(1).MData(26),
		     spm_ports_m_1_MData_25_Q => n_spm_masters(1).MData(25),
		     spm_ports_m_1_MData_24_Q => n_spm_masters(1).MData(24),
		     spm_ports_m_1_MData_23_Q => n_spm_masters(1).MData(23),
		     spm_ports_m_1_MData_22_Q => n_spm_masters(1).MData(22),
		     spm_ports_m_1_MData_21_Q => n_spm_masters(1).MData(21),
		     spm_ports_m_1_MData_20_Q => n_spm_masters(1).MData(20),
		     spm_ports_m_1_MData_19_Q => n_spm_masters(1).MData(19),
		     spm_ports_m_1_MData_18_Q => n_spm_masters(1).MData(18),
		     spm_ports_m_1_MData_17_Q => n_spm_masters(1).MData(17),
		     spm_ports_m_1_MData_16_Q => n_spm_masters(1).MData(16),
		     spm_ports_m_1_MData_15_Q => n_spm_masters(1).MData(15),
		     spm_ports_m_1_MData_14_Q => n_spm_masters(1).MData(14),
		     spm_ports_m_1_MData_13_Q => n_spm_masters(1).MData(13),
		     spm_ports_m_1_MData_12_Q => n_spm_masters(1).MData(12),
		     spm_ports_m_1_MData_11_Q => n_spm_masters(1).MData(11),
		     spm_ports_m_1_MData_10_Q => n_spm_masters(1).MData(10),
		     spm_ports_m_1_MData_9_Q  => n_spm_masters(1).MData(9),
		     spm_ports_m_1_MData_8_Q  => n_spm_masters(1).MData(8),
		     spm_ports_m_1_MData_7_Q  => n_spm_masters(1).MData(7),
		     spm_ports_m_1_MData_6_Q  => n_spm_masters(1).MData(6),
		     spm_ports_m_1_MData_5_Q  => n_spm_masters(1).MData(5),
		     spm_ports_m_1_MData_4_Q  => n_spm_masters(1).MData(4),
		     spm_ports_m_1_MData_3_Q  => n_spm_masters(1).MData(3),
		     spm_ports_m_1_MData_2_Q  => n_spm_masters(1).MData(2),
		     spm_ports_m_1_MData_1_Q  => n_spm_masters(1).MData(1),
		     spm_ports_m_1_MData_0_Q  => n_spm_masters(1).MData(0),
		     ocp_io_ss_1_SData_31_Q   => p_slaves(1).SData(31),
		     ocp_io_ss_1_SData_30_Q   => p_slaves(1).SData(30),
		     ocp_io_ss_1_SData_29_Q   => p_slaves(1).SData(29),
		     ocp_io_ss_1_SData_28_Q   => p_slaves(1).SData(28),
		     ocp_io_ss_1_SData_27_Q   => p_slaves(1).SData(27),
		     ocp_io_ss_1_SData_26_Q   => p_slaves(1).SData(26),
		     ocp_io_ss_1_SData_25_Q   => p_slaves(1).SData(25),
		     ocp_io_ss_1_SData_24_Q   => p_slaves(1).SData(24),
		     ocp_io_ss_1_SData_23_Q   => p_slaves(1).SData(23),
		     ocp_io_ss_1_SData_22_Q   => p_slaves(1).SData(22),
		     ocp_io_ss_1_SData_21_Q   => p_slaves(1).SData(21),
		     ocp_io_ss_1_SData_20_Q   => p_slaves(1).SData(20),
		     ocp_io_ss_1_SData_19_Q   => p_slaves(1).SData(19),
		     ocp_io_ss_1_SData_18_Q   => p_slaves(1).SData(18),
		     ocp_io_ss_1_SData_17_Q   => p_slaves(1).SData(17),
		     ocp_io_ss_1_SData_16_Q   => p_slaves(1).SData(16),
		     ocp_io_ss_1_SData_15_Q   => p_slaves(1).SData(15),
		     ocp_io_ss_1_SData_14_Q   => p_slaves(1).SData(14),
		     ocp_io_ss_1_SData_13_Q   => p_slaves(1).SData(13),
		     ocp_io_ss_1_SData_12_Q   => p_slaves(1).SData(12),
		     ocp_io_ss_1_SData_11_Q   => p_slaves(1).SData(11),
		     ocp_io_ss_1_SData_10_Q   => p_slaves(1).SData(10),
		     ocp_io_ss_1_SData_9_Q    => p_slaves(1).SData(9),
		     ocp_io_ss_1_SData_8_Q    => p_slaves(1).SData(8),
		     ocp_io_ss_1_SData_7_Q    => p_slaves(1).SData(7),
		     ocp_io_ss_1_SData_6_Q    => p_slaves(1).SData(6),
		     ocp_io_ss_1_SData_5_Q    => p_slaves(1).SData(5),
		     ocp_io_ss_1_SData_4_Q    => p_slaves(1).SData(4),
		     ocp_io_ss_1_SData_3_Q    => p_slaves(1).SData(3),
		     ocp_io_ss_1_SData_2_Q    => p_slaves(1).SData(2),
		     ocp_io_ss_1_SData_1_Q    => p_slaves(1).SData(1),
		     ocp_io_ss_1_SData_0_Q    => p_slaves(1).SData(0),
		     spm_ports_m_1_MAddr_15_Q => n_spm_masters(1).MAddr(15),
		     spm_ports_m_1_MAddr_14_Q => n_spm_masters(1).MAddr(14),
		     spm_ports_m_1_MAddr_13_Q => n_spm_masters(1).MAddr(13),
		     spm_ports_m_1_MAddr_12_Q => n_spm_masters(1).MAddr(12),
		     spm_ports_m_1_MAddr_11_Q => n_spm_masters(1).MAddr(11),
		     spm_ports_m_1_MAddr_10_Q => n_spm_masters(1).MAddr(10),
		     spm_ports_m_1_MAddr_9_Q  => n_spm_masters(1).MAddr(9),
		     spm_ports_m_1_MAddr_8_Q  => n_spm_masters(1).MAddr(8),
		     spm_ports_m_1_MAddr_7_Q  => n_spm_masters(1).MAddr(7),
		     spm_ports_m_1_MAddr_6_Q  => n_spm_masters(1).MAddr(6),
		     spm_ports_m_1_MAddr_5_Q  => n_spm_masters(1).MAddr(5),
		     spm_ports_m_1_MAddr_4_Q  => n_spm_masters(1).MAddr(4),
		     spm_ports_m_1_MAddr_3_Q  => n_spm_masters(1).MAddr(3),
		     spm_ports_m_1_MAddr_2_Q  => n_spm_masters(1).MAddr(2),
		     spm_ports_m_1_MAddr_1_Q  => n_spm_masters(1).MAddr(1),
		     spm_ports_m_1_MAddr_0_Q  => n_spm_masters(1).MAddr(0),
		     spm_ports_m_0_MData_63_Q => n_spm_masters(0).MData(63),
		     spm_ports_m_0_MData_62_Q => n_spm_masters(0).MData(62),
		     spm_ports_m_0_MData_61_Q => n_spm_masters(0).MData(61),
		     spm_ports_m_0_MData_60_Q => n_spm_masters(0).MData(60),
		     spm_ports_m_0_MData_59_Q => n_spm_masters(0).MData(59),
		     spm_ports_m_0_MData_58_Q => n_spm_masters(0).MData(58),
		     spm_ports_m_0_MData_57_Q => n_spm_masters(0).MData(57),
		     spm_ports_m_0_MData_56_Q => n_spm_masters(0).MData(56),
		     spm_ports_m_0_MData_55_Q => n_spm_masters(0).MData(55),
		     spm_ports_m_0_MData_54_Q => n_spm_masters(0).MData(54),
		     spm_ports_m_0_MData_53_Q => n_spm_masters(0).MData(53),
		     spm_ports_m_0_MData_52_Q => n_spm_masters(0).MData(52),
		     spm_ports_m_0_MData_51_Q => n_spm_masters(0).MData(51),
		     spm_ports_m_0_MData_50_Q => n_spm_masters(0).MData(50),
		     spm_ports_m_0_MData_49_Q => n_spm_masters(0).MData(49),
		     spm_ports_m_0_MData_48_Q => n_spm_masters(0).MData(48),
		     spm_ports_m_0_MData_47_Q => n_spm_masters(0).MData(47),
		     spm_ports_m_0_MData_46_Q => n_spm_masters(0).MData(46),
		     spm_ports_m_0_MData_45_Q => n_spm_masters(0).MData(45),
		     spm_ports_m_0_MData_44_Q => n_spm_masters(0).MData(44),
		     spm_ports_m_0_MData_43_Q => n_spm_masters(0).MData(43),
		     spm_ports_m_0_MData_42_Q => n_spm_masters(0).MData(42),
		     spm_ports_m_0_MData_41_Q => n_spm_masters(0).MData(41),
		     spm_ports_m_0_MData_40_Q => n_spm_masters(0).MData(40),
		     spm_ports_m_0_MData_39_Q => n_spm_masters(0).MData(39),
		     spm_ports_m_0_MData_38_Q => n_spm_masters(0).MData(38),
		     spm_ports_m_0_MData_37_Q => n_spm_masters(0).MData(37),
		     spm_ports_m_0_MData_36_Q => n_spm_masters(0).MData(36),
		     spm_ports_m_0_MData_35_Q => n_spm_masters(0).MData(35),
		     spm_ports_m_0_MData_34_Q => n_spm_masters(0).MData(34),
		     spm_ports_m_0_MData_33_Q => n_spm_masters(0).MData(33),
		     spm_ports_m_0_MData_32_Q => n_spm_masters(0).MData(32),
		     spm_ports_m_0_MData_31_Q => n_spm_masters(0).MData(31),
		     spm_ports_m_0_MData_30_Q => n_spm_masters(0).MData(30),
		     spm_ports_m_0_MData_29_Q => n_spm_masters(0).MData(29),
		     spm_ports_m_0_MData_28_Q => n_spm_masters(0).MData(28),
		     spm_ports_m_0_MData_27_Q => n_spm_masters(0).MData(27),
		     spm_ports_m_0_MData_26_Q => n_spm_masters(0).MData(26),
		     spm_ports_m_0_MData_25_Q => n_spm_masters(0).MData(25),
		     spm_ports_m_0_MData_24_Q => n_spm_masters(0).MData(24),
		     spm_ports_m_0_MData_23_Q => n_spm_masters(0).MData(23),
		     spm_ports_m_0_MData_22_Q => n_spm_masters(0).MData(22),
		     spm_ports_m_0_MData_21_Q => n_spm_masters(0).MData(21),
		     spm_ports_m_0_MData_20_Q => n_spm_masters(0).MData(20),
		     spm_ports_m_0_MData_19_Q => n_spm_masters(0).MData(19),
		     spm_ports_m_0_MData_18_Q => n_spm_masters(0).MData(18),
		     spm_ports_m_0_MData_17_Q => n_spm_masters(0).MData(17),
		     spm_ports_m_0_MData_16_Q => n_spm_masters(0).MData(16),
		     spm_ports_m_0_MData_15_Q => n_spm_masters(0).MData(15),
		     spm_ports_m_0_MData_14_Q => n_spm_masters(0).MData(14),
		     spm_ports_m_0_MData_13_Q => n_spm_masters(0).MData(13),
		     spm_ports_m_0_MData_12_Q => n_spm_masters(0).MData(12),
		     spm_ports_m_0_MData_11_Q => n_spm_masters(0).MData(11),
		     spm_ports_m_0_MData_10_Q => n_spm_masters(0).MData(10),
		     spm_ports_m_0_MData_9_Q  => n_spm_masters(0).MData(9),
		     spm_ports_m_0_MData_8_Q  => n_spm_masters(0).MData(8),
		     spm_ports_m_0_MData_7_Q  => n_spm_masters(0).MData(7),
		     spm_ports_m_0_MData_6_Q  => n_spm_masters(0).MData(6),
		     spm_ports_m_0_MData_5_Q  => n_spm_masters(0).MData(5),
		     spm_ports_m_0_MData_4_Q  => n_spm_masters(0).MData(4),
		     spm_ports_m_0_MData_3_Q  => n_spm_masters(0).MData(3),
		     spm_ports_m_0_MData_2_Q  => n_spm_masters(0).MData(2),
		     spm_ports_m_0_MData_1_Q  => n_spm_masters(0).MData(1),
		     spm_ports_m_0_MData_0_Q  => n_spm_masters(0).MData(0),
		     ocp_io_ms_0_MData_31_Q   => p_masters(0).MData(31),
		     ocp_io_ms_0_MData_30_Q   => p_masters(0).MData(30),
		     ocp_io_ms_0_MData_29_Q   => p_masters(0).MData(29),
		     ocp_io_ms_0_MData_28_Q   => p_masters(0).MData(28),
		     ocp_io_ms_0_MData_27_Q   => p_masters(0).MData(27),
		     ocp_io_ms_0_MData_26_Q   => p_masters(0).MData(26),
		     ocp_io_ms_0_MData_25_Q   => p_masters(0).MData(25),
		     ocp_io_ms_0_MData_24_Q   => p_masters(0).MData(24),
		     ocp_io_ms_0_MData_23_Q   => p_masters(0).MData(23),
		     ocp_io_ms_0_MData_22_Q   => p_masters(0).MData(22),
		     ocp_io_ms_0_MData_21_Q   => p_masters(0).MData(21),
		     ocp_io_ms_0_MData_20_Q   => p_masters(0).MData(20),
		     ocp_io_ms_0_MData_19_Q   => p_masters(0).MData(19),
		     ocp_io_ms_0_MData_18_Q   => p_masters(0).MData(18),
		     ocp_io_ms_0_MData_17_Q   => p_masters(0).MData(17),
		     ocp_io_ms_0_MData_16_Q   => p_masters(0).MData(16),
		     ocp_io_ms_0_MData_15_Q   => p_masters(0).MData(15),
		     ocp_io_ms_0_MData_14_Q   => p_masters(0).MData(14),
		     ocp_io_ms_0_MData_13_Q   => p_masters(0).MData(13),
		     ocp_io_ms_0_MData_12_Q   => p_masters(0).MData(12),
		     ocp_io_ms_0_MData_11_Q   => p_masters(0).MData(11),
		     ocp_io_ms_0_MData_10_Q   => p_masters(0).MData(10),
		     ocp_io_ms_0_MData_9_Q    => p_masters(0).MData(9),
		     ocp_io_ms_0_MData_8_Q    => p_masters(0).MData(8),
		     ocp_io_ms_0_MData_7_Q    => p_masters(0).MData(7),
		     ocp_io_ms_0_MData_6_Q    => p_masters(0).MData(6),
		     ocp_io_ms_0_MData_5_Q    => p_masters(0).MData(5),
		     ocp_io_ms_0_MData_4_Q    => p_masters(0).MData(4),
		     ocp_io_ms_0_MData_3_Q    => p_masters(0).MData(3),
		     ocp_io_ms_0_MData_2_Q    => p_masters(0).MData(2),
		     ocp_io_ms_0_MData_1_Q    => p_masters(0).MData(1),
		     ocp_io_ms_0_MData_0_Q    => p_masters(0).MData(0),
		     spm_ports_s_1_SData_63_Q => n_spm_slaves(1).SData(63),
		     spm_ports_s_1_SData_62_Q => n_spm_slaves(1).SData(62),
		     spm_ports_s_1_SData_61_Q => n_spm_slaves(1).SData(61),
		     spm_ports_s_1_SData_60_Q => n_spm_slaves(1).SData(60),
		     spm_ports_s_1_SData_59_Q => n_spm_slaves(1).SData(59),
		     spm_ports_s_1_SData_58_Q => n_spm_slaves(1).SData(58),
		     spm_ports_s_1_SData_57_Q => n_spm_slaves(1).SData(57),
		     spm_ports_s_1_SData_56_Q => n_spm_slaves(1).SData(56),
		     spm_ports_s_1_SData_55_Q => n_spm_slaves(1).SData(55),
		     spm_ports_s_1_SData_54_Q => n_spm_slaves(1).SData(54),
		     spm_ports_s_1_SData_53_Q => n_spm_slaves(1).SData(53),
		     spm_ports_s_1_SData_52_Q => n_spm_slaves(1).SData(52),
		     spm_ports_s_1_SData_51_Q => n_spm_slaves(1).SData(51),
		     spm_ports_s_1_SData_50_Q => n_spm_slaves(1).SData(50),
		     spm_ports_s_1_SData_49_Q => n_spm_slaves(1).SData(49),
		     spm_ports_s_1_SData_48_Q => n_spm_slaves(1).SData(48),
		     spm_ports_s_1_SData_47_Q => n_spm_slaves(1).SData(47),
		     spm_ports_s_1_SData_46_Q => n_spm_slaves(1).SData(46),
		     spm_ports_s_1_SData_45_Q => n_spm_slaves(1).SData(45),
		     spm_ports_s_1_SData_44_Q => n_spm_slaves(1).SData(44),
		     spm_ports_s_1_SData_43_Q => n_spm_slaves(1).SData(43),
		     spm_ports_s_1_SData_42_Q => n_spm_slaves(1).SData(42),
		     spm_ports_s_1_SData_41_Q => n_spm_slaves(1).SData(41),
		     spm_ports_s_1_SData_40_Q => n_spm_slaves(1).SData(40),
		     spm_ports_s_1_SData_39_Q => n_spm_slaves(1).SData(39),
		     spm_ports_s_1_SData_38_Q => n_spm_slaves(1).SData(38),
		     spm_ports_s_1_SData_37_Q => n_spm_slaves(1).SData(37),
		     spm_ports_s_1_SData_36_Q => n_spm_slaves(1).SData(36),
		     spm_ports_s_1_SData_35_Q => n_spm_slaves(1).SData(35),
		     spm_ports_s_1_SData_34_Q => n_spm_slaves(1).SData(34),
		     spm_ports_s_1_SData_33_Q => n_spm_slaves(1).SData(33),
		     spm_ports_s_1_SData_32_Q => n_spm_slaves(1).SData(32),
		     spm_ports_s_1_SData_31_Q => n_spm_slaves(1).SData(31),
		     spm_ports_s_1_SData_30_Q => n_spm_slaves(1).SData(30),
		     spm_ports_s_1_SData_29_Q => n_spm_slaves(1).SData(29),
		     spm_ports_s_1_SData_28_Q => n_spm_slaves(1).SData(28),
		     spm_ports_s_1_SData_27_Q => n_spm_slaves(1).SData(27),
		     spm_ports_s_1_SData_26_Q => n_spm_slaves(1).SData(26),
		     spm_ports_s_1_SData_25_Q => n_spm_slaves(1).SData(25),
		     spm_ports_s_1_SData_24_Q => n_spm_slaves(1).SData(24),
		     spm_ports_s_1_SData_23_Q => n_spm_slaves(1).SData(23),
		     spm_ports_s_1_SData_22_Q => n_spm_slaves(1).SData(22),
		     spm_ports_s_1_SData_21_Q => n_spm_slaves(1).SData(21),
		     spm_ports_s_1_SData_20_Q => n_spm_slaves(1).SData(20),
		     spm_ports_s_1_SData_19_Q => n_spm_slaves(1).SData(19),
		     spm_ports_s_1_SData_18_Q => n_spm_slaves(1).SData(18),
		     spm_ports_s_1_SData_17_Q => n_spm_slaves(1).SData(17),
		     spm_ports_s_1_SData_16_Q => n_spm_slaves(1).SData(16),
		     spm_ports_s_1_SData_15_Q => n_spm_slaves(1).SData(15),
		     spm_ports_s_1_SData_14_Q => n_spm_slaves(1).SData(14),
		     spm_ports_s_1_SData_13_Q => n_spm_slaves(1).SData(13),
		     spm_ports_s_1_SData_12_Q => n_spm_slaves(1).SData(12),
		     spm_ports_s_1_SData_11_Q => n_spm_slaves(1).SData(11),
		     spm_ports_s_1_SData_10_Q => n_spm_slaves(1).SData(10),
		     spm_ports_s_1_SData_9_Q  => n_spm_slaves(1).SData(9),
		     spm_ports_s_1_SData_8_Q  => n_spm_slaves(1).SData(8),
		     spm_ports_s_1_SData_7_Q  => n_spm_slaves(1).SData(7),
		     spm_ports_s_1_SData_6_Q  => n_spm_slaves(1).SData(6),
		     spm_ports_s_1_SData_5_Q  => n_spm_slaves(1).SData(5),
		     spm_ports_s_1_SData_4_Q  => n_spm_slaves(1).SData(4),
		     spm_ports_s_1_SData_3_Q  => n_spm_slaves(1).SData(3),
		     spm_ports_s_1_SData_2_Q  => n_spm_slaves(1).SData(2),
		     spm_ports_s_1_SData_1_Q  => n_spm_slaves(1).SData(1),
		     spm_ports_s_1_SData_0_Q  => n_spm_slaves(1).SData(0),
		     ocp_io_ms_0_MAddr_31_Q   => p_masters(0).MAddr(31),
		     ocp_io_ms_0_MAddr_30_Q   => p_masters(0).MAddr(30),
		     ocp_io_ms_0_MAddr_29_Q   => p_masters(0).MAddr(29),
		     ocp_io_ms_0_MAddr_28_Q   => p_masters(0).MAddr(28),
		     ocp_io_ms_0_MAddr_27_Q   => p_masters(0).MAddr(27),
		     ocp_io_ms_0_MAddr_26_Q   => p_masters(0).MAddr(26),
		     ocp_io_ms_0_MAddr_25_Q   => p_masters(0).MAddr(25),
		     ocp_io_ms_0_MAddr_24_Q   => p_masters(0).MAddr(24),
		     ocp_io_ms_0_MAddr_23_Q   => p_masters(0).MAddr(23),
		     ocp_io_ms_0_MAddr_22_Q   => p_masters(0).MAddr(22),
		     ocp_io_ms_0_MAddr_21_Q   => p_masters(0).MAddr(21),
		     ocp_io_ms_0_MAddr_20_Q   => p_masters(0).MAddr(20),
		     ocp_io_ms_0_MAddr_19_Q   => p_masters(0).MAddr(19),
		     ocp_io_ms_0_MAddr_18_Q   => p_masters(0).MAddr(18),
		     ocp_io_ms_0_MAddr_17_Q   => p_masters(0).MAddr(17),
		     ocp_io_ms_0_MAddr_16_Q   => p_masters(0).MAddr(16),
		     ocp_io_ms_0_MAddr_15_Q   => p_masters(0).MAddr(15),
		     ocp_io_ms_0_MAddr_14_Q   => p_masters(0).MAddr(14),
		     ocp_io_ms_0_MAddr_13_Q   => p_masters(0).MAddr(13),
		     ocp_io_ms_0_MAddr_12_Q   => p_masters(0).MAddr(12),
		     ocp_io_ms_0_MAddr_11_Q   => p_masters(0).MAddr(11),
		     ocp_io_ms_0_MAddr_10_Q   => p_masters(0).MAddr(10),
		     ocp_io_ms_0_MAddr_9_Q    => p_masters(0).MAddr(9),
		     ocp_io_ms_0_MAddr_8_Q    => p_masters(0).MAddr(8),
		     ocp_io_ms_0_MAddr_7_Q    => p_masters(0).MAddr(7),
		     ocp_io_ms_0_MAddr_6_Q    => p_masters(0).MAddr(6),
		     ocp_io_ms_0_MAddr_5_Q    => p_masters(0).MAddr(5),
		     ocp_io_ms_0_MAddr_4_Q    => p_masters(0).MAddr(4),
		     ocp_io_ms_0_MAddr_3_Q    => p_masters(0).MAddr(3),
		     ocp_io_ms_0_MAddr_2_Q    => p_masters(0).MAddr(2),
		     ocp_io_ms_0_MAddr_1_Q    => p_masters(0).MAddr(1),
		     ocp_io_ms_0_MAddr_0_Q    => p_masters(0).MAddr(0),
		     spm_ports_s_0_SData_63_Q => n_spm_slaves(0).SData(63),
		     spm_ports_s_0_SData_62_Q => n_spm_slaves(0).SData(62),
		     spm_ports_s_0_SData_61_Q => n_spm_slaves(0).SData(61),
		     spm_ports_s_0_SData_60_Q => n_spm_slaves(0).SData(60),
		     spm_ports_s_0_SData_59_Q => n_spm_slaves(0).SData(59),
		     spm_ports_s_0_SData_58_Q => n_spm_slaves(0).SData(58),
		     spm_ports_s_0_SData_57_Q => n_spm_slaves(0).SData(57),
		     spm_ports_s_0_SData_56_Q => n_spm_slaves(0).SData(56),
		     spm_ports_s_0_SData_55_Q => n_spm_slaves(0).SData(55),
		     spm_ports_s_0_SData_54_Q => n_spm_slaves(0).SData(54),
		     spm_ports_s_0_SData_53_Q => n_spm_slaves(0).SData(53),
		     spm_ports_s_0_SData_52_Q => n_spm_slaves(0).SData(52),
		     spm_ports_s_0_SData_51_Q => n_spm_slaves(0).SData(51),
		     spm_ports_s_0_SData_50_Q => n_spm_slaves(0).SData(50),
		     spm_ports_s_0_SData_49_Q => n_spm_slaves(0).SData(49),
		     spm_ports_s_0_SData_48_Q => n_spm_slaves(0).SData(48),
		     spm_ports_s_0_SData_47_Q => n_spm_slaves(0).SData(47),
		     spm_ports_s_0_SData_46_Q => n_spm_slaves(0).SData(46),
		     spm_ports_s_0_SData_45_Q => n_spm_slaves(0).SData(45),
		     spm_ports_s_0_SData_44_Q => n_spm_slaves(0).SData(44),
		     spm_ports_s_0_SData_43_Q => n_spm_slaves(0).SData(43),
		     spm_ports_s_0_SData_42_Q => n_spm_slaves(0).SData(42),
		     spm_ports_s_0_SData_41_Q => n_spm_slaves(0).SData(41),
		     spm_ports_s_0_SData_40_Q => n_spm_slaves(0).SData(40),
		     spm_ports_s_0_SData_39_Q => n_spm_slaves(0).SData(39),
		     spm_ports_s_0_SData_38_Q => n_spm_slaves(0).SData(38),
		     spm_ports_s_0_SData_37_Q => n_spm_slaves(0).SData(37),
		     spm_ports_s_0_SData_36_Q => n_spm_slaves(0).SData(36),
		     spm_ports_s_0_SData_35_Q => n_spm_slaves(0).SData(35),
		     spm_ports_s_0_SData_34_Q => n_spm_slaves(0).SData(34),
		     spm_ports_s_0_SData_33_Q => n_spm_slaves(0).SData(33),
		     spm_ports_s_0_SData_32_Q => n_spm_slaves(0).SData(32),
		     spm_ports_s_0_SData_31_Q => n_spm_slaves(0).SData(31),
		     spm_ports_s_0_SData_30_Q => n_spm_slaves(0).SData(30),
		     spm_ports_s_0_SData_29_Q => n_spm_slaves(0).SData(29),
		     spm_ports_s_0_SData_28_Q => n_spm_slaves(0).SData(28),
		     spm_ports_s_0_SData_27_Q => n_spm_slaves(0).SData(27),
		     spm_ports_s_0_SData_26_Q => n_spm_slaves(0).SData(26),
		     spm_ports_s_0_SData_25_Q => n_spm_slaves(0).SData(25),
		     spm_ports_s_0_SData_24_Q => n_spm_slaves(0).SData(24),
		     spm_ports_s_0_SData_23_Q => n_spm_slaves(0).SData(23),
		     spm_ports_s_0_SData_22_Q => n_spm_slaves(0).SData(22),
		     spm_ports_s_0_SData_21_Q => n_spm_slaves(0).SData(21),
		     spm_ports_s_0_SData_20_Q => n_spm_slaves(0).SData(20),
		     spm_ports_s_0_SData_19_Q => n_spm_slaves(0).SData(19),
		     spm_ports_s_0_SData_18_Q => n_spm_slaves(0).SData(18),
		     spm_ports_s_0_SData_17_Q => n_spm_slaves(0).SData(17),
		     spm_ports_s_0_SData_16_Q => n_spm_slaves(0).SData(16),
		     spm_ports_s_0_SData_15_Q => n_spm_slaves(0).SData(15),
		     spm_ports_s_0_SData_14_Q => n_spm_slaves(0).SData(14),
		     spm_ports_s_0_SData_13_Q => n_spm_slaves(0).SData(13),
		     spm_ports_s_0_SData_12_Q => n_spm_slaves(0).SData(12),
		     spm_ports_s_0_SData_11_Q => n_spm_slaves(0).SData(11),
		     spm_ports_s_0_SData_10_Q => n_spm_slaves(0).SData(10),
		     spm_ports_s_0_SData_9_Q  => n_spm_slaves(0).SData(9),
		     spm_ports_s_0_SData_8_Q  => n_spm_slaves(0).SData(8),
		     spm_ports_s_0_SData_7_Q  => n_spm_slaves(0).SData(7),
		     spm_ports_s_0_SData_6_Q  => n_spm_slaves(0).SData(6),
		     spm_ports_s_0_SData_5_Q  => n_spm_slaves(0).SData(5),
		     spm_ports_s_0_SData_4_Q  => n_spm_slaves(0).SData(4),
		     spm_ports_s_0_SData_3_Q  => n_spm_slaves(0).SData(3),
		     spm_ports_s_0_SData_2_Q  => n_spm_slaves(0).SData(2),
		     spm_ports_s_0_SData_1_Q  => n_spm_slaves(0).SData(1),
		     spm_ports_s_0_SData_0_Q  => n_spm_slaves(0).SData(0),
		     ocp_io_ms_3_MByteEn_3_Q  => p_masters(3).MByteEn(3),
		     ocp_io_ms_3_MByteEn_2_Q  => p_masters(3).MByteEn(2),
		     ocp_io_ms_3_MByteEn_1_Q  => p_masters(3).MByteEn(1),
		     ocp_io_ms_3_MByteEn_0_Q  => p_masters(3).MByteEn(0),
		     ocp_io_ms_3_MData_31_Q   => p_masters(3).MData(31),
		     ocp_io_ms_3_MData_30_Q   => p_masters(3).MData(30),
		     ocp_io_ms_3_MData_29_Q   => p_masters(3).MData(29),
		     ocp_io_ms_3_MData_28_Q   => p_masters(3).MData(28),
		     ocp_io_ms_3_MData_27_Q   => p_masters(3).MData(27),
		     ocp_io_ms_3_MData_26_Q   => p_masters(3).MData(26),
		     ocp_io_ms_3_MData_25_Q   => p_masters(3).MData(25),
		     ocp_io_ms_3_MData_24_Q   => p_masters(3).MData(24),
		     ocp_io_ms_3_MData_23_Q   => p_masters(3).MData(23),
		     ocp_io_ms_3_MData_22_Q   => p_masters(3).MData(22),
		     ocp_io_ms_3_MData_21_Q   => p_masters(3).MData(21),
		     ocp_io_ms_3_MData_20_Q   => p_masters(3).MData(20),
		     ocp_io_ms_3_MData_19_Q   => p_masters(3).MData(19),
		     ocp_io_ms_3_MData_18_Q   => p_masters(3).MData(18),
		     ocp_io_ms_3_MData_17_Q   => p_masters(3).MData(17),
		     ocp_io_ms_3_MData_16_Q   => p_masters(3).MData(16),
		     ocp_io_ms_3_MData_15_Q   => p_masters(3).MData(15),
		     ocp_io_ms_3_MData_14_Q   => p_masters(3).MData(14),
		     ocp_io_ms_3_MData_13_Q   => p_masters(3).MData(13),
		     ocp_io_ms_3_MData_12_Q   => p_masters(3).MData(12),
		     ocp_io_ms_3_MData_11_Q   => p_masters(3).MData(11),
		     ocp_io_ms_3_MData_10_Q   => p_masters(3).MData(10),
		     ocp_io_ms_3_MData_9_Q    => p_masters(3).MData(9),
		     ocp_io_ms_3_MData_8_Q    => p_masters(3).MData(8),
		     ocp_io_ms_3_MData_7_Q    => p_masters(3).MData(7),
		     ocp_io_ms_3_MData_6_Q    => p_masters(3).MData(6),
		     ocp_io_ms_3_MData_5_Q    => p_masters(3).MData(5),
		     ocp_io_ms_3_MData_4_Q    => p_masters(3).MData(4),
		     ocp_io_ms_3_MData_3_Q    => p_masters(3).MData(3),
		     ocp_io_ms_3_MData_2_Q    => p_masters(3).MData(2),
		     ocp_io_ms_3_MData_1_Q    => p_masters(3).MData(1),
		     ocp_io_ms_3_MData_0_Q    => p_masters(3).MData(0),
		     ocp_io_ms_2_MByteEn_3_Q  => p_masters(2).MByteEn(3),
		     ocp_io_ms_2_MByteEn_2_Q  => p_masters(2).MByteEn(2),
		     ocp_io_ms_2_MByteEn_1_Q  => p_masters(2).MByteEn(1),
		     ocp_io_ms_2_MByteEn_0_Q  => p_masters(2).MByteEn(0),
		     ocp_io_ms_3_MAddr_31_Q   => p_masters(3).MAddr(31),
		     ocp_io_ms_3_MAddr_30_Q   => p_masters(3).MAddr(30),
		     ocp_io_ms_3_MAddr_29_Q   => p_masters(3).MAddr(29),
		     ocp_io_ms_3_MAddr_28_Q   => p_masters(3).MAddr(28),
		     ocp_io_ms_3_MAddr_27_Q   => p_masters(3).MAddr(27),
		     ocp_io_ms_3_MAddr_26_Q   => p_masters(3).MAddr(26),
		     ocp_io_ms_3_MAddr_25_Q   => p_masters(3).MAddr(25),
		     ocp_io_ms_3_MAddr_24_Q   => p_masters(3).MAddr(24),
		     ocp_io_ms_3_MAddr_23_Q   => p_masters(3).MAddr(23),
		     ocp_io_ms_3_MAddr_22_Q   => p_masters(3).MAddr(22),
		     ocp_io_ms_3_MAddr_21_Q   => p_masters(3).MAddr(21),
		     ocp_io_ms_3_MAddr_20_Q   => p_masters(3).MAddr(20),
		     ocp_io_ms_3_MAddr_19_Q   => p_masters(3).MAddr(19),
		     ocp_io_ms_3_MAddr_18_Q   => p_masters(3).MAddr(18),
		     ocp_io_ms_3_MAddr_17_Q   => p_masters(3).MAddr(17),
		     ocp_io_ms_3_MAddr_16_Q   => p_masters(3).MAddr(16),
		     ocp_io_ms_3_MAddr_15_Q   => p_masters(3).MAddr(15),
		     ocp_io_ms_3_MAddr_14_Q   => p_masters(3).MAddr(14),
		     ocp_io_ms_3_MAddr_13_Q   => p_masters(3).MAddr(13),
		     ocp_io_ms_3_MAddr_12_Q   => p_masters(3).MAddr(12),
		     ocp_io_ms_3_MAddr_11_Q   => p_masters(3).MAddr(11),
		     ocp_io_ms_3_MAddr_10_Q   => p_masters(3).MAddr(10),
		     ocp_io_ms_3_MAddr_9_Q    => p_masters(3).MAddr(9),
		     ocp_io_ms_3_MAddr_8_Q    => p_masters(3).MAddr(8),
		     ocp_io_ms_3_MAddr_7_Q    => p_masters(3).MAddr(7),
		     ocp_io_ms_3_MAddr_6_Q    => p_masters(3).MAddr(6),
		     ocp_io_ms_3_MAddr_5_Q    => p_masters(3).MAddr(5),
		     ocp_io_ms_3_MAddr_4_Q    => p_masters(3).MAddr(4),
		     ocp_io_ms_3_MAddr_3_Q    => p_masters(3).MAddr(3),
		     ocp_io_ms_3_MAddr_2_Q    => p_masters(3).MAddr(2),
		     ocp_io_ms_3_MAddr_1_Q    => p_masters(3).MAddr(1),
		     ocp_io_ms_3_MAddr_0_Q    => p_masters(3).MAddr(0),
		     ocp_io_ms_2_MData_31_Q   => p_masters(2).MData(31),
		     ocp_io_ms_2_MData_30_Q   => p_masters(2).MData(30),
		     ocp_io_ms_2_MData_29_Q   => p_masters(2).MData(29),
		     ocp_io_ms_2_MData_28_Q   => p_masters(2).MData(28),
		     ocp_io_ms_2_MData_27_Q   => p_masters(2).MData(27),
		     ocp_io_ms_2_MData_26_Q   => p_masters(2).MData(26),
		     ocp_io_ms_2_MData_25_Q   => p_masters(2).MData(25),
		     ocp_io_ms_2_MData_24_Q   => p_masters(2).MData(24),
		     ocp_io_ms_2_MData_23_Q   => p_masters(2).MData(23),
		     ocp_io_ms_2_MData_22_Q   => p_masters(2).MData(22),
		     ocp_io_ms_2_MData_21_Q   => p_masters(2).MData(21),
		     ocp_io_ms_2_MData_20_Q   => p_masters(2).MData(20),
		     ocp_io_ms_2_MData_19_Q   => p_masters(2).MData(19),
		     ocp_io_ms_2_MData_18_Q   => p_masters(2).MData(18),
		     ocp_io_ms_2_MData_17_Q   => p_masters(2).MData(17),
		     ocp_io_ms_2_MData_16_Q   => p_masters(2).MData(16),
		     ocp_io_ms_2_MData_15_Q   => p_masters(2).MData(15),
		     ocp_io_ms_2_MData_14_Q   => p_masters(2).MData(14),
		     ocp_io_ms_2_MData_13_Q   => p_masters(2).MData(13),
		     ocp_io_ms_2_MData_12_Q   => p_masters(2).MData(12),
		     ocp_io_ms_2_MData_11_Q   => p_masters(2).MData(11),
		     ocp_io_ms_2_MData_10_Q   => p_masters(2).MData(10),
		     ocp_io_ms_2_MData_9_Q    => p_masters(2).MData(9),
		     ocp_io_ms_2_MData_8_Q    => p_masters(2).MData(8),
		     ocp_io_ms_2_MData_7_Q    => p_masters(2).MData(7),
		     ocp_io_ms_2_MData_6_Q    => p_masters(2).MData(6),
		     ocp_io_ms_2_MData_5_Q    => p_masters(2).MData(5),
		     ocp_io_ms_2_MData_4_Q    => p_masters(2).MData(4),
		     ocp_io_ms_2_MData_3_Q    => p_masters(2).MData(3),
		     ocp_io_ms_2_MData_2_Q    => p_masters(2).MData(2),
		     ocp_io_ms_2_MData_1_Q    => p_masters(2).MData(1),
		     ocp_io_ms_2_MData_0_Q    => p_masters(2).MData(0),
		     ocp_io_ms_1_MByteEn_3_Q  => p_masters(1).MByteEn(3),
		     ocp_io_ms_1_MByteEn_2_Q  => p_masters(1).MByteEn(2),
		     ocp_io_ms_1_MByteEn_1_Q  => p_masters(1).MByteEn(1),
		     ocp_io_ms_1_MByteEn_0_Q  => p_masters(1).MByteEn(0),
		     spm_ports_s_3_SData_63_Q => n_spm_slaves(3).SData(63),
		     spm_ports_s_3_SData_62_Q => n_spm_slaves(3).SData(62),
		     spm_ports_s_3_SData_61_Q => n_spm_slaves(3).SData(61),
		     spm_ports_s_3_SData_60_Q => n_spm_slaves(3).SData(60),
		     spm_ports_s_3_SData_59_Q => n_spm_slaves(3).SData(59),
		     spm_ports_s_3_SData_58_Q => n_spm_slaves(3).SData(58),
		     spm_ports_s_3_SData_57_Q => n_spm_slaves(3).SData(57),
		     spm_ports_s_3_SData_56_Q => n_spm_slaves(3).SData(56),
		     spm_ports_s_3_SData_55_Q => n_spm_slaves(3).SData(55),
		     spm_ports_s_3_SData_54_Q => n_spm_slaves(3).SData(54),
		     spm_ports_s_3_SData_53_Q => n_spm_slaves(3).SData(53),
		     spm_ports_s_3_SData_52_Q => n_spm_slaves(3).SData(52),
		     spm_ports_s_3_SData_51_Q => n_spm_slaves(3).SData(51),
		     spm_ports_s_3_SData_50_Q => n_spm_slaves(3).SData(50),
		     spm_ports_s_3_SData_49_Q => n_spm_slaves(3).SData(49),
		     spm_ports_s_3_SData_48_Q => n_spm_slaves(3).SData(48),
		     spm_ports_s_3_SData_47_Q => n_spm_slaves(3).SData(47),
		     spm_ports_s_3_SData_46_Q => n_spm_slaves(3).SData(46),
		     spm_ports_s_3_SData_45_Q => n_spm_slaves(3).SData(45),
		     spm_ports_s_3_SData_44_Q => n_spm_slaves(3).SData(44),
		     spm_ports_s_3_SData_43_Q => n_spm_slaves(3).SData(43),
		     spm_ports_s_3_SData_42_Q => n_spm_slaves(3).SData(42),
		     spm_ports_s_3_SData_41_Q => n_spm_slaves(3).SData(41),
		     spm_ports_s_3_SData_40_Q => n_spm_slaves(3).SData(40),
		     spm_ports_s_3_SData_39_Q => n_spm_slaves(3).SData(39),
		     spm_ports_s_3_SData_38_Q => n_spm_slaves(3).SData(38),
		     spm_ports_s_3_SData_37_Q => n_spm_slaves(3).SData(37),
		     spm_ports_s_3_SData_36_Q => n_spm_slaves(3).SData(36),
		     spm_ports_s_3_SData_35_Q => n_spm_slaves(3).SData(35),
		     spm_ports_s_3_SData_34_Q => n_spm_slaves(3).SData(34),
		     spm_ports_s_3_SData_33_Q => n_spm_slaves(3).SData(33),
		     spm_ports_s_3_SData_32_Q => n_spm_slaves(3).SData(32),
		     spm_ports_s_3_SData_31_Q => n_spm_slaves(3).SData(31),
		     spm_ports_s_3_SData_30_Q => n_spm_slaves(3).SData(30),
		     spm_ports_s_3_SData_29_Q => n_spm_slaves(3).SData(29),
		     spm_ports_s_3_SData_28_Q => n_spm_slaves(3).SData(28),
		     spm_ports_s_3_SData_27_Q => n_spm_slaves(3).SData(27),
		     spm_ports_s_3_SData_26_Q => n_spm_slaves(3).SData(26),
		     spm_ports_s_3_SData_25_Q => n_spm_slaves(3).SData(25),
		     spm_ports_s_3_SData_24_Q => n_spm_slaves(3).SData(24),
		     spm_ports_s_3_SData_23_Q => n_spm_slaves(3).SData(23),
		     spm_ports_s_3_SData_22_Q => n_spm_slaves(3).SData(22),
		     spm_ports_s_3_SData_21_Q => n_spm_slaves(3).SData(21),
		     spm_ports_s_3_SData_20_Q => n_spm_slaves(3).SData(20),
		     spm_ports_s_3_SData_19_Q => n_spm_slaves(3).SData(19),
		     spm_ports_s_3_SData_18_Q => n_spm_slaves(3).SData(18),
		     spm_ports_s_3_SData_17_Q => n_spm_slaves(3).SData(17),
		     spm_ports_s_3_SData_16_Q => n_spm_slaves(3).SData(16),
		     spm_ports_s_3_SData_15_Q => n_spm_slaves(3).SData(15),
		     spm_ports_s_3_SData_14_Q => n_spm_slaves(3).SData(14),
		     spm_ports_s_3_SData_13_Q => n_spm_slaves(3).SData(13),
		     spm_ports_s_3_SData_12_Q => n_spm_slaves(3).SData(12),
		     spm_ports_s_3_SData_11_Q => n_spm_slaves(3).SData(11),
		     spm_ports_s_3_SData_10_Q => n_spm_slaves(3).SData(10),
		     spm_ports_s_3_SData_9_Q  => n_spm_slaves(3).SData(9),
		     spm_ports_s_3_SData_8_Q  => n_spm_slaves(3).SData(8),
		     spm_ports_s_3_SData_7_Q  => n_spm_slaves(3).SData(7),
		     spm_ports_s_3_SData_6_Q  => n_spm_slaves(3).SData(6),
		     spm_ports_s_3_SData_5_Q  => n_spm_slaves(3).SData(5),
		     spm_ports_s_3_SData_4_Q  => n_spm_slaves(3).SData(4),
		     spm_ports_s_3_SData_3_Q  => n_spm_slaves(3).SData(3),
		     spm_ports_s_3_SData_2_Q  => n_spm_slaves(3).SData(2),
		     spm_ports_s_3_SData_1_Q  => n_spm_slaves(3).SData(1),
		     spm_ports_s_3_SData_0_Q  => n_spm_slaves(3).SData(0),
		     ocp_io_ms_2_MAddr_31_Q   => p_masters(2).MAddr(31),
		     ocp_io_ms_2_MAddr_30_Q   => p_masters(2).MAddr(30),
		     ocp_io_ms_2_MAddr_29_Q   => p_masters(2).MAddr(29),
		     ocp_io_ms_2_MAddr_28_Q   => p_masters(2).MAddr(28),
		     ocp_io_ms_2_MAddr_27_Q   => p_masters(2).MAddr(27),
		     ocp_io_ms_2_MAddr_26_Q   => p_masters(2).MAddr(26),
		     ocp_io_ms_2_MAddr_25_Q   => p_masters(2).MAddr(25),
		     ocp_io_ms_2_MAddr_24_Q   => p_masters(2).MAddr(24),
		     ocp_io_ms_2_MAddr_23_Q   => p_masters(2).MAddr(23),
		     ocp_io_ms_2_MAddr_22_Q   => p_masters(2).MAddr(22),
		     ocp_io_ms_2_MAddr_21_Q   => p_masters(2).MAddr(21),
		     ocp_io_ms_2_MAddr_20_Q   => p_masters(2).MAddr(20),
		     ocp_io_ms_2_MAddr_19_Q   => p_masters(2).MAddr(19),
		     ocp_io_ms_2_MAddr_18_Q   => p_masters(2).MAddr(18),
		     ocp_io_ms_2_MAddr_17_Q   => p_masters(2).MAddr(17),
		     ocp_io_ms_2_MAddr_16_Q   => p_masters(2).MAddr(16),
		     ocp_io_ms_2_MAddr_15_Q   => p_masters(2).MAddr(15),
		     ocp_io_ms_2_MAddr_14_Q   => p_masters(2).MAddr(14),
		     ocp_io_ms_2_MAddr_13_Q   => p_masters(2).MAddr(13),
		     ocp_io_ms_2_MAddr_12_Q   => p_masters(2).MAddr(12),
		     ocp_io_ms_2_MAddr_11_Q   => p_masters(2).MAddr(11),
		     ocp_io_ms_2_MAddr_10_Q   => p_masters(2).MAddr(10),
		     ocp_io_ms_2_MAddr_9_Q    => p_masters(2).MAddr(9),
		     ocp_io_ms_2_MAddr_8_Q    => p_masters(2).MAddr(8),
		     ocp_io_ms_2_MAddr_7_Q    => p_masters(2).MAddr(7),
		     ocp_io_ms_2_MAddr_6_Q    => p_masters(2).MAddr(6),
		     ocp_io_ms_2_MAddr_5_Q    => p_masters(2).MAddr(5),
		     ocp_io_ms_2_MAddr_4_Q    => p_masters(2).MAddr(4),
		     ocp_io_ms_2_MAddr_3_Q    => p_masters(2).MAddr(3),
		     ocp_io_ms_2_MAddr_2_Q    => p_masters(2).MAddr(2),
		     ocp_io_ms_2_MAddr_1_Q    => p_masters(2).MAddr(1),
		     ocp_io_ms_2_MAddr_0_Q    => p_masters(2).MAddr(0),
		     ocp_io_ms_3_MCmd_2_Q     => p_masters(3).MCmd(2),
		     ocp_io_ms_3_MCmd_1_Q     => p_masters(3).MCmd(1),
		     ocp_io_ms_3_MCmd_0_Q     => p_masters(3).MCmd(0),
		     ocp_io_ms_1_MData_31_Q   => p_masters(1).MData(31),
		     ocp_io_ms_1_MData_30_Q   => p_masters(1).MData(30),
		     ocp_io_ms_1_MData_29_Q   => p_masters(1).MData(29),
		     ocp_io_ms_1_MData_28_Q   => p_masters(1).MData(28),
		     ocp_io_ms_1_MData_27_Q   => p_masters(1).MData(27),
		     ocp_io_ms_1_MData_26_Q   => p_masters(1).MData(26),
		     ocp_io_ms_1_MData_25_Q   => p_masters(1).MData(25),
		     ocp_io_ms_1_MData_24_Q   => p_masters(1).MData(24),
		     ocp_io_ms_1_MData_23_Q   => p_masters(1).MData(23),
		     ocp_io_ms_1_MData_22_Q   => p_masters(1).MData(22),
		     ocp_io_ms_1_MData_21_Q   => p_masters(1).MData(21),
		     ocp_io_ms_1_MData_20_Q   => p_masters(1).MData(20),
		     ocp_io_ms_1_MData_19_Q   => p_masters(1).MData(19),
		     ocp_io_ms_1_MData_18_Q   => p_masters(1).MData(18),
		     ocp_io_ms_1_MData_17_Q   => p_masters(1).MData(17),
		     ocp_io_ms_1_MData_16_Q   => p_masters(1).MData(16),
		     ocp_io_ms_1_MData_15_Q   => p_masters(1).MData(15),
		     ocp_io_ms_1_MData_14_Q   => p_masters(1).MData(14),
		     ocp_io_ms_1_MData_13_Q   => p_masters(1).MData(13),
		     ocp_io_ms_1_MData_12_Q   => p_masters(1).MData(12),
		     ocp_io_ms_1_MData_11_Q   => p_masters(1).MData(11),
		     ocp_io_ms_1_MData_10_Q   => p_masters(1).MData(10),
		     ocp_io_ms_1_MData_9_Q    => p_masters(1).MData(9),
		     ocp_io_ms_1_MData_8_Q    => p_masters(1).MData(8),
		     ocp_io_ms_1_MData_7_Q    => p_masters(1).MData(7),
		     ocp_io_ms_1_MData_6_Q    => p_masters(1).MData(6),
		     ocp_io_ms_1_MData_5_Q    => p_masters(1).MData(5),
		     ocp_io_ms_1_MData_4_Q    => p_masters(1).MData(4),
		     ocp_io_ms_1_MData_3_Q    => p_masters(1).MData(3),
		     ocp_io_ms_1_MData_2_Q    => p_masters(1).MData(2),
		     ocp_io_ms_1_MData_1_Q    => p_masters(1).MData(1),
		     ocp_io_ms_1_MData_0_Q    => p_masters(1).MData(0),
		     ocp_io_ms_0_MByteEn_3_Q  => p_masters(0).MByteEn(3),
		     ocp_io_ms_0_MByteEn_2_Q  => p_masters(0).MByteEn(2),
		     ocp_io_ms_0_MByteEn_1_Q  => p_masters(0).MByteEn(1),
		     ocp_io_ms_0_MByteEn_0_Q  => p_masters(0).MByteEn(0),
		     ocp_io_ms_2_MCmd_2_Q     => p_masters(2).MCmd(2),
		     ocp_io_ms_2_MCmd_1_Q     => p_masters(2).MCmd(1),
		     ocp_io_ms_2_MCmd_0_Q     => p_masters(2).MCmd(0),
		     spm_ports_s_2_SData_63_Q => n_spm_slaves(2).SData(63),
		     spm_ports_s_2_SData_62_Q => n_spm_slaves(2).SData(62),
		     spm_ports_s_2_SData_61_Q => n_spm_slaves(2).SData(61),
		     spm_ports_s_2_SData_60_Q => n_spm_slaves(2).SData(60),
		     spm_ports_s_2_SData_59_Q => n_spm_slaves(2).SData(59),
		     spm_ports_s_2_SData_58_Q => n_spm_slaves(2).SData(58),
		     spm_ports_s_2_SData_57_Q => n_spm_slaves(2).SData(57),
		     spm_ports_s_2_SData_56_Q => n_spm_slaves(2).SData(56),
		     spm_ports_s_2_SData_55_Q => n_spm_slaves(2).SData(55),
		     spm_ports_s_2_SData_54_Q => n_spm_slaves(2).SData(54),
		     spm_ports_s_2_SData_53_Q => n_spm_slaves(2).SData(53),
		     spm_ports_s_2_SData_52_Q => n_spm_slaves(2).SData(52),
		     spm_ports_s_2_SData_51_Q => n_spm_slaves(2).SData(51),
		     spm_ports_s_2_SData_50_Q => n_spm_slaves(2).SData(50),
		     spm_ports_s_2_SData_49_Q => n_spm_slaves(2).SData(49),
		     spm_ports_s_2_SData_48_Q => n_spm_slaves(2).SData(48),
		     spm_ports_s_2_SData_47_Q => n_spm_slaves(2).SData(47),
		     spm_ports_s_2_SData_46_Q => n_spm_slaves(2).SData(46),
		     spm_ports_s_2_SData_45_Q => n_spm_slaves(2).SData(45),
		     spm_ports_s_2_SData_44_Q => n_spm_slaves(2).SData(44),
		     spm_ports_s_2_SData_43_Q => n_spm_slaves(2).SData(43),
		     spm_ports_s_2_SData_42_Q => n_spm_slaves(2).SData(42),
		     spm_ports_s_2_SData_41_Q => n_spm_slaves(2).SData(41),
		     spm_ports_s_2_SData_40_Q => n_spm_slaves(2).SData(40),
		     spm_ports_s_2_SData_39_Q => n_spm_slaves(2).SData(39),
		     spm_ports_s_2_SData_38_Q => n_spm_slaves(2).SData(38),
		     spm_ports_s_2_SData_37_Q => n_spm_slaves(2).SData(37),
		     spm_ports_s_2_SData_36_Q => n_spm_slaves(2).SData(36),
		     spm_ports_s_2_SData_35_Q => n_spm_slaves(2).SData(35),
		     spm_ports_s_2_SData_34_Q => n_spm_slaves(2).SData(34),
		     spm_ports_s_2_SData_33_Q => n_spm_slaves(2).SData(33),
		     spm_ports_s_2_SData_32_Q => n_spm_slaves(2).SData(32),
		     spm_ports_s_2_SData_31_Q => n_spm_slaves(2).SData(31),
		     spm_ports_s_2_SData_30_Q => n_spm_slaves(2).SData(30),
		     spm_ports_s_2_SData_29_Q => n_spm_slaves(2).SData(29),
		     spm_ports_s_2_SData_28_Q => n_spm_slaves(2).SData(28),
		     spm_ports_s_2_SData_27_Q => n_spm_slaves(2).SData(27),
		     spm_ports_s_2_SData_26_Q => n_spm_slaves(2).SData(26),
		     spm_ports_s_2_SData_25_Q => n_spm_slaves(2).SData(25),
		     spm_ports_s_2_SData_24_Q => n_spm_slaves(2).SData(24),
		     spm_ports_s_2_SData_23_Q => n_spm_slaves(2).SData(23),
		     spm_ports_s_2_SData_22_Q => n_spm_slaves(2).SData(22),
		     spm_ports_s_2_SData_21_Q => n_spm_slaves(2).SData(21),
		     spm_ports_s_2_SData_20_Q => n_spm_slaves(2).SData(20),
		     spm_ports_s_2_SData_19_Q => n_spm_slaves(2).SData(19),
		     spm_ports_s_2_SData_18_Q => n_spm_slaves(2).SData(18),
		     spm_ports_s_2_SData_17_Q => n_spm_slaves(2).SData(17),
		     spm_ports_s_2_SData_16_Q => n_spm_slaves(2).SData(16),
		     spm_ports_s_2_SData_15_Q => n_spm_slaves(2).SData(15),
		     spm_ports_s_2_SData_14_Q => n_spm_slaves(2).SData(14),
		     spm_ports_s_2_SData_13_Q => n_spm_slaves(2).SData(13),
		     spm_ports_s_2_SData_12_Q => n_spm_slaves(2).SData(12),
		     spm_ports_s_2_SData_11_Q => n_spm_slaves(2).SData(11),
		     spm_ports_s_2_SData_10_Q => n_spm_slaves(2).SData(10),
		     spm_ports_s_2_SData_9_Q  => n_spm_slaves(2).SData(9),
		     spm_ports_s_2_SData_8_Q  => n_spm_slaves(2).SData(8),
		     spm_ports_s_2_SData_7_Q  => n_spm_slaves(2).SData(7),
		     spm_ports_s_2_SData_6_Q  => n_spm_slaves(2).SData(6),
		     spm_ports_s_2_SData_5_Q  => n_spm_slaves(2).SData(5),
		     spm_ports_s_2_SData_4_Q  => n_spm_slaves(2).SData(4),
		     spm_ports_s_2_SData_3_Q  => n_spm_slaves(2).SData(3),
		     spm_ports_s_2_SData_2_Q  => n_spm_slaves(2).SData(2),
		     spm_ports_s_2_SData_1_Q  => n_spm_slaves(2).SData(1),
		     spm_ports_s_2_SData_0_Q  => n_spm_slaves(2).SData(0),
		     ocp_io_ms_1_MCmd_2_Q     => p_masters(1).MCmd(2),
		     ocp_io_ms_1_MCmd_1_Q     => p_masters(1).MCmd(1),
		     ocp_io_ms_1_MCmd_0_Q     => p_masters(1).MCmd(0),
		     ocp_io_ms_1_MAddr_31_Q   => p_masters(1).MAddr(31),
		     ocp_io_ms_1_MAddr_30_Q   => p_masters(1).MAddr(30),
		     ocp_io_ms_1_MAddr_29_Q   => p_masters(1).MAddr(29),
		     ocp_io_ms_1_MAddr_28_Q   => p_masters(1).MAddr(28),
		     ocp_io_ms_1_MAddr_27_Q   => p_masters(1).MAddr(27),
		     ocp_io_ms_1_MAddr_26_Q   => p_masters(1).MAddr(26),
		     ocp_io_ms_1_MAddr_25_Q   => p_masters(1).MAddr(25),
		     ocp_io_ms_1_MAddr_24_Q   => p_masters(1).MAddr(24),
		     ocp_io_ms_1_MAddr_23_Q   => p_masters(1).MAddr(23),
		     ocp_io_ms_1_MAddr_22_Q   => p_masters(1).MAddr(22),
		     ocp_io_ms_1_MAddr_21_Q   => p_masters(1).MAddr(21),
		     ocp_io_ms_1_MAddr_20_Q   => p_masters(1).MAddr(20),
		     ocp_io_ms_1_MAddr_19_Q   => p_masters(1).MAddr(19),
		     ocp_io_ms_1_MAddr_18_Q   => p_masters(1).MAddr(18),
		     ocp_io_ms_1_MAddr_17_Q   => p_masters(1).MAddr(17),
		     ocp_io_ms_1_MAddr_16_Q   => p_masters(1).MAddr(16),
		     ocp_io_ms_1_MAddr_15_Q   => p_masters(1).MAddr(15),
		     ocp_io_ms_1_MAddr_14_Q   => p_masters(1).MAddr(14),
		     ocp_io_ms_1_MAddr_13_Q   => p_masters(1).MAddr(13),
		     ocp_io_ms_1_MAddr_12_Q   => p_masters(1).MAddr(12),
		     ocp_io_ms_1_MAddr_11_Q   => p_masters(1).MAddr(11),
		     ocp_io_ms_1_MAddr_10_Q   => p_masters(1).MAddr(10),
		     ocp_io_ms_1_MAddr_9_Q    => p_masters(1).MAddr(9),
		     ocp_io_ms_1_MAddr_8_Q    => p_masters(1).MAddr(8),
		     ocp_io_ms_1_MAddr_7_Q    => p_masters(1).MAddr(7),
		     ocp_io_ms_1_MAddr_6_Q    => p_masters(1).MAddr(6),
		     ocp_io_ms_1_MAddr_5_Q    => p_masters(1).MAddr(5),
		     ocp_io_ms_1_MAddr_4_Q    => p_masters(1).MAddr(4),
		     ocp_io_ms_1_MAddr_3_Q    => p_masters(1).MAddr(3),
		     ocp_io_ms_1_MAddr_2_Q    => p_masters(1).MAddr(2),
		     ocp_io_ms_1_MAddr_1_Q    => p_masters(1).MAddr(1),
		     ocp_io_ms_1_MAddr_0_Q    => p_masters(1).MAddr(0),
		     ocp_io_ms_0_MCmd_2_Q     => p_masters(0).MCmd(2),
		     ocp_io_ms_0_MCmd_1_Q     => p_masters(0).MCmd(1),
		     ocp_io_ms_0_MCmd_0_Q     => p_masters(0).MCmd(0));  

--na clock 
na_clk_generate: process
begin
	wait for NA_HPERIOD;
	n_clk <= not n_clk;
        wait for SKEW;
        n_clk_sk <= n_clk;
end process;

--proc clock 
proc_clk_generate: process
begin
	wait for P_HPERIOD;
	p_clk <= not p_clk;
        wait for SKEW;
        p_clk_sk <= p_clk;
end process;

--reset
rst_generate: process
begin
	wait for 4*NA_HPERIOD;
        wait for delay;
	reset <= '0';
	wait;
end process;



spm_initilize: process

  variable count : natural := 0;

begin

   	for i in 0 to N-1 loop
		for j in 0 to N-1 loop
                  p_spm_masters((i*N)+j).MCmd  <= (others=>'0');
                  p_spm_masters((i*N)+j).MAddr <= (others=>'0');
                  p_spm_masters((i*N)+j).MData <= (others=>'0');
		end loop;
	end loop;                  

                        
        wait until falling_edge(reset);

        while(count < SPM_INIT_SIZE) loop

                wait until rising_edge(n_clk);
                wait for delay;

                p_spm_masters(0).MCmd <="1";
                p_spm_masters(0).MAddr <= std_logic_vector(to_unsigned(count,16));--x"00000000";
                p_spm_masters(0).MData <= x"0000000011111111";
                p_spm_masters(1).MCmd <="1";
                p_spm_masters(1).MAddr <= std_logic_vector(to_unsigned(count+SPM_INIT_SIZE,16));--x"00000002";
                p_spm_masters(1).MData <= x"2222222233333333";
                p_spm_masters(2).MCmd <="1";
                p_spm_masters(2).MAddr <= std_logic_vector(to_unsigned(count+2*SPM_INIT_SIZE,16));--x"00000004";
                p_spm_masters(2).MData <= x"4444444455555555";
                p_spm_masters(3).MCmd <="1";
                p_spm_masters(3).MAddr <= std_logic_vector(to_unsigned(count+3*SPM_INIT_SIZE,16));--x"00000006";
                p_spm_masters(3).MData <= x"6666666677777777";

                count := count + 1;

        end loop;

        wait until rising_edge(n_clk);
        --wait until rising_edge(n_clk);
        wait for delay;
       
        p_spm_masters(0).MCmd <="0";
        p_spm_masters(0).MAddr <= (others=>'0');
        p_spm_masters(0).MData <= (others=>'0');
        p_spm_masters(1).MCmd <="0";
        p_spm_masters(1).MAddr <= (others=>'0');
        p_spm_masters(1).MData <= (others=>'0');
        p_spm_masters(2).MCmd <="0";
        p_spm_masters(2).MAddr <= (others=>'0');
        p_spm_masters(2).MData <= (others=>'0');
        p_spm_masters(3).MCmd <="0";
        p_spm_masters(3).MAddr <= (others=>'0');
        p_spm_masters(3).MData <= (others=>'0');


        wait for 1900 ns ;

        wait until rising_edge(n_clk);

        count := 0;
        while(count < 4*SPM_INIT_SIZE) loop

                wait until rising_edge(n_clk);
                wait for delay;

                p_spm_masters(0).MCmd <="0";
                p_spm_masters(0).MAddr <= std_logic_vector(to_unsigned(count,16));--x"00000000";
                p_spm_masters(1).MCmd <="0";
                p_spm_masters(1).MAddr <= std_logic_vector(to_unsigned(count,16));--x"00000002";
                p_spm_masters(2).MCmd <="0";
                p_spm_masters(2).MAddr <= std_logic_vector(to_unsigned(count,16));--x"00000004";
                p_spm_masters(3).MCmd <="0";
                p_spm_masters(3).MAddr <= std_logic_vector(to_unsigned(count,16));--x"00000006";

                count := count + 1;

        end loop;

        wait;


end process;


init_ni0: process

variable word   : string (100 downto 1);--std_logic_vector(15 downto 0) := (others => '0');
variable cnt    : integer :=0;
variable slt_num : integer;
variable l      : line;
variable slt    : std_logic_vector(4 downto 0);
variable route  : std_logic_vector(15 downto 0);

begin

        p_masters(0).MCmd  <= (others=>'0');
        p_masters(0).MAddr <= (others=>'0');
        p_masters(0).MData <= (others=>'0');
        p_masters(0).MByteEn <= (others=>'0');
        p_masters(0).MRespAccept <= '0';

                    
        wait until falling_edge(reset);
      	wait for 6*NA_HPERIOD;

        if not endfile(schedule0) then

                loop 
                        str_read(schedule0, word);
                        exit when word(100 downto 96)="# NI0" or endfile(schedule0);
                end loop;

                report "NI==========>" & word(100 downto 96) severity note;

                loop
                        str_read(schedule0, word);
                        exit when word(100 downto 89)="# SLOT_TABLE" or endfile(schedule0);
                end loop;

                report "ST==========>" & word(100 downto 89) severity note;
                
                readline(schedule0, l);
		read(l, slt_num);
                cnt := 0;
                loop
                        readline(schedule0, l);
			read(l, slt);
                        --st_write
                        --print str(slt);
                        st_write(p_masters(0),
                                 p_slaves(0),
                                 std_logic_vector(to_unsigned(cnt*4, OCP_ADDR_WIDTH-ADDR_MASK_W)),
                                 slt, p_clk);
                        cnt := cnt + 1;
                        exit when cnt = slt_num or endfile(schedule0);
                end loop;

                loop 
                        str_read(schedule0, word);
                        exit when word(100 downto 88)="# ROUTE_TABLE" or endfile(schedule0);
                end loop; 
                report "RT==========>" & word(100 downto 88) severity note;

                cnt := 0;
                loop
                        readline(schedule0, l);
			read(l, route);
                        --rt_write
                        --report str(route);
                        route_write (p_masters(0),
                                     p_slaves(0),
                                     std_logic_vector(to_unsigned(cnt*4, OCP_ADDR_WIDTH-ADDR_MASK_W)),
                                     route, p_clk);
                        cnt := cnt + 1;
                        exit when cnt = N*N or endfile(schedule0);
                end loop;

                --DMA 1
                dma_write (p_masters(0), p_slaves(0),
                           x"00000c", x"00000000", p_clk);
                --DMA 2
                dma_write (p_masters(0), p_slaves(0),
                           x"000014", x"00000000", p_clk);
                --DMA 3
                dma_write (p_masters(0), p_slaves(0),
                           x"00001c", x"00000000", p_clk);

                --enable and start
                --DMA 1
                dma_write (p_masters(0), p_slaves(0),
                           x"000008", x"00008004", p_clk);
                --DMA 2
                dma_write (p_masters(0), p_slaves(0),
                           x"000010", x"00008004", p_clk);
                --DMA 3
                dma_write (p_masters(0), p_slaves(0),
                           x"000018", x"00008004", p_clk);

                -- DMA 1 read for testing
                dma_read (p_masters(0), p_slaves(0),
                           x"000008", p_clk);
        end if;
          
end process;


init_ni1: process

variable word   : string (100 downto 1);--std_logic_vector(15 downto 0) := (others => '0');
variable cnt    : integer :=0;
variable slt_num : integer;
variable l      : line;
variable slt    : std_logic_vector(4 downto 0);
variable route  : std_logic_vector(15 downto 0);

begin

        p_masters(1).MCmd  <= (others=>'0');
        p_masters(1).MAddr <= (others=>'0');
        p_masters(1).MData <= (others=>'0');
        p_masters(1).MByteEn <= (others=>'0');
        p_masters(1).MRespAccept <= '0';
        
        wait until falling_edge(reset);
      	wait for 6*NA_HPERIOD;

        if not endfile(schedule1) then

                loop 
                        str_read(schedule1, word);
                        exit when word(100 downto 96)="# NI1" or endfile(schedule1);
                end loop;

                report "NI==========>" & word(100 downto 96) severity note;

                loop
                        str_read(schedule1, word);
                        exit when word(100 downto 89)="# SLOT_TABLE" or endfile(schedule1);
                end loop;
                

                report "ST==========>" & word(100 downto 89) severity note;

                readline(schedule1, l);
		read(l, slt_num);
                cnt := 0;
                loop
                        readline(schedule1, l);
			read(l, slt);
                        --st_write
                        --print str(slt);
                        st_write(p_masters(1),
                                 p_slaves(1),
                                 std_logic_vector(to_unsigned(cnt*4, OCP_ADDR_WIDTH-ADDR_MASK_W)),
                                 slt, p_clk);
                        cnt := cnt + 1;
                        exit when cnt = slt_num or endfile(schedule1);
                end loop;

                loop 
                        str_read(schedule1, word);
                        exit when word(100 downto 88)="# ROUTE_TABLE" or endfile(schedule0);
                end loop; 
                report "RT==========>" & word(100 downto 88) severity note;

                cnt := 0;
                loop
                        readline(schedule1, l);
			read(l, route);
                        --rt_write
                        --print str(route);
                        route_write (p_masters(1),
                                     p_slaves(1),
                                     std_logic_vector(to_unsigned(cnt*4, OCP_ADDR_WIDTH-ADDR_MASK_W)),
                                     route, p_clk);
                        cnt := cnt + 1;
                        exit when cnt = N*N or endfile(schedule1);
                end loop;

                --DMA 0
                dma_write (p_masters(1), p_slaves(1),
                           x"000004", x"00040004", p_clk);
                --DMA 2
                dma_write (p_masters(1), p_slaves(1),
                           x"000014", x"00040004", p_clk);
                --DMA 3
                dma_write (p_masters(1), p_slaves(1),
                           x"00001c", x"00040004", p_clk);

                --enable and start
                --DMA 0
                dma_write (p_masters(1), p_slaves(1),
                           x"000000", x"00008004", p_clk);
                --DMA 2
                dma_write (p_masters(1), p_slaves(1),
                           x"000010", x"00008004", p_clk);
                --DMA 3
                dma_write (p_masters(1), p_slaves(1),
                           x"000018", x"00008004", p_clk);                
        end if;
          
end process;




init_ni2: process

variable word   : string (100 downto 1);--std_logic_vector(15 downto 0) := (others => '0');
variable cnt    : integer :=0;
variable slt_num : integer;
variable l      : line;
variable slt    : std_logic_vector(4 downto 0);
variable route  : std_logic_vector(15 downto 0);

begin

        p_masters(2).MCmd  <= (others=>'0');
        p_masters(2).MAddr <= (others=>'0');
        p_masters(2).MData <= (others=>'0');
        p_masters(2).MByteEn <= (others=>'0');
        p_masters(2).MRespAccept <= '0';
        
        wait until falling_edge(reset);
      	wait for 6*NA_HPERIOD;

        if not endfile(schedule2) then

                loop 
                        str_read(schedule2, word);
                        exit when word(100 downto 96)="# NI2" or endfile(schedule2);
                end loop;

                report "NI==========>" & word(100 downto 96) severity note;

                loop
                        str_read(schedule2, word);
                        exit when word(100 downto 89)="# SLOT_TABLE" or endfile(schedule2);
                end loop;
                

                report "ST==========>" & word(100 downto 89) severity note;

                readline(schedule2, l);
		read(l, slt_num);
                cnt := 0;
                loop
                        readline(schedule2, l);
			read(l, slt);
                        --st_write
                        --print str(slt);
                        st_write(p_masters(2),
                                 p_slaves(2),
                                 std_logic_vector(to_unsigned(cnt*4, OCP_ADDR_WIDTH-ADDR_MASK_W)),
                                 slt, p_clk);
                        cnt := cnt + 1;
                        exit when cnt = slt_num or endfile(schedule2);
                end loop;

                loop 
                        str_read(schedule2, word);
                        exit when word(100 downto 88)="# ROUTE_TABLE" or endfile(schedule0);
                end loop; 
                report "RT==========>" & word(100 downto 88) severity note;

                cnt := 0;
                loop
                        readline(schedule2, l);
			read(l, route);
                        --rt_write
                        --print str(route);
                        route_write (p_masters(2),
                                     p_slaves(2),
                                     std_logic_vector(to_unsigned(cnt*4, OCP_ADDR_WIDTH-ADDR_MASK_W)),
                                     route, p_clk);
                        cnt := cnt + 1;
                        exit when cnt = N*N or endfile(schedule2);
                end loop;

                --DMA 0
                dma_write (p_masters(2), p_slaves(2),
                           x"000004", x"00080008", p_clk);
                --DMA 1
                dma_write (p_masters(2), p_slaves(2),
                           x"00000c", x"00080008", p_clk);
                --DMA 3
                dma_write (p_masters(2), p_slaves(2),
                           x"00001c", x"00080008", p_clk);

                --enable and start
                --DMA 0
                dma_write (p_masters(2), p_slaves(2),
                           x"000000", x"00008004", p_clk);
                --DMA 1
                dma_write (p_masters(2), p_slaves(2),
                           x"000008", x"00008004", p_clk);
                --DMA 3
                dma_write (p_masters(2), p_slaves(2),
                           x"000018", x"00008004", p_clk);
                
        end if;
          
end process;




init_ni3: process

variable word   : string (100 downto 1);--std_logic_vector(15 downto 0) := (others => '0');
variable cnt    : integer :=0;
variable l      : line;
variable slt_num : integer;
variable slt    : std_logic_vector(4 downto 0);
variable route  : std_logic_vector(15 downto 0);

begin
        p_masters(3).MCmd  <= (others=>'0');
        p_masters(3).MAddr <= (others=>'0');
        p_masters(3).MData <= (others=>'0');
        p_masters(3).MByteEn <= (others=>'0');
        p_masters(3).MRespAccept <= '0';
        
        wait until falling_edge(reset);
      	wait for 6*NA_HPERIOD;

        if not endfile(schedule3) then

                loop 
                        str_read(schedule3, word);
                        exit when word(100 downto 96)="# NI3" or endfile(schedule3);
                end loop;

                report "NI==========>" & word(100 downto 96) severity note;

                loop
                        str_read(schedule3, word);
                        exit when word(100 downto 89)="# SLOT_TABLE" or endfile(schedule3);
                end loop;
                

                report "ST==========>" & word(100 downto 89) severity note;

                readline(schedule3, l);
		read(l, slt_num);
                cnt := 0;
                loop
                        readline(schedule3, l);
			read(l, slt);
                        --st_write
                        --print str(slt);
                        st_write(p_masters(3),
                                  p_slaves(3),
                                std_logic_vector(to_unsigned(cnt*4, OCP_ADDR_WIDTH-ADDR_MASK_W)),
                                 slt, p_clk);
                        cnt := cnt + 1;
                        exit when cnt = slt_num or endfile(schedule3);
                end loop;

                loop 
                        str_read(schedule3, word);
                        exit when word(100 downto 88)="# ROUTE_TABLE" or endfile(schedule0);
                end loop; 
                report "RT==========>" & word(100 downto 88) severity note;

                cnt := 0;
                loop
                        readline(schedule3, l);
			read(l, route);
                        --rt_write
                        --print str(route);
                        route_write (p_masters(3),
                                     p_slaves(3),
                                     std_logic_vector(to_unsigned(cnt*4, OCP_ADDR_WIDTH-ADDR_MASK_W)),
                                     route, p_clk);
                        cnt := cnt + 1;
                        exit when cnt = N*N or endfile(schedule3);
                end loop;

                --DMA 0
                dma_write (p_masters(3), p_slaves(3),
                           x"000004", x"000c000c", p_clk);
                --DMA 1
                dma_write (p_masters(3), p_slaves(3),
                           x"00000c", x"000c000c", p_clk);
                --DMA 2
                dma_write (p_masters(3), p_slaves(3),
                           x"000014", x"000c000c", p_clk);

                --enable and start
                --DMA 0
                dma_write (p_masters(3), p_slaves(3),
                           x"000000", x"00008004", p_clk);
                --DMA 1
                dma_write (p_masters(3), p_slaves(3),
                           x"000008", x"00008004", p_clk);
                --DMA 2
                dma_write (p_masters(3), p_slaves(3),
                           x"000010", x"00008004", p_clk);
                                
        end if;          
end process;



end behav;
