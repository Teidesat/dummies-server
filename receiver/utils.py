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

"""
Flag to enable the detection of the oversampling rate. False by default, as it is not working for the moment
"""

ENABLE_OVERSAMPLING_DETECTION = False

class TimeOutWrapper:
    """
    Simple wrapper for a bool value to be changed in the timeout function
    """

    def __init__(self, initialTimeout: bool):
        self.timeout = initialTimeout


def addExperimentToBuffer(
    buffer: list[Experiment],
    experiment: Experiment,
    timeout: TimeOutWrapper,
):
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
            binary_char = binary_str[ind : ind + 8]
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
        if (
            Levenshtein.hamming(byte_seq[ind : ind + items_in_pattern], pattern)
            <= tolerance
        ):
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
    print("string", item)
    item = json.loads(item)
    print("dictionary", item)
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


def denoise_oversampled(message, offset, oversampling, bits_after_header):
    """Apply majority voting from a start index over the bit length."""
    print("signal length", len(message))
    print("signal", type(message))
    print("start_idx", offset)
    print("bit_len", oversampling)
    print("num_bits", bits_after_header)
    output_bits = bitarray()
    counter = 0
    size = -1
    for i in range(bits_after_header):
        counter += 1
        start = offset + i * oversampling
        end = start + oversampling
        bit_window = message[start:end]
        if size < len(bit_window):
            size = len(bit_window)
        majority = bit_window.count(1) > len(bit_window) // 2
        output_bits.append(1 if majority else 0)
    return output_bits


def oversample_pattern(pattern, rate):
    """Repeat each bit in the pattern `rate` times."""
    result = bitarray()
    for bit in pattern:
        result.extend([bit] * rate)
    return result


def generate_oversampled_variants(header, rates):
    """Generate oversampled header variants for all rates and flips."""
    variant_dict = {}
    if isinstance(rates, int):
        variant_dict = oversample_pattern(header, rates)
    else:
        for r in rates:
            variant_dict[r] = [oversample_pattern(header, r)]

    return variant_dict


def cross_correlate_score(signal, pattern):
    """Compute max match score of pattern against signal (bitwise)."""
    plen = len(pattern)
    max_score = -1
    best_idx = 0
    for i in range(len(signal) - plen):
        window = signal[i : i + plen]
        score = sum(a == b for a, b in zip(window, pattern)) / (0.5 * plen)
        if score > max_score:
            max_score = score
            best_idx = i
    return max_score, best_idx


def detect_oversampling(signal, header, rate_range):
    """Estimate oversampling rate and alignment from oversampled header."""
    header_variants = generate_oversampled_variants(header, rate_range)
    best_score = -1
    best_params = (None, None, None)  # (rate, offset, score)
    print(f"variants: {len(header_variants)}")
    for rate, patterns in header_variants.items():
        for pattern in patterns:
            score, idx = cross_correlate_score(signal, pattern)
            print(f"Rate: {rate}, Score: {score}, Index: {idx}")
            if score > best_score:  # Ensure it's a significant match
                best_score = score
                best_params = (rate, idx, best_score)
                # print(f"New best score: {best_score}, Rate: {rate}, Offset: {idx}")

    return best_params  # oversampling, offset, score


