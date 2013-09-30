library ieee;
use ieee.std_logic_1164.all;

package ocp is

       -- OCP
    constant OCP_CMD_WIDTH  : integer := 3;     -- 8 possible cmds --> 2
    constant OCP_ADDR_WIDTH : integer := 32;    --32
    constant OCP_DATA_WIDTH : integer := 32;
    constant OCP_BYTE_WIDTH : integer := OCP_DATA_WIDTH/8;
    constant OCP_RESP_WIDTH : integer := 2;

    constant OCP_CMD_IDLE : std_logic_vector(OCP_CMD_WIDTH-1 downto 0) := "000";
    constant OCP_CMD_WRITE: std_logic_vector(OCP_CMD_WIDTH-1 downto 0) := "001";
    constant OCP_CMD_READ : std_logic_vector(OCP_CMD_WIDTH-1 downto 0) := "010";

    constant OCP_RESP_NO   : std_logic_vector(OCP_RESP_WIDTH-1 downto 0) := "00";
    constant OCP_RESP_VALID: std_logic_vector(OCP_RESP_WIDTH-1 downto 0) := "01";
    constant OCP_RESP_ERROR: std_logic_vector(OCP_RESP_WIDTH-1 downto 0) := "10";
    constant OCP_RESP_FAULT: std_logic_vector(OCP_RESP_WIDTH-1 downto 0) := "11";

    type ocp_core_m is record
        MCmd        : std_logic_vector(OCP_CMD_WIDTH-1 downto 0);
        MAddr       : std_logic_vector(OCP_ADDR_WIDTH-1 downto 0);
        MData       : std_logic_vector(OCP_DATA_WIDTH-1 downto 0);
        MByteEn     : std_logic_vector(OCP_BYTE_WIDTH-1 downto 0);
    end record;

    type ocp_core_s is record
        SResp       : std_logic_vector(OCP_RESP_WIDTH-1 downto 0);
        SData       : std_logic_vector(OCP_DATA_WIDTH-1 downto 0);
    end record;

    type ocp_io_m is record
        MCmd        : std_logic_vector(OCP_CMD_WIDTH-1 downto 0);
        MAddr       : std_logic_vector(OCP_ADDR_WIDTH-1 downto 0);
        MData       : std_logic_vector(OCP_DATA_WIDTH-1 downto 0);
        MByteEn     : std_logic_vector(OCP_BYTE_WIDTH-1 downto 0);
        MRespAccept : std_logic;
    end record;

    type ocp_io_s is record
        SResp       : std_logic_vector(OCP_RESP_WIDTH-1 downto 0);
        SData       : std_logic_vector(OCP_DATA_WIDTH-1 downto 0);
        SCmdAccept  : std_logic;
    end record;

    type ocp_burst_m is record
        MCmd        : std_logic_vector(OCP_CMD_WIDTH-1 downto 0);
        MAddr       : std_logic_vector(OCP_ADDR_WIDTH-1 downto 0);
        MData       : std_logic_vector(OCP_DATA_WIDTH-1 downto 0);
        MDataByteEn : std_logic_vector(OCP_BYTE_WIDTH-1 downto 0);
        MDataValid  : std_logic;
    end record;

    type ocp_burst_s is record
        SResp       : std_logic_vector(OCP_RESP_WIDTH-1 downto 0);
        SData       : std_logic_vector(OCP_DATA_WIDTH-1 downto 0);
        SCmdAccept  : std_logic;
        SDataAccept : std_logic;
    end record;


end package ; -- ocp
