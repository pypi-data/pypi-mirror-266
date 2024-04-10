
# standard library imports
from ctypes import c_int, c_ushort, c_long, c_ulong, c_ubyte, c_ulonglong, byref
from typing import Optional, Union
import logging
import time
import platform
import sys
from typing import Tuple, List

# imports from the python-can module
from can.message import Message
from can.bus import BusABC, BusState
from can.exceptions import CanOperationError, CanInitializationError, CanTimeoutError, CanInterfaceNotImplementedError
from can.ctypesutil import CLibrary, HANDLE

# import CHAI library
from . import chai_header as chai


_CANLIB = CLibrary("C:\\Program Files (x86)\\CHAI-2.14.0\\x64\\chai.dll")
for function, restype, argtypes in chai._DLL_FUNCTIONS:
    _CANLIB.map_symbol(function, restype, argtypes)


class ChaiBus(BusABC):
    """
    A plugin for the python-can module, that allows the use of CAN interfaces that rely on the CHAI driver.
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(channel=0)
        self.ch_rx: int = 0
        error_code = _CANLIB.CiInit(None)
        print(f"init: {error_code}")

    def ch_init(self,
                ch=0,
                frame=chai.CIO_CAN11|chai.CIO_CAN29,
                baud=chai.BCI_500K):
        error_code = _CANLIB.CiStop(c_ubyte(ch))
        print(f"stop: {error_code}")
        error_code = _CANLIB.CiOpen(c_ubyte(ch), c_ubyte(frame))
        print(f"open: {error_code}")
        error_code = _CANLIB.CiSetBaud(c_ubyte(ch), *baud)
        print(f"baud: {error_code}")

    def ch_start(self, ch=0):
        error_code = _CANLIB.CiStart(c_ubyte(ch))
        print(f"start: {error_code}")

    def send(self, msg: Message, timeout: Optional[float] = None) -> None:
        msg_struct = chai.canmsg()
        msg_struct.id = c_ulong(msg.arbitration_id)
        msg_struct.len = c_ubyte(msg.dlc)
        # copy data
        data = c_ubyte * len(msg.data)
        msg_struct.data = data(*msg.data)
        error_code = _CANLIB.CiTransmit(c_ubyte(msg.channel), byref(msg_struct))
        # print(f"tx: {error_code}")

    def _recv_internal(
        self, timeout: Optional[float]
    ) -> Tuple[Optional[Message], bool]:
        msg_struct = chai.canmsg()
        self.ch_rx = self.ch_rx + 1 if self.ch_rx == 0 else 0
        if (res:= _CANLIB.CiRead(c_ubyte(self.ch_rx), byref(msg_struct), c_ushort(1))) >= 0:
            msg: Message = Message(channel=self.ch_rx,
                                   arbitration_id=msg_struct.id,
                                   dlc=msg_struct.len,
                                   data=[msg_struct.data[i] for i in range(msg_struct.len)],
                                   timestamp=msg_struct.ts/1000000)
            return (msg, False)
        else:
            return (None, False)
