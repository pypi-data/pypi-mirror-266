
from ctypes import (
    c_char,
    c_double,
    c_int,
    c_uint,
    c_short,
    c_ushort,
    c_long,
    c_ulong,
    c_longlong,
    c_ulonglong,
    c_byte,
    c_ubyte,
    c_void_p,
    c_bool,
    c_wchar_p,
    c_char_p,
    byref,
    POINTER,
)
from ctypes import Structure


class canmsg(Structure):
    _fields_ = [
        ("id", c_ulong),
        ("data", c_ubyte * 8),
        ("len", c_ubyte),
        ("flags", c_ushort),     # bit 0 - RTR, 2 - EFF
        ("ts", c_ulong),
    ]

class canwait(Structure):
    _fields_ = [
        ("chan", c_ubyte),
        ("wflags", c_ubyte),
        ("rflags", c_ubyte),
    ]

CI_BRDSTR_SIZE = 64

class canboard(Structure):
    _fields_ = [
        ("brdnum", c_ubyte),
        ("hwver", c_ulong),
        ("chip", c_short * 4),
        ("name", c_char * CI_BRDSTR_SIZE),
        ("manufact", c_char * CI_BRDSTR_SIZE),
    ]

class canerrs(Structure):
    _fields_ = [
        ("ewl", c_ushort),
        ("boff", c_ushort),
        ("hwovr", c_ushort),
        ("swovr", c_ushort),
        ("wtout", c_ushort),
    ]

class chipstat(Structure):
    _fields_ = [
        ("type", c_ushort),
        ("brdnum", c_ushort),
        ("irq", c_long),
        ("baddr", c_ulong),
        ("state", c_ubyte),
        ("hovr_cnt", c_ulong),
        ("sovr_cnt", c_ulong),
        ("_pad", c_char * 32),
    ]

class sja1000stat(Structure):
    _fields_ = [
        ("type", c_short),
        ("brdnum", c_short),
        ("irq", c_long),
        ("baddr", c_ulong),
        ("state", c_ubyte),
        ("hovr_cnt", c_ulong),
        ("sovr_cnt", c_ulong),
        ("mode", c_ubyte),
        ("stat", c_ubyte),
        ("inten", c_ubyte),
        ("clkdiv", c_ubyte),
        ("ecc", c_ubyte),
        ("ewl", c_ubyte),
        ("rxec", c_ubyte),
        ("txec", c_ubyte),
        ("rxmc", c_ubyte),
        ("acode", c_ulong),
        ("amask", c_ulong),
        ("btr0", c_ubyte),
        ("btr1", c_ubyte),
        ("outctl", c_ubyte),
        ("_pad", c_char * 8),
    ]

CI_CHSTAT_MAXLEN = 16
CI_CHSTAT_STRNUM = 32

class chstat_desc(Structure):
    _fields_ = [
        ("name", (c_char * CI_CHSTAT_STRNUM) * CI_CHSTAT_MAXLEN),
        ("val", (c_char * CI_CHSTAT_STRNUM) * CI_CHSTAT_MAXLEN),
    ]

CI_BRD_NUMS      = 8
CI_CHAN_NUMS     = 8
CIQUE_RC         = 0
CIQUE_TR         = 1
CIQUE_DEFSIZE_RC = 4096
CIQUE_DEFSIZE_TR = 64

CIQUE_RC_THRESHOLD_DEF = 1
CIQUE_TR_THRESHOLD_DEF = CIQUE_DEFSIZE_TR

CI_WRITE_TIMEOUT_DEF = 20
# MAX is not used, backcompat
CI_WRITE_TIMEOUT_MAX = 500

# states of CAN controller
CAN_INIT    = 0
CAN_RUNNING = 1

# predefined baud rates (recommended by CiA)
# Phillips SJA1000 (16 MHz)

