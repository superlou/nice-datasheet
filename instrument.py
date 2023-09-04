from serial.tools import list_ports


class Instrument:
    @property
    def model(self):
        raise NotImplementedError


class InstrumentException(Exception):
    pass


class NoResponse(Exception):
    pass

