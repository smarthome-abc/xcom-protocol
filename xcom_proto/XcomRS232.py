#! /usr/bin/env python3

##
# Class abstracting Xcom-RS232i serial protocol
##

import serial
import logging

from .parameters import ERROR_CODES
from .protocol import Package
from .XcomAbs import XcomAbs

SERIAL_TERMINATOR = b'\x0D\x0A'


class XcomRS232(XcomAbs):

    def __init__(self, serialDevice: str, baudrate: int, timeout=2):
        self.serialDevice = serialDevice
        self.baudrate = baudrate
        self.timeout = timeout
        self.log = logging.getLogger("XcomRS232")

    def sendPackage(self, package: Package) -> Package:
        data: bytes = package.getBytes() + SERIAL_TERMINATOR

        with serial.Serial(self.serialDevice, self.baudrate, timeout=self.timeout) as ser:
            self.log.debug(f" --> {data.hex()}")
            ser.write(data)

            response: bytes = ser.read_until(SERIAL_TERMINATOR, size=256)
            self.log.debug(f" <-- {response.hex()}")

        retPackage = Package.parseBytes(response[:-len(SERIAL_TERMINATOR)])
        self.log.debug(retPackage)

        if err := retPackage.getError():
            errCode = ERROR_CODES.get(err, "UNKNOWN ERROR")
            raise KeyError("Error received", errCode)

        return retPackage