BCI_1M_bt0   = c_ubyte(int("0x00", 16))
BCI_1M_bt1   = c_ubyte(int("0x14", 16))
BCI_800K_bt0 = c_ubyte(int("0x00", 16))
BCI_800K_bt1 = c_ubyte(int("0x16", 16))
BCI_500K_bt0 = c_ubyte(int("0x00", 16))
BCI_500K_bt1 = c_ubyte(int("0x1c", 16))
BCI_250K_bt0 = c_ubyte(int("0x01", 16))
BCI_250K_bt1 = c_ubyte(int("0x1c", 16))
BCI_125K_bt0 = c_ubyte(int("0x03", 16))
BCI_125K_bt1 = c_ubyte(int("0x1c", 16))
BCI_100K_bt0 = c_ubyte(int("0x04", 16))
BCI_100K_bt1 = c_ubyte(int("0x1c", 16))
BCI_50K_bt0  = c_ubyte(int("0x09", 16))
BCI_50K_bt1  = c_ubyte(int("0x1c", 16))
BCI_20K_bt0  = c_ubyte(int("0x18", 16))
BCI_20K_bt1  = c_ubyte(int("0x1c", 16))
BCI_10K_bt0  = c_ubyte(int("0x31", 16))
BCI_10K_bt1  = c_ubyte(int("0x1c", 16))
BCI_1M       = (BCI_1M_bt0, BCI_1M_bt1)
BCI_800K     = (BCI_800K_bt0, BCI_800K_bt1)
BCI_500K     = (BCI_500K_bt0, BCI_500K_bt1)
BCI_250K     = (BCI_250K_bt0, BCI_250K_bt1)
BCI_125K     = (BCI_125K_bt0, BCI_125K_bt1)
BCI_100K     = (BCI_100K_bt0, BCI_100K_bt1)
BCI_50K      = (BCI_50K_bt0, BCI_50K_bt1)
BCI_20K      = (BCI_20K_bt0, BCI_20K_bt1)
BCI_10K      = (BCI_10K_bt0, BCI_10K_bt1)

# Error codes
ECIOK     = 0   # success
ECIGEN    = 1   # generic (not specified) error
ECIBUSY   = 2   # device or resourse busy
ECIMFAULT = 3   # memory fault
ECISTATE  = 4   # function can't be called for chip in current state
ECIINCALL = 5   # invalid call, function can't be called for this object
ECIINVAL  = 6   # invalid parameter
ECIACCES  = 7   # can not access resource
ECINOSYS  = 8   # function or feature not implemented
ECIIO     = 9   # input/output error
ECINODEV  = 10  # no such device or object
ECIINTR   = 11  # call was interrupted by event
ECINORES  = 12  # no resources
ECITOUT   = 13  # time out occured

# Flags for CiOpen
CIO_BLOCK = int("0x1", 16)         # ignored (block mode was removed in CHAI 2.x
CIO_CAN11 = int("0x2", 16)
CIO_CAN29 = int("0x4", 16)

# Flags for CiWaitEvent
CI_WAIT_RC = int("0x1", 16)
CI_WAIT_TR = int("0x2", 16)
CI_WAIT_ER = int("0x4", 16)

# Commands for CiSetLom
CI_LOM_OFF = 0
CI_LOM_ON  = 1

CI_CMD_GET = 0
CI_CMD_SET = 1

CI_OFF = 0
CI_ON  = 1

# Transmit status
CI_TR_COMPLETE_OK    = int("0x0", 16)
CI_TR_COMPLETE_ABORT = int("0x1", 16)
CI_TR_INCOMPLETE     = int("0x2", 16)
CI_TR_DELAY          = int("0x3", 16)

# Transmit cancel status
CI_TRCANCEL_TRANSMITTED    = int("0x0", 16)
CI_TRCANCEL_ABORTED        = int("0x1", 16)
CI_TRCANCEL_NOTRANSMISSION = int("0x2", 16)
CI_TRCANCEL_DELAYABORTED   = int("0x3", 16)

