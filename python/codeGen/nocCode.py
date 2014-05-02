#
# Copyright Technical University of Denmark. All rights reserved.
# This file is part of the T-CREST project.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN
# NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of the copyright holder.
#
###############################################################################
# Authors:
#    Rasmus Bo Soerensen (rasmus@rbscloud.dk)
#
###############################################################################

def writeConfig(f,N,M,NODES):

    f.write('''\
library ieee;
use ieee.std_logic_1164.all;
use work.config_types.all;

package config is

    constant N : integer := '''+N+''';
    constant M : integer := '''+M+''';
    constant NODES : integer := '''+str(NODES)+''';
    constant PRD_LENGTH : integer := '''+str(NODES*2)+''';

    constant PDELAY	: time := 500 ps;
    constant NA_HPERIOD	: time := 5 ns;
    constant P_HPERIOD	: time := 5 ns;
    constant SKEW       : time := 0 ns;
    constant delay      : time := 0.3 ns;

end package ; -- aegean_def

''')

def writeNodeInst(f,instancename,k,i,j):
    pass

def writeEast(noc,i1,i2,j1,j2):
    noc.arch.addToBody('''
    east_in_f('''+i2+''')('''+j2+''') <= west_out_f('''+i1+''')('''+j1+''');
    west_out_b('''+i1+''')('''+j1+''') <= east_in_b('''+i2+''')('''+j2+''');
''')

def writeWest(noc,i1,i2,j1,j2):
    noc.arch.addToBody('''
    west_in_f('''+i2+''')('''+j2+''') <= east_out_f('''+i1+''')('''+j1+''');
    east_out_b('''+i1+''')('''+j1+''') <= west_in_b('''+i2+''')('''+j2+''');
''')

def writeSouth(noc,i1,i2,j1,j2):
    noc.arch.addToBody('''
    south_in_f('''+i2+''')('''+j2+''') <= north_out_f('''+i1+''')('''+j1+''');
    north_out_b('''+i1+''')('''+j1+''') <= south_in_b('''+i2+''')('''+j2+''');
''')

def writeNorth(noc,i1,i2,j1,j2):
    noc.arch.addToBody('''
    north_in_f('''+i2+''')('''+j2+''') <= south_out_f('''+i1+''')('''+j1+''');
    south_out_b('''+i1+''')('''+j1+''') <= north_in_b('''+i2+''')('''+j2+''');
''')

def writeBitorus(noc):
    noc.arch.addToBody('''
    links_m : for i in 0 to M-1 generate
        links_n : for j in 0 to N-1 generate
            wrap_ns : if i = 0 generate
                south_in_f(0)(j) <= north_out_f(M-1)(j);
                north_out_b(M-1)(j) <= south_in_b(0)(j);
                north_in_f(M-1)(j) <= south_out_f(0)(j);
                south_out_b(0)(j) <= north_in_b(M-1)(j);
            end generate wrap_ns;
            wrap_ew : if j = 0 generate
                east_in_f(i)(0) <= west_out_f(i)(N-1);
                west_out_b(i)(N-1) <= east_in_b(i)(0);
                west_in_f(i)(N-1) <= east_out_f(i)(0);
                east_out_b(i)(0) <= west_in_b(i)(N-1);
            end generate wrap_ew;
            ns : if i > 0 generate
                south_in_f(i)(j) <= north_out_f(i-1)(j);
                north_out_b(i-1)(j) <= south_in_b(i)(j);
                north_in_f(i-1)(j) <= south_out_f(i)(j);
                south_out_b(i)(j) <= north_in_b(i-1)(j);
            end generate ns;
            ew : if j > 0 generate
                east_in_f(i)(j) <= west_out_f(i)(j-1);
                west_out_b(i)(j-1) <= east_in_b(i)(j);
                west_in_f(i)(j-1) <= east_out_f(i)(j);
                east_out_b(i)(j) <= west_in_b(i)(j-1);
            end generate ew;
        end generate links_n;
    end generate links_m;

''')

def writeMesh(noc):
    noc.arch.addToBody('''
    links_m : for i in 0 to M-1 generate
        links_n : for j in 0 to N-1 generate
            bottom : if (i = (M-1) and j < (N-1)) generate
                east_in_f(i)(j) <= west_out_f(i)(j+1);
                west_out_b(i)(j+1) <= east_in_b(i)(j);
                west_in_f(i)(j+1) <= east_out_f(i)(j);
                east_out_b(i)(j) <= west_in_b(i)(j+1);
            end generate bottom;
            right : if (i < (M-1) and j = (N-1)) generate
                south_in_f(i)(j) <= north_out_f(i+1)(j);
                north_out_b(i+1)(j) <= south_in_b(i)(j);
                north_in_f(i+1)(j) <= south_out_f(i)(j);
                south_out_b(i)(j) <= north_in_b(i+1)(j);
            end generate right;
            center : if (i < (M-1) and j < (N-1)) generate
                north_in_f(i+1)(j) <= south_out_f(i)(j);
                south_out_b(i)(j) <= north_in_b(i+1)(j);
                south_in_f(i)(j) <= north_out_f(i+1)(j);
                north_out_b(i+1)(j) <= south_in_b(i)(j);
                west_in_f(i)(j+1) <= east_out_f(i)(j);
                east_out_b(i)(j) <= west_in_b(i)(j+1);
                east_in_f(i)(j) <= west_out_f(i)(j+1);
                west_out_b(i)(j+1) <= east_in_b(i)(j);
            end generate center;
        end generate links_n;
    end generate links_m;

''')


