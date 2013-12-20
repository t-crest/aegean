from codeGen.Component import Component
import math

def getAegean():
    aegean = Component('aegean')
    aegean.addPackage('ieee','std_logic_1164')
    aegean.addPackage('ieee','numeric_std')
    aegean.addPackage('work','config')
    aegean.addPackage('work','ocp')
    aegean.addPackage('work','noc_interface')

    aegean.entity.addPort('clk')
    aegean.entity.addPort('reset')

    aegean.entity.addPort('io_sramPins_ram_out_addr','out','std_logic_vector',19)
    aegean.entity.addPort('io_sramPins_ram_out_dout_ena','out','std_logic')
    aegean.entity.addPort('io_sramPins_ram_out_nadsc','out','std_logic')
    aegean.entity.addPort('io_sramPins_ram_out_noe','out','std_logic')
    aegean.entity.addPort('io_sramPins_ram_out_nbwe','out','std_logic')
    aegean.entity.addPort('io_sramPins_ram_out_nbw','out','std_logic_vector',4)
    aegean.entity.addPort('io_sramPins_ram_out_ngw','out','std_logic')
    aegean.entity.addPort('io_sramPins_ram_out_nce1','out','std_logic')
    aegean.entity.addPort('io_sramPins_ram_out_ce2','out','std_logic')
    aegean.entity.addPort('io_sramPins_ram_out_nce3','out','std_logic')
    aegean.entity.addPort('io_sramPins_ram_out_nadsp','out','std_logic')
    aegean.entity.addPort('io_sramPins_ram_out_nadv','out','std_logic')
    aegean.entity.addPort('io_sramPins_ram_out_dout','out','std_logic_vector',32)
    aegean.entity.addPort('io_sramPins_ram_in_din','in','std_logic_vector',32)

    return aegean

def getSram():
    sram = Component('SsramBurstRW')
    sram.entity.addPort('clk')
    sram.entity.addPort('reset')
    sram.entity.addPort('io_ocp_port_M_Cmd','in','std_logic_vector',3)
    sram.entity.addPort('io_ocp_port_M_Addr','in','std_logic_vector',21)
    sram.entity.addPort('io_ocp_port_M_Data','in','std_logic_vector',32)
    sram.entity.addPort('io_ocp_port_M_DataValid','in','std_logic')
    sram.entity.addPort('io_ocp_port_M_DataByteEn','in','std_logic_vector',4)
    sram.entity.addPort('io_ocp_port_S_Resp','out','std_logic_vector',2)
    sram.entity.addPort('io_ocp_port_S_Data','out','std_logic_vector',32)
    sram.entity.addPort('io_ocp_port_S_CmdAccept','out','std_logic')
    sram.entity.addPort('io_ocp_port_S_DataAccept','out','std_logic')
    sram.entity.addPort('io_ram_out_addr','out','std_logic_vector',19)
    sram.entity.addPort('io_ram_out_dout_ena','out','std_logic')
    sram.entity.addPort('io_ram_out_nadsc','out','std_logic')
    sram.entity.addPort('io_ram_out_noe','out','std_logic')
    sram.entity.addPort('io_ram_out_nbwe','out','std_logic')
    sram.entity.addPort('io_ram_out_nbw','out','std_logic_vector',4)
    sram.entity.addPort('io_ram_out_ngw','out','std_logic')
    sram.entity.addPort('io_ram_out_nce1','out','std_logic')
    sram.entity.addPort('io_ram_out_ce2','out','std_logic')
    sram.entity.addPort('io_ram_out_nce3','out','std_logic')
    sram.entity.addPort('io_ram_out_nadsp','out','std_logic')
    sram.entity.addPort('io_ram_out_nadv','out','std_logic')
    sram.entity.addPort('io_ram_out_dout','out','std_logic_vector',32)
    sram.entity.addPort('io_ram_in_din','in','std_logic_vector',32)
    return sram


