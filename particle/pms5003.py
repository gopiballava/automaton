from dataclasses import asdict, dataclass
from typing import Tuple, List
import serial
import time


UPDATE_RATE = 120


@dataclass
class PlantowerReading:
    count0_3: int
    count0_5: int
    count1_0: int
    count2_5: int
    count5_0: int
    count10: int
    pm1_0: int
    pm2_5: int
    pm10: int


def average_plantowers(readings: List[PlantowerReading]) -> PlantowerReading:
    sum_dict = {}
    for key in asdict(readings[0]).keys():
        reading_sum = sum([asdict(reading)[key] for reading in readings])
        sum_dict[key] = int(reading_sum / len(readings))
    return PlantowerReading(**sum_dict)


class PMS:
    def __init__(self):
        self._serial = serial.Serial("/dev/ttyS0", baudrate=9600)

    def get_averaged_readings(self) -> PlantowerReading:
        start_time = time.time()
        readings = []
        while True:
            readings.append(self.get_single_reading())
            if time.time() - start_time > UPDATE_RATE:
                return average_plantowers(readings)

    def _get_chars(self, count: int = 1) -> bytes:
        return self._serial.read(count)

    def _convert_to_sixteen(self, msg: bytes) -> List[int]:
        if len(msg) % 2 != 0:
            print(f"WARNING: Message length {len(msg)} is NOT DIVISIBLE BY TWO!")
            msg = msg[0:-1]
        retv = []
        for i in range(len(msg) // 2):
            retv.append(msg[i * 2] * 0xFF + msg[i * 2 + 1])
        return retv

    def get_single_reading(self) -> PlantowerReading:
        while True:
            while self._get_chars() != b"B":
                pass
            if self._get_chars() == b"M":
                status_message = self._get_chars(count=30)
                int_message = self._convert_to_sixteen(status_message)
                print("\n=============")
                print(
                    f"Frame length: {int_message[0]}     PM1: {int_message[1]}     PM2.5: {int_message[2]}     PM10: {int_message[3]}     Checksum: {hex(int_message[14])}"
                )
                print(
                    f"Counts: 0.3: {int_message[7]}     0.5: {int_message[8]}     1.0: {int_message[9]}     2.5: {int_message[10]}     5: {int_message[11]}     10: {int_message[12]}"
                )
                print(f"Raw: {int_message}")
                return PlantowerReading(
                    pm1_0=int_message[1],
                    pm2_5=int_message[2],
                    pm10=int_message[3],
                    count0_3=int_message[7],
                    count0_5=int_message[8],
                    count1_0=int_message[9],
                    count2_5=int_message[10],
                    count5_0=int_message[11],
                    count10=int_message[12],
                )
