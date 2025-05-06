"""
Utility functions for the receiver server on the Optical Communications Experiment
"""
import Levenshtein
import json
from experiment import Experiment
from bitarray import bitarray
from itertools import combinations
from bitarray.util import ba2base, base2ba
import random

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


def oversample(signal: bitarray, factor: int) -> bitarray:
    """
    Oversample the bits of the signal by the given factor
    """
    oversampled = bitarray()
    for bit in signal:
        for i in range(factor):
            random_bit = random.randint(0, 10)
            if random_bit >= 0:
                oversampled.append(bit)
            else:
                if random.randint(0, 10) > 5:
                    oversampled.append(0)
                else:
                    oversampled.append(1)
            
    return oversampled


def bits_from_bytes(byte_data):
    """Convert bytes to bitarray."""
    ba = bitarray()
    ba.frombytes(byte_data)
    return ba

def generate_variants(header_bits, max_flips=1):
    """Generate header variants with up to max_flips bit flips."""
    variants = set()
    n = len(header_bits)
    variants.add(tuple(header_bits))
    for d in range(1, max_flips + 1):
        for indices in combinations(range(n), d):
            flipped = list(header_bits)
            for idx in indices:
                flipped[idx] ^= 1
            variants.add(tuple(flipped))
    return [bitarray(v) for v in variants]


def denoise_oversampled(signal, start_idx, bit_len, num_bits):
    """Apply majority voting from a start index over the bit length."""
    print("signal length", len(signal))
    print("signal", type(signal))
    print("start_idx", start_idx)
    print("bit_len", bit_len)
    print("num_bits", num_bits)
    output_bits = bitarray()
    counter = 0
    size = -1
    for i in range(num_bits):
        counter += 1
        bit_window = signal[start_idx + i * bit_len : start_idx + (i + 1) * bit_len]
        if size < len(bit_window):
            size = len(bit_window)
        if not bit_window:
            break
        majority = bit_window.count(1) > len(bit_window) // 2
        output_bits.append(int(majority))
    print("output_bits length", len(output_bits))
    print(counter, size)
    return output_bits


def oversample_pattern(pattern, rate):
    """Repeat each bit in the pattern `rate` times."""
    result = bitarray()
    for bit in pattern:
        result.extend([bit] * rate)
    return result

def generate_oversampled_header_variants(header, rates=range(2, 10)):
    """Generate oversampled header variants for all rates and flips."""
    variant_dict = {}
    for r in rates:
        variant_dict[r] = [oversample_pattern(header, r)]

    return variant_dict

def cross_correlate_score(signal, pattern):
    """Compute max match score of pattern against signal (bitwise)."""
    plen = len(pattern)
    max_score = -1
    best_idx = 0
    for i in range(len(signal) - plen):
        window = signal[i:i+plen]
        score = sum(a == b for a, b in zip(window, pattern)) / (0.5 * plen)
        if score > max_score:
            max_score = score
            best_idx = i
    return max_score, best_idx

def detect_oversampling(signal, header, rate_range=(2, 10)):
    """Estimate oversampling rate and alignment from oversampled header."""
    header_variants = generate_oversampled_header_variants(header, rates=range(*rate_range))
    best_score = -1
    best_params = (None, None)  # (rate, offset)
    print(f"variants: {len(header_variants)}")
    for rate, patterns in header_variants.items():
        for pattern in patterns:
            score, idx = cross_correlate_score(signal, pattern)
            print(f"Rate: {rate}, Score: {score}, Index: {idx}")
            if score > best_score and (len(signal) - idx) % rate == 0:  # Ensure it's a significant match
                best_score = score
                best_params = (rate, idx)
                #print(f"New best score: {best_score}, Rate: {rate}, Offset: {idx}")

    return best_params  # oversampling, offset
  
def denoise_message(message, header, tail):
    print("Message length:", len(message))
    if type(message) == bytes:
        message = bits_from_bytes(message)
    if type(header) == bytes:
        header = bits_from_bytes(header)
    if type(tail) == bytes:
        tail = bits_from_bytes(tail)
    print("Message length:", len(message))
    print("Received message:", message)
    print("Header:", header)
    print("Tail:", tail)
    oversampling, offset = detect_oversampling(message, header, rate_range=(2, 10))
    bits_after_header = (len(message) - offset) / oversampling
    print(f"Bits after header: {bits_after_header}")
    denoised = denoise_oversampled(message, offset, oversampling, int(bits_after_header))
    print("denoised bits:", denoised)
    denoised = ba2base(16, denoised)
    print("hex bits:", denoised)
    print("Recovered bits:", bytearray.fromhex(denoised).decode())
    return denoised