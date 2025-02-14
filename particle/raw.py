from typing import Tuple
import serial
import time


UPDATE_RATE = 120


class Raw:
    def __init__(self):
        self._serial = serial.Serial("/dev/ttyUSB1", baudrate=9600)

    def get_averaged_readings(self) -> Tuple[int, int]:
        start_time = time.time()
        readings = []
        while True:
            readings.append(self.get_single_reading())
            if time.time() - start_time > UPDATE_RATE:
                return int(sum(readings) / len(readings))

    def get_single_reading(self) -> int:
        while True:
            input_line = self._serial.readline().decode()
            if "Raw Concentration:" in input_line:
                print(f"Reading: {input_line}")
                (_, count) = input_line.split(":")
                return int(count)
