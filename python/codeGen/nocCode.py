def writeConfig(f,N,M,NODES):

    f.write('''\
package config is

    constant N : integer := '''+N+''';
    constant M : integer := '''+M+''';
    constant NODES : integer := '''+str(NODES)+''';

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
            top : if (i = 0) generate
                north_in_f(i)(j) <= south_out_f(M-1)(j);
                south_out_b(M-1)(j) <= north_in_b(i)(j);
                south_in_f(M-1)(j) <= north_out_f(i)(j);
                north_out_b(i)(j) <= south_in_b(M-1)(j);
            end generate top;
            left : if (j = 0) generate
                west_in_f(i)(j) <= east_out_f(i)(N-1);
                east_out_b(i)(N-1) <= west_in_b(i)(j);
                east_in_f(i)(N-1) <= west_out_f(i)(j);
                west_out_b(i)(j) <= east_in_b(i)(N-1);
            end generate left;
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