def getArbiter(numPorts):
    arbiter = Component('Arbiter')
    arbiter.entity.addPort('clk')
    arbiter.entity.addPort('reset')
    arbiter.entity.addPort('io_slave_M_Cmd','out','std_logic_vector',3)
    arbiter.entity.addPort('io_slave_M_Addr','out','std_logic_vector',21)
    arbiter.entity.addPort('io_slave_M_Data','out','std_logic_vector',32)
    arbiter.entity.addPort('io_slave_M_DataValid','out','std_logic')
    arbiter.entity.addPort('io_slave_M_DataByteEn','out','std_logic_vector',4)
    arbiter.entity.addPort('io_slave_S_Resp','in','std_logic_vector',2)
    arbiter.entity.addPort('io_slave_S_Data','in','std_logic_vector',32)
    arbiter.entity.addPort('io_slave_S_CmdAccept','in','std_logic')
    arbiter.entity.addPort('io_slave_S_DataAccept','in','std_logic')
    for i in range(0,numPorts):
        arbiter.entity.addPort('io_master_'+str(i)+'_M_Cmd','in','std_logic_vector',3)
        arbiter.entity.addPort('io_master_'+str(i)+'_M_Addr','in','std_logic_vector',21)
        arbiter.entity.addPort('io_master_'+str(i)+'_M_Data','in','std_logic_vector',32)
        arbiter.entity.addPort('io_master_'+str(i)+'_M_DataValid','in','std_logic')
        arbiter.entity.addPort('io_master_'+str(i)+'_M_DataByteEn','in','std_logic_vector',4)
        arbiter.entity.addPort('io_master_'+str(i)+'_S_Resp','out','std_logic_vector',2)
        arbiter.entity.addPort('io_master_'+str(i)+'_S_Data','out','std_logic_vector',32)
        arbiter.entity.addPort('io_master_'+str(i)+'_S_CmdAccept','out','std_logic')
        arbiter.entity.addPort('io_master_'+str(i)+'_S_DataAccept','out','std_logic')
    return arbiter


def getPatmos(IPType,ledPort=None,uartPort=None):
    patmos = Component(IPType+'PatmosCore')
    patmos.entity.addPort('clk')
    patmos.entity.addPort('reset')

    patmos.entity.addPort('io_comConf_M_Cmd','out', 'std_logic_vector',3)
    patmos.entity.addPort('io_comConf_M_Addr','out', 'std_logic_vector',32)
    patmos.entity.addPort('io_comConf_M_Data','out', 'std_logic_vector',32)
    patmos.entity.addPort('io_comConf_M_ByteEn','out', 'std_logic_vector',4)
    patmos.entity.addPort('io_comConf_M_RespAccept','out', 'std_logic')
    patmos.entity.addPort('io_comConf_S_Resp','in', 'std_logic_vector',2)
    patmos.entity.addPort('io_comConf_S_Data','in', 'std_logic_vector',32)
    patmos.entity.addPort('io_comConf_S_CmdAccept','in', 'std_logic')
    patmos.entity.addPort('io_comSpm_M_Cmd','out', 'std_logic_vector',3)
    patmos.entity.addPort('io_comSpm_M_Addr','out', 'std_logic_vector',32)
    patmos.entity.addPort('io_comSpm_M_Data','out', 'std_logic_vector',32)
    patmos.entity.addPort('io_comSpm_M_ByteEn','out', 'std_logic_vector',4)
    patmos.entity.addPort('io_comSpm_S_Resp','in', 'std_logic_vector',2)
    patmos.entity.addPort('io_comSpm_S_Data','in', 'std_logic_vector',32)
    patmos.entity.addPort('io_cpuInfoPins_id','in', 'std_logic_vector',32)
    patmos.entity.addPort('io_memPort_M_Cmd','out', 'std_logic_vector',3)
    patmos.entity.addPort('io_memPort_M_Addr','out', 'std_logic_vector',21)
    patmos.entity.addPort('io_memPort_M_Data','out', 'std_logic_vector',32)
    patmos.entity.addPort('io_memPort_M_DataValid','out', 'std_logic')
    patmos.entity.addPort('io_memPort_M_DataByteEn','out', 'std_logic_vector',4)
    patmos.entity.addPort('io_memPort_S_Resp','in', 'std_logic_vector',2)
    patmos.entity.addPort('io_memPort_S_Data','in', 'std_logic_vector',32)
    patmos.entity.addPort('io_memPort_S_CmdAccept','in', 'std_logic')
    patmos.entity.addPort('io_memPort_S_DataAccept','in', 'std_logic')

    if ledPort is not None:
        patmos.entity.addPort('io_ledsPins_led','out','std_logic_vector',9)
    if uartPort is not None:
        patmos.entity.addPort('io_uartPins_tx','out','std_logic')
        patmos.entity.addPort('io_uartPins_rx','in','std_logic')

    return patmos


