"""
Program to emulate the messages sent from the receiver's firmware.
"""
import sys
import os
from package_sequence import PackageSequence
import random
from bitarray import bitarray

def main():
  sequence = PackageSequence()
  option = None
  while option != "0":
    show_menu()
    option = input("Select your option: ")
    if option == "1":
      add_message(sequence)
    elif option == "2":
      add_noise(sequence)
    elif option == "3":
      print(sequence)
    elif option == "4":
      print("Sending packages...")
      print(sys.getsizeof(sequence), "packages to send")
      print(sys.getsizeof(sequence.packages), "packages")
      sequence.send()
    elif option == "5":
      show_help_message()
      
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

def add_message(sequence: PackageSequence):
  path = input("Write the path to the message to add: ")
  if not os.path.isfile(path):
    print(f"There was an error finding {path}")
    return
  with open(path, "rb") as fp:
    message = fp.read()
  header = bits_from_bytes(b"TEIDESAT")
  tail = bits_from_bytes(b"TASEDIET")
  message = bits_from_bytes(message)
  message_with_header_tail = oversample(header + message + tail, 5) 
  print(f"The message's size is {len(message)} bytes, {len(message_with_header_tail)} bytes with header/tail")
  print(message_with_header_tail)
  sequence.add_message(message_with_header_tail)

def random_modify(string: bytes) -> bytes:
    """
    Randomly modifies a string by changing up to 5 random characters to random values.
    """
    num_mutations = random.randint(1, 5)  # Random number of mutations between 1 and 5

    if len(string) == 0:
        return string

    # 1-in-3 chance to mutate
    if random.randint(1, 3) % 3 == 0:
        string_array = bytearray(string)  # make mutable
        mutation_indices = random.sample(range(len(string_array)), min(num_mutations, len(string_array)))

        for idx in mutation_indices:
            original_byte = string_array[idx]
            new_byte = random.randint(0, 255)
            while new_byte == original_byte:
                new_byte = random.randint(0, 255)
            string_array[idx] = new_byte

        return bytes(string_array)
    else:
        return string



def add_noise(sequence: PackageSequence):
  num_bytes = input("Write how many padding bytes are you adding: ")
  error = False
  try:
    num_bytes = int(num_bytes)
  except:
    error = True
  if error or num_bytes <= 0:
    print(f"Inserted value {num_bytes} is not a valid number")
    return
  sequence.add_noise(num_bytes)

def show_menu():
  print("0) Exit")
  print("1) Add message")
  print("2) Add padding")
  print("3) Show current packages to send")
  print("4) Send current packages")
  print("5) Help")
  print()

def show_help_message():
  print()
  print(sys.argv[0] + " - Receiver's firmware emulator")
  print("Provides a way to test the receiver's server by sending packets of information in the same format as the firmware")
  print("The messages and noise are stored until the")
  print()

if __name__ == "__main__":
  main()