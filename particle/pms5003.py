from typing import Tuple, List
import serial
import time


UPDATE_RATE = 120


def average_of_tuple_list(list_of_tuples):
    """
    Calculates the average of corresponding elements in a list of tuples.

    Args:
      list_of_tuples: A list of tuples, where each tuple has the same length.

    Returns:
      A tuple containing the averages of the corresponding elements,
      or an empty tuple if the input list is empty.
    """
    if not list_of_tuples:
        return tuple()

    num_tuples = len(list_of_tuples)
    num_elements = len(list_of_tuples[0])
    averages = []

    for i in range(num_elements):
        total = sum(t[i] for t in list_of_tuples)
        averages.append(total / num_tuples)

    return tuple(averages)


class PMS:
    def __init__(self):
        self._serial = serial.Serial("/dev/ttyS0", baudrate=9600)

    def get_averaged_readings(self) -> Tuple[int, int, int]:
        start_time = time.time()
        readings = []
        while True:
            readings.append(self.get_single_reading())
            if time.time() - start_time > UPDATE_RATE:
                (small, medium, large) = average_of_tuple_list(readings)
                return (int(small), int(medium), int(large))

    def _get_chars(self, count: int = 1) -> bytes:
        return self._serial.read(count)

    def _convert_to_sixteen(self, msg: bytes) -> List[int]:
        if len(msg) %2 != 0:
            print(f"WARNING: Message length {len(msg)} is NOT DIVISIBLE BY TWO!")
            msg = msg[0:-1]
        retv = []
        for i in range(len(msg) / 2):
            retv.append(msg[i*2] * 0xff + msg[i*2+1])
        return retv

    def get_single_reading(self) -> Tuple[int, int, int]:
        while True:
            while self._get_chars() != b'B':
                pass
            if self._get_chars() == b'M':
                status_message = self._get_chars(count=30)
                int_message = self._convert_to_sixteen(status_message)
                print(f"Frame length: {int_message[0]}  PM1: {int_message[1]} PM2.5: {int_message[2]} PM10: {int_message[3]} Checksum: {hex(int_message[14])}")
                print(f"Counts: 0.3: {int_message[7]} 0.5: {int_message[8]} 1.0: {int_message[9]} 2.5: {int_message[10]} 5: {int_message[11]} 10: {int_message[12]}")
                return (int_message[8], int_message[10], int_message[12])