def declareSignals(aegean):
    aegean.arch.declSignal('ocp_io_ms','ocp_io_m_a')
    aegean.arch.declSignal('ocp_io_ss','ocp_io_s_a')
    aegean.arch.declSignal('ocp_core_ms','ocp_core_m_a')
    aegean.arch.declSignal('ocp_core_ss','ocp_core_s_a')
    aegean.arch.declSignal('ocp_burst_ms','ocp_burst_m_a')
    aegean.arch.declSignal('ocp_burst_ss','ocp_burst_s_a')
    aegean.arch.declSignal('ocp_burst_m_mem','ocp_burst_m')
    aegean.arch.declSignal('ocp_burst_s_mem','ocp_burst_s')
    aegean.arch.declSignal('spm_ms','spm_masters')
    aegean.arch.declSignal('spm_ss','spm_slaves')

def setSPMSize(aegean,sizes):
    aegean.arch.decl('''
    type size_array is array(0 to NODES-1) of integer;
''')
    #name, constType, width, value
    s = ', '.join(str(math.ceil(math.log(size,2))) for size in sizes)
    aegean.arch.declConstant('SPM_WIDTH', 'size_array', 1, '('+ s +')')


def bindPatmos(patmos,p,ledPort=None,txdPort=None,rxdPort=None):

    patmos.entity.bindPort('clk','clk')
    patmos.entity.bindPort('reset','reset')
    patmos.entity.bindPort('io_comConf_M_Cmd','ocp_io_ms('+str(p)+').MCmd')
    patmos.entity.bindPort('io_comConf_M_Addr','ocp_io_ms('+str(p)+').MAddr')
    patmos.entity.bindPort('io_comConf_M_Data','ocp_io_ms('+str(p)+').MData')
    patmos.entity.bindPort('io_comConf_M_ByteEn','ocp_io_ms('+str(p)+').MByteEn')
    patmos.entity.bindPort('io_comConf_M_RespAccept','ocp_io_ms('+str(p)+').MRespAccept')
    patmos.entity.bindPort('io_comConf_S_Resp','ocp_io_ss('+str(p)+').SResp')
    patmos.entity.bindPort('io_comConf_S_Data','ocp_io_ss('+str(p)+').SData')
    patmos.entity.bindPort('io_comConf_S_CmdAccept','ocp_io_ss('+str(p)+').SCmdAccept')
    patmos.entity.bindPort('io_comSpm_M_Cmd','ocp_core_ms('+str(p)+').MCmd')
    patmos.entity.bindPort('io_comSpm_M_Addr','ocp_core_ms('+str(p)+').MAddr')
    patmos.entity.bindPort('io_comSpm_M_Data','ocp_core_ms('+str(p)+').MData')
    patmos.entity.bindPort('io_comSpm_M_ByteEn','ocp_core_ms('+str(p)+').MByteEn')
    patmos.entity.bindPort('io_comSpm_S_Resp','ocp_core_ss('+str(p)+').SResp')
    patmos.entity.bindPort('io_comSpm_S_Data','ocp_core_ss('+str(p)+').SData')
    patmos.entity.bindPort('io_cpuInfoPins_id','std_logic_vector(to_unsigned('+str(p)+',32))')
    patmos.entity.bindPort('io_memPort_M_Cmd','ocp_burst_ms('+str(p)+').MCmd')
    patmos.entity.bindPort('io_memPort_M_Addr','ocp_burst_ms('+str(p)+').MAddr')
    patmos.entity.bindPort('io_memPort_M_Data','ocp_burst_ms('+str(p)+').MData')
    patmos.entity.bindPort('io_memPort_M_DataValid','ocp_burst_ms('+str(p)+').MDataValid')
    patmos.entity.bindPort('io_memPort_M_DataByteEn','ocp_burst_ms('+str(p)+').MDataByteEn')
    patmos.entity.bindPort('io_memPort_S_Resp','ocp_burst_ss('+str(p)+').SResp')
    patmos.entity.bindPort('io_memPort_S_Data','ocp_burst_ss('+str(p)+').SData')
    patmos.entity.bindPort('io_memPort_S_CmdAccept','ocp_burst_ss('+str(p)+').SCmdAccept')
    patmos.entity.bindPort('io_memPort_S_DataAccept','ocp_burst_ss('+str(p)+').SDataAccept')

    if ledPort is not None:
        patmos.entity.bindPort('io_ledsPins_led',ledPort)
    if txdPort is not None:
        patmos.entity.bindPort('io_uartPins_tx',txdPort)
    if rxdPort is not None:
        patmos.entity.bindPort('io_uartPins_rx',rxdPort)


