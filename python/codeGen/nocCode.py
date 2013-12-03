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
    east_in('''+i2+''')('''+j2+''') <= west_out('''+i1+''')('''+j1+''');
''')

def writeWest(noc,i1,i2,j1,j2):
    noc.arch.addToBody('''
    west_in('''+i2+''')('''+j2+''') <= east_out('''+i1+''')('''+j1+''');
''')

def writeSouth(noc,i1,i2,j1,j2):
    noc.arch.addToBody('''
    south_in('''+i2+''')('''+j2+''') <= north_out('''+i1+''')('''+j1+''');
''')

def writeNorth(noc,i1,i2,j1,j2):
    noc.arch.addToBody('''
    north_in('''+i2+''')('''+j2+''') <= south_out('''+i1+''')('''+j1+''');
''')

def writeBitorus(noc):
    noc.arch.addToBody('''
    links_m : for i in 0 to M-1 generate
        links_n : for j in 0 to N-1 generate
            top : if (i = 0) generate
                north_in(i)(j) <= south_out(M-1)(j);
                south_in(M-1)(j) <= north_out(i)(j);
            end generate top;
            left : if (j = 0) generate
                west_in(i)(j) <= east_out(i)(N-1);
                east_in(i)(N-1) <= west_out(i)(j);
            end generate left;
            bottom : if (i = (M-1) and j < (N-1)) generate
                east_in(i)(j) <= west_out(i)(j+1);
                west_in(i)(j+1) <= east_out(i)(j);
            end generate bottom;
            right : if (i < (M-1) and j = (N-1)) generate
                south_in(i)(j) <= north_out(i+1)(j);
                north_in(i+1)(j) <= south_out(i)(j);
            end generate right;
            center : if (i < (M-1) and j < (N-1)) generate
                north_in(i+1)(j) <= south_out(i)(j);
                south_in(i)(j) <= north_out(i+1)(j);
                west_in(i)(j+1) <= east_out(i)(j);
                east_in(i)(j) <= west_out(i)(j+1);
            end generate center;
        end generate links_n;
    end generate links_m;

''')

def writeMesh(noc):
    noc.arch.addToBody('''
    links_m : for i in 0 to M-1 generate
        links_n : for j in 0 to N-1 generate
            bottom : if (i = (M-1) and j < (N-1)) generate
                east_in(i)(j) <= west_out(i)(j+1);
                west_in(i)(j+1) <= east_out(i)(j);
            end generate bottom;
            right : if (i < (M-1) and j = (N-1)) generate
                south_in(i)(j) <= north_out(i+1)(j);
                north_in(i+1)(j) <= south_out(i)(j);
            end generate right;
            center : if (i < (M-1) and j < (N-1)) generate
                north_in(i+1)(j) <= south_out(i)(j);
                south_in(i)(j) <= north_out(i+1)(j);
                west_in(i)(j+1) <= east_out(i)(j);
                east_in(i)(j) <= west_out(i)(j+1);
            end generate center;
        end generate links_n;
    end generate links_m;

''')


