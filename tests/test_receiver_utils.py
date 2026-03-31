import pytest
import sys 
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]/"receiver"))

from bitarray import bitarray
from utils import binary_to_ascii, calculate_checksum, oversample

def test_binary_to_ascii():  #test with the binary representation of "Hello world!"
    result = binary_to_ascii("010010000110010101101100011011000110111100100000011101110110111101110010011011000110010000100001")
    assert result == "Hello world!"

def test_calculate_checksum(): 
    assert calculate_checksum(b'\x01\x02') == 513 # 1*256 + 2 = 513

def test_detect_oversample():
    signal = bitarray("101")
    assert oversample(signal, 3) == bitarray("111000111")

def test_oversample_incorrect_factor():
    signal = bitarray("101")
    assert oversample(signal, 0) == bitarray("") # Oversampling factor of 0 should return an empty bitarray

