from pyftdi.spi import SpiController
from typing import List


class AwilFt232h:
    def __init__(self, serial_number: str) -> None:
        self._url = f'ftdi://ftdi:232h:{serial_number}/1'

        self._spi = None
        self._slave = None

        self._cs = 0
        self._freq = 1E6
        self._mode = 0

        self._is_open = False

    def __def__(self) -> None:
        if self._spi is not None:
            self.close()

    def open(self, cs: int = None, freq: int = None, mode: int = None) -> None:
        self._spi = SpiController()
        self._spi.configure(self._url)
        self._is_open = True

        self._update_slave(cs=cs, freq=freq, mode=mode)

    def close(self) -> None:
        self._spi.close()
        self._spi.terminate()
        self._spi = None
        self._slave = None
        self._is_open = False

    def write(self, data: List[int], start: bool = True, stop: bool = True, cs: int = None, freq: int = None, mode: int = None) -> None:
        if self._is_open == False:
            raise Exception('SPI is not open')

        self._update_slave(cs=cs, freq=freq, mode=mode)
        self._slave.write(data, start, stop)

    def read(self, lenght: int, start: bool = True, stop: bool = True, cs: int = None, freq: int = None, mode: int = None) -> List[int]:
        if self._is_open == False:
            raise Exception('SPI is not open')

        self._update_slave(cs=cs, freq=freq, mode=mode)
        return list(self._slave.read(lenght, start, stop))

    def exchange(self, data: List[int], cs: int = None, freq: int = None, mode: int = None) -> bytes:
        if self._is_open == False:
            raise Exception('SPI is not open')

        self._update_slave(cs=cs, freq=freq, mode=mode)
        return list(self._slave.exchange(data, len(data), duplex=True))

    def _update_slave(self, cs: int = None, freq: int = None, mode: int = None) -> None:
        if self._is_open == False:
            raise Exception('SPI is not open')
        if cs is None and freq is None and mode is None:
            return

        if cs is not None:
            self._cs = cs
        if freq is not None:
            self._freq = freq
        if mode is not None:
            self._mode = mode

        self._slave = self._spi.get_port(cs=self._cs, freq=self._freq, mode=self._mode)