# Bits in canmsg_t.flags field
MSG_RTR       = 0
MSG_FF        = 2       # if set - extended frame format is used
FRAME_RTR     = int("0x1", 16)
FRAME_EFF     = int("0x4", 16)
FRAME_TRDELAY = int("0x10", 16)

# CAN-controller types 
CHIP_UNKNOWN = 0
SJA1000      = 1
EMU          = 2
MSCAN        = 3

# Manufacturers 
MANUF_UNKNOWN = 0
MARATHON      = 1
SA            = 2
FREESCALE     = 3

# CAN adapter types 
BRD_UNKNOWN      = 0
CAN_BUS_ISA      = 1
CAN_BUS_MICROPC  = 2
CAN_BUS_PCI      = 3
CAN_EMU          = 4
CAN2_PCI_M       = 5
MPC5200TQM       = 6
CAN_BUS_USB      = 7
CAN_BUS_PCI_E    = 8
CAN_BUS_USB_NP   = 9
CAN_BUS_USB_NPS  = 10

# The functions defined in chai.h
# Function name, response type, arguments tuple, error function (Optional)
_DLL_FUNCTIONS = [
    ("CiInit", c_short, (c_void_p,)),
    ("CiOpen", c_short, (c_ubyte, c_ubyte)),
    ("CiClose", c_short, (c_ubyte,)),
    ("CiStart", c_short, (c_ubyte,)),
    ("CiStop", c_short, (c_ubyte,)),
    ("CiSetFilter", c_short, (c_ubyte, c_ulong, c_ulong)),
    ("CiSetBaud", c_short, (c_ubyte, c_ubyte, c_ubyte)),
    ("CiTransmit", c_short, (c_ubyte, POINTER(canmsg))),
    ("CiTrCancel", c_short, (c_ubyte, POINTER(c_ushort))),
    ("CiTrStat", c_short, (c_ubyte, POINTER(c_ushort))),
    ("CiRead", c_short, (c_ubyte, POINTER(canmsg), c_ushort)),
    ("CiErrsGetClear", c_short, (c_ubyte, POINTER(canerrs))),
    ("CiWaitEvent", c_short, (POINTER(canwait), c_int, c_int)),

    ("CiChipStat", c_short, (c_ubyte, POINTER(chipstat))),
    ("CiChipStatToStr", c_short, (POINTER(chipstat), POINTER(chstat_desc))),
    ("CiBoardInfo", c_short, (POINTER(canboard),)),
    ("CiGetFirmwareVer", c_short, (c_ubyte, POINTER(c_ulong))),
    ("CiGetLibVer", c_ulong, (c_void_p,)),
    ("CiGetDrvVer", c_ulong, (c_void_p,)),

    ("CiTrQueThreshold", c_short, (c_ubyte, c_short, POINTER(c_ushort))),
    ("CiRcQueThreshold", c_short, (c_ubyte, c_short, POINTER(c_ushort))),
    ("CiRcQueResize", c_short, (c_ubyte, c_ushort)),
    ("CiRcQueCancel", c_short, (c_ubyte, POINTER(c_ushort))),
    ("CiRcQueGetCnt", c_short, (c_ubyte, POINTER(c_ushort))),
    ("CiBoardGetSerial", c_short, (c_ubyte, c_char_p, c_ushort)),
    ("CiHwReset", c_short, (c_ubyte,)),
    ("CiSetLom", c_short, (c_ubyte, c_ubyte)),
    ("CiStrError", c_void_p, (c_short, c_char_p, c_short)),
    ("CiPerror", c_void_p, (c_short, c_char_p)),

    ("msg_zero", c_void_p, (POINTER(canmsg),)),
    ("msg_isrtr", c_short, (POINTER(canmsg),)),
    ("msg_setrtr", c_void_p, (POINTER(canmsg),)),
    ("msg_iseff", c_short, (POINTER(canmsg),)),
    ("msg_seteff", c_void_p, (POINTER(canmsg),)),
    ("msg_setdelaytr", c_void_p, (POINTER(canmsg), c_ulong)),
]
