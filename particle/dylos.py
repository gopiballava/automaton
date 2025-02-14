from typing import Tuple
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


class Dylos:
    def __init__(self):
        self._serial = serial.Serial("/dev/ttyUSB0", baudrate=9600)

    def get_averaged_readings(self) -> Tuple[int, int]:
        start_time = time.time()
        readings = []
        while True:
            readings.append(self.get_single_reading())
            if time.time() - start_time > UPDATE_RATE:
                (large, small) = average_of_tuple_list(readings)
                return (int(large), int(small))

    def get_single_reading(self) -> Tuple[int, int]:
        while True:
            input_line = self._serial.readline()
            if "," in input_line:
                print(f"Reading: {input_line}")
                (large, small) = input_line.split(",")
                return (int(large), int(small))
