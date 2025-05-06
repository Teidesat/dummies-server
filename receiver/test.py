from bitarray import bitarray
from itertools import combinations
from bitarray.util import ba2base, base2ba
import random

def oversample(signal: bitarray, factor: int) -> bitarray:
    """
    Oversample the bits of the signal by the given factor
    """
    oversampled = bitarray()
    for bit in signal:
        for i in range(factor):
            random_bit = random.randint(0, 10)
            if random_bit >= 1:
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
    output_bits = bitarray()
    for i in range(num_bits):
        bit_window = signal[start_idx + i * bit_len : start_idx + (i + 1) * bit_len]
        if not bit_window:
            break
        majority = bit_window.count(1) > len(bit_window) // 2
        output_bits.append(int(majority))
    return output_bits


def oversample_pattern(pattern, rate):
    """Repeat each bit in the pattern `rate` times."""
    result = bitarray()
    for bit in pattern:
        result.extend([bit] * rate)
    return result

def generate_oversampled_header_variants(header, max_flips=2, rates=range(2, 10)):
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

def detect_oversampling(signal, header, rate_range=(2, 10), max_flips=1):
    """Estimate oversampling rate and alignment from oversampled header."""
    header_variants = generate_oversampled_header_variants(header, max_flips, rates=range(*rate_range))
    best_score = -1
    best_params = (None, None, None)  # (rate, offset, pattern)
    print(f"variants: {len(header_variants)}")
    for rate, patterns in header_variants.items():
        for pattern in patterns:
            score, idx = cross_correlate_score(signal, pattern)
            print(f"Rate: {rate}, Score: {score}, Index: {idx}")
            if score > best_score and (len(signal) - idx) % rate == 0:  # Ensure it's a significant match
                best_score = score
                best_params = (rate, idx, pattern)
                #print(f"New best score: {best_score}, Rate: {rate}, Offset: {idx}")

    return best_params  # oversampling, offset, matched_oversampled_header


header = bits_from_bytes(b"TEIDESAT")
tail = bits_from_bytes(b"TASEDIET")
#print(oversample(test_header, 2))
signal = bits_from_bytes(b"{\"experiment_id\": \"CO_D3.0-A0.0-I0.5-F30.0-L1.0-Mm\", \"message\": \"011000010111001101100100\", \"settings\": {\"dummy_distance\": 3.0, \"transmitter_angle\": 0.0, \"led_intensity\": 0.5, \"blinking_frequency\": 30.0, \"messages_batch\": 1.0}}")
#print(signal)
#print(header)
oversampled = oversample(header + signal + tail, 4)
#print(oversampled)
oversampling, offset, matched_header = detect_oversampling(oversampled, header, rate_range=(2, 10))

# Estimate total bits from remaining length
bits_after_header = (len(oversampled) - offset) // oversampling
#print(f"Bits after header: {bits_after_header}")
denoised = denoise_oversampled(oversampled, offset, oversampling, bits_after_header)
#print(f"Denoised: {denoised}")

#print(f"Detected oversampling: {oversampling}, Offset: {offset}")
denoised = ba2base(16, denoised)
print("hex bits:", denoised)
print("Recovered bits:", bytearray.fromhex(denoised).decode())