from dataclasses import dataclass
from enum import Enum
import time
import asyncio
from decimal import Decimal
from instrument import Instrument, InstrumentException, NoResponse
import serial


class DisplayMode(Enum):
    Single = 0
    Dual = 1


class ReadingRate(Enum):
    Slow = "S"
    Medium = "M"
    Fast = "F"


class Function(Enum):
    Vdc = 0
    Vac = 1
    Res2Wire = 2
    Res4Wire = 3
    Adc = 4
    Aac = 5
    Diode = 6
    Hz = 7
    Vacdc = 8
    Aacdc = 9


@dataclass
class R0Info:
    compare_mode: bool
    relative_mode: bool
    db_mode: bool
    dbm_mode: bool
    display_mode: DisplayMode
    reading_rate: ReadingRate
    function1: Function


def bit_set(num, pos):
    return num & (1 << pos) != 0


def decode_r0(response):
    if len(response) not in [8, 10]:
        raise InstrumentException(f'BK5492 bad response: {response}')
    
    h = int(response[:2], 16)
    g = int(response[2:4], 16)
    v = int(response[4])
    x = response[5]
    f1 = int(response[6])

    info = R0Info(
        compare_mode=bit_set(h, 7),
        relative_mode=bit_set(h, 6),
        db_mode=bit_set(h, 5),
        dbm_mode=bit_set(h, 4),
        display_mode=DisplayMode((h & (1 << 3) >> 3)),
        reading_rate=ReadingRate(x),
        function1=Function(f1)
    )
    
    return info


class BK5492(Instrument):
    def __init__(self, verbose=False):
        # for port, desc, hwid in list_ports.comports():
        #     print(f"{port}: {desc} [{hwid}]")
        
        self.port = "/dev/ttyUSB0"
        self.baud = 9600
        self.timeout = 0.1
        self.verbose = verbose
        self.change_delay = 5

    def send_cmd(self, cmd):
        with serial.Serial(self.port, self.baud, timeout=self.timeout) as ser:
            tx = cmd.encode("ascii") + b"\r\n"

            # todo Use logging
            if self.verbose:
                print(">", tx)

            ser.write(tx)
            ser.flush()
            time.sleep(0.05) # This seems to reduce the odds of bad results?
            rx = ser.read_until(b"\r\n")
            
            if self.verbose:
                print("<", rx)

            # # Not sure why, but sometimes the BK5492 gives bad responses
            # bad_responses = [b"\r\n", b">\r\n"]

            # if rx in bad_responses:
            #     print(">", tx)
            #     ser.write(tx)
            #     time.sleep(0.1)
            #     rx = ser.read_until(b"\r\n")
            #     print("<", rx)

            if rx == b"":
                raise NoResponse(f"No response from BK5492 at {self.port}")

            return rx.strip().decode()
    
    async def change_to_vdc(self):
        response = self.send_cmd("R0")
        response = decode_r0(response)
    
        if response.function1 != Function.Vdc:
            self.send_cmd("S100S")
            await asyncio.sleep(self.change_delay)


    async def change_to_vac(self):
        response = self.send_cmd("R0")
        response = decode_r0(response)
    
        if response.function1 != Function.Vac:
            self.send_cmd("S110S")
            await asyncio.sleep(self.change_delay)


    async def measure_vdc(self):
        await self.change_to_vdc()
        response = self.send_cmd("R1")
        return Decimal(response)

    async def measure_mvdc(self):
        measurement = await self.measure_vdc()
        return measurement * Decimal("1000")
    
    async def measure_vac(self):
        await self.change_to_vac()
        response = self.send_cmd("R1")
        return Decimal(response)

    async def measure_mvac(self):
        measurement = await self.measure_vac()
        return measurement * Decimal("1000")

    @property
    def firmware(self):
        result = self.send_cmd("RV")
        return result.split(",")[0]

    @property
    def model(self):
        result = self.send_cmd("RV")
        return {
            "5": "BK5491",
            "6": "BK5492",
        }[result.strip().split(",")[1]]