def bindNoc(noc):
    noc.entity.bindPort('clk','clk')
    noc.entity.bindPort('reset','reset')
    noc.entity.bindPort('ocp_io_ms','ocp_io_ms')
    noc.entity.bindPort('ocp_io_ss','ocp_io_ss')
    noc.entity.bindPort('spm_ports_m','spm_ms')
    noc.entity.bindPort('spm_ports_s','spm_ss')

def addSPM():
    return '''
    spms : for i in 0 to NODES-1 generate
        spm : entity work.com_spm
        generic map(
            SPM_IDX_SIZE => SPM_WIDTH(i)
            )
        port map(
            p_clk => clk,
            n_clk => clk,
            reset => reset,
            ocp_core_m => ocp_core_ms(i),
            ocp_core_s => ocp_core_ss(i),
            spm_m => spm_ms(i),
            spm_s => spm_ss(i)
            );
    end generate ; -- spms
'''


def bindSram(sram):
    sram.entity.bindPort('clk','clk')
    sram.entity.bindPort('reset','reset')
    sram.entity.bindPort('io_ocp_port_M_Cmd','ocp_burst_m_mem.MCmd')
    sram.entity.bindPort('io_ocp_port_M_Addr','ocp_burst_m_mem.MAddr')
    sram.entity.bindPort('io_ocp_port_M_Data','ocp_burst_m_mem.MData')
    sram.entity.bindPort('io_ocp_port_M_DataValid','ocp_burst_m_mem.MDataValid')
    sram.entity.bindPort('io_ocp_port_M_DataByteEn','ocp_burst_m_mem.MDataByteEn')
    sram.entity.bindPort('io_ocp_port_S_Resp','ocp_burst_s_mem.SResp')
    sram.entity.bindPort('io_ocp_port_S_Data','ocp_burst_s_mem.SData')
    sram.entity.bindPort('io_ocp_port_S_CmdAccept','ocp_burst_s_mem.SCmdAccept')
    sram.entity.bindPort('io_ocp_port_S_DataAccept','ocp_burst_s_mem.SDataAccept')
    sram.entity.bindPort('io_ram_out_addr','io_sramPins_ram_out_addr')
    sram.entity.bindPort('io_ram_out_dout_ena','io_sramPins_ram_out_dout_ena')
    sram.entity.bindPort('io_ram_out_nadsc','io_sramPins_ram_out_nadsc')
    sram.entity.bindPort('io_ram_out_noe','io_sramPins_ram_out_noe')
    sram.entity.bindPort('io_ram_out_nbwe','io_sramPins_ram_out_nbwe')
    sram.entity.bindPort('io_ram_out_nbw','io_sramPins_ram_out_nbw')
    sram.entity.bindPort('io_ram_out_ngw','io_sramPins_ram_out_ngw')
    sram.entity.bindPort('io_ram_out_nce1','io_sramPins_ram_out_nce1')
    sram.entity.bindPort('io_ram_out_ce2','io_sramPins_ram_out_ce2')
    sram.entity.bindPort('io_ram_out_nce3','io_sramPins_ram_out_nce3')
    sram.entity.bindPort('io_ram_out_nadsp','io_sramPins_ram_out_nadsp')
    sram.entity.bindPort('io_ram_out_nadv','io_sramPins_ram_out_nadv')
    sram.entity.bindPort('io_ram_out_dout','io_sramPins_ram_out_dout')
    sram.entity.bindPort('io_ram_in_din','io_sramPins_ram_in_din')

