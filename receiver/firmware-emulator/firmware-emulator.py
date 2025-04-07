"""
Program to emulate the messages sent from the receiver's firmware.
"""
import sys
import os
from package_sequence import PackageSequence

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
      sequence.send()
    elif option == "5":
      show_help_message()

def add_message(sequence: PackageSequence):
  path = input("Write the path to the message to add: ")
  if not os.path.isfile(path):
    print(f"There was an error finding {path}")
    return
  with open(path, "rb") as fp:
    message = fp.read()
  message_with_header_tail = b"TEIDESAT" + message + b"TASEDIET" 
  print(f"The message's size is {len(message)} bytes, {len(message_with_header_tail)} bytes with header/tail")
  sequence.add_message(message_with_header_tail)

def add_noise(sequence: PackageSequence):
  num_bytes = input("Write how many noise bytes are you adding: ")
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
  print("2) Add noise")
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