def denoise_message(
    message: bytes,
    header: bytes,
    tail: bytes,
    oversampling: int,
    header_status: bool,
):  # Check to exit the function, if the message is too small the header may be segmented
    if len(message) < 100:
        return bitarray(), header, tail, -1, False, message

    if type(message) == bytes:
        message = bits_from_bytes(message)
    if type(header) == bytes:
        header = bits_from_bytes(header)
    if type(tail) == bytes:
        tail = bits_from_bytes(tail)
    bits_after_header = -1
    bits_before_tail = -1
    # Case when we don't know the oversampling rate
    if oversampling < 0:
        if ENABLE_OVERSAMPLING_DETECTION:
            oversampling, offset, header_score = detect_oversampling(
                message,
                header,
                rate_range=range(2, 10),
            )
            bits_after_header = (len(message) - offset) // oversampling
            if header_score > 1.5:
                # If we have a good header score, we assume the header is present
                header_status = True
        else:
            # Assume rate is 1 (raw data) and find header directly
            oversampling = 1
            offset = find_byte_sequence(message.tobytes(), header.tobytes(), 5)
            if offset != -1: 
                # Offset points to the end of the header, we need to adjust
                offset = (offset + 1) * 8 # Convert bytes index to bit index
                header_score = 2.0
                header_status = True
                bits_after_header = len(message) - offset
            else: # If the header is not found, we try to find the tail, assuming the message has already started in another package
                offset = 0
                header_score = 0
                header_status = False
                bits_after_header = -1
    # If we have found a header, we check for a tail
    if header_status:
        if ENABLE_OVERSAMPLING_DETECTION:
            score = -1
            _, tail_start, score = detect_oversampling(message, tail, oversampling)
            # If we have found a tail, we know the message is complete, we calculate the amount of bits before the tail
            # We check for a high score to ensure we have a valid tail
            if score > 1.5:
                header_status = False
                # This value will just be from the beginning of the message to the tail start
                bits_before_tail = tail_start // oversampling
        else:
            # Find the tail directly, assuming the oversampling is 1
            tail_idx = find_byte_sequence(message.tobytes(), tail.tobytes(), 5)
            if tail_idx != -1:
                score = 2.0
                header_status = False
                tail_start = (tail_idx - len(tail.tobytes()) + 1) * 8 # Start bit of tail
                bits_before_tail = tail_start // oversampling
            else:
                score = 0
                tail_start = -1
    # We have a few different cases, header and tail in message, only header in message, only tail in message, no header or tail in message
    if ENABLE_OVERSAMPLING_DETECTION:
        if bits_after_header < 0 and bits_before_tail < 0:
            # No header or tail, but we should have oversampling
            denoised = denoise_oversampled(message, 0, oversampling, 0)
        elif bits_before_tail > 0 and bits_after_header > 0:
            # Both header and tail in message
            denoised = denoise_oversampled(
                message,
                offset,
                oversampling,
                bits_before_tail - (len(message) - bits_after_header),
            )
        elif bits_after_header > 0 and bits_before_tail < 0:
            # Only header in message
            denoised = denoise_oversampled(message, offset, oversampling, bits_after_header)
        elif bits_before_tail > 0 and bits_after_header < 0:
            # Only tail in message
            denoised = denoise_oversampled(message, 0, oversampling, bits_before_tail)
    else:
        # Just slice the message directly, no denoising
        if bits_after_header > 0 and bits_before_tail > 0:
            denoised = message[offset:tail_start]
        elif bits_after_header > 0:
            denoised = message[offset:]
        elif bits_before_tail > 0:
            denoised = message[:tail_start]
        else:
            denoised = bitarray()
    leftover = None
    # If we have a tail, we will return the leftover message, which is the part of the message that is not denoised
    # There is also the case that in this package we are treating there is more than one message, so we call recursively until all is treated and return it all together to later processing
    if ENABLE_OVERSAMPLING_DETECTION:
        step = len(denoised) * oversampling
    else:
        # In bypass, the step is just the message end + 64 bits of the tail
        step = bits_before_tail + 64 if bits_before_tail > 0 else -1
    if 0 < step < len(message):
        remaining_message = message[step:]
        aux_denoised, _, _, leftover = denoise_message(
            remaining_message, header, tail, -1, False
        )
        if aux_denoised:
            if isinstance(aux_denoised, bytes):
                denoised.frombytes(aux_denoised)
            else:
                denoised.extend(aux_denoised)

    print("denoised bits:", denoised)
    # Check if we actually have bits to convert to avoid crashes
    if len(denoised) > 0:
        denoised_bytes = denoised.tobytes()
        hex_str = ba2base(16, denoised)
        print("hex bits:", hex_str)
        try:
            print("Recovered bits:", bytearray.fromhex(hex_str).decode())
        except Exception as e:
            print("Could not decode to string yet:", e)
            
        denoised = denoised_bytes
    else:
        denoised = b"" 

    return denoised, oversampling, header_status, leftover