def bindArbiter(arbiter,numPorts):
    arbiter.entity.bindPort('clk','clk')
    arbiter.entity.bindPort('reset','reset')
    arbiter.entity.bindPort('io_slave_M_Cmd','ocp_burst_m_mem.MCmd')
    arbiter.entity.bindPort('io_slave_M_Addr','ocp_burst_m_mem.MAddr')
    arbiter.entity.bindPort('io_slave_M_Data','ocp_burst_m_mem.MData')
    arbiter.entity.bindPort('io_slave_M_DataValid','ocp_burst_m_mem.MDataValid')
    arbiter.entity.bindPort('io_slave_M_DataByteEn','ocp_burst_m_mem.MDataByteEn')
    arbiter.entity.bindPort('io_slave_S_Resp','ocp_burst_s_mem.SResp')
    arbiter.entity.bindPort('io_slave_S_Data','ocp_burst_s_mem.SData')
    arbiter.entity.bindPort('io_slave_S_CmdAccept','ocp_burst_s_mem.SCmdAccept')
    arbiter.entity.bindPort('io_slave_S_DataAccept','ocp_burst_s_mem.SDataAccept')

    for i in range(0,numPorts):
        arbiter.entity.bindPort('io_master_'+str(i)+'_M_Cmd       ','ocp_burst_ms('+str(i)+').MCmd')
        arbiter.entity.bindPort('io_master_'+str(i)+'_M_Addr      ','ocp_burst_ms('+str(i)+').MAddr')
        arbiter.entity.bindPort('io_master_'+str(i)+'_M_Data      ','ocp_burst_ms('+str(i)+').MData')
        arbiter.entity.bindPort('io_master_'+str(i)+'_M_DataValid ','ocp_burst_ms('+str(i)+').MDataValid')
        arbiter.entity.bindPort('io_master_'+str(i)+'_M_DataByteEn','ocp_burst_ms('+str(i)+').MDataByteEn')
        arbiter.entity.bindPort('io_master_'+str(i)+'_S_Resp      ','ocp_burst_ss('+str(i)+').SResp')
        arbiter.entity.bindPort('io_master_'+str(i)+'_S_Data      ','ocp_burst_ss('+str(i)+').SData')
        arbiter.entity.bindPort('io_master_'+str(i)+'_S_CmdAccept ','ocp_burst_ss('+str(i)+').SCmdAccept')
        arbiter.entity.bindPort('io_master_'+str(i)+'_S_DataAccept','ocp_burst_ss('+str(i)+').SDataAccept')

