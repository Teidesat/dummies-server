"""
Utility functions for the receiver server on the Optical Communications Experiment
"""
import Levenshtein
import json
from experiment import Experiment

class TimeOutWrapper:
  """
  Simple wrapper for a bool value to be changed in the timeout function
  """
  def __init__(self, initialTimeout: bool):
    self.timeout = initialTimeout

def addExperimentToBuffer(buffer: list[Experiment], experiment: Experiment, timeout: TimeOutWrapper):
  """
  Timeout function, adds the given experiment to the buffer.
  """
  buffer.append(experiment)
  timeout.timeout = True
  
def binary_to_ascii(binary_str: str):
    """
    Transforms the given binary string to ASCII
    """
    try:
        result = ""
        for ind in range(0, len(binary_str), 8):
            binary_char =  binary_str[ind:ind + 8]
            ascii_code = int(binary_char, 2)
            ascii_char = format(ascii_code, "c")
            result += ascii_char
        return result
    except:
        print(f"Failed to transform {binary_str} into an ASCII string")
        return binary_str


def find_byte_sequence(byte_seq: bytes, pattern: bytes, tolerance: int):
    """
    Finds a the given byte pattern in the given byte sequence.

    Uses Humming's distance to calculate an error between the pattern and the
    evaluated section of the byte sequence. If the error is lower or equal to the
    given tolerance, the section will be considered a match.

    Returns the last index of the match if the pattern is found, -1 otherwise.
    """
    beginning = len(byte_seq) - 5004
    items_in_pattern = len(pattern)
    if beginning < 0:
      beginning = 0
    for ind in range(beginning, len(byte_seq)):
      if Levenshtein.hamming(byte_seq[ind:ind + items_in_pattern], pattern) <= tolerance:
        return ind + items_in_pattern - 1
    return -1
  
def calculate_checksum(byte_sequence: bytes):
    # Perform 16 bits XOR checksum
    checksum = 0
    for ind in range(0, len(byte_sequence), 2):
      byte = byte_sequence[ind + 1] << 8 | byte_sequence[ind]
      checksum ^= byte
    return checksum
  
def process_binary(byte_seq: bytes):
  item = byte_seq.decode("utf-8")
  print("string",item)
  item = json.loads(item)
  print("dictionary",item)
  return item
