from package import Package
import re
import random

class PackageSequence:
  def __init__(self):
    self.packages = [Package()]
  
  def add_noise(self, num_of_bytes: int):
    noise_bytes = b"0" * num_of_bytes
    self.add_bytes(noise_bytes, "N")

  def add_message(self, bytes_to_add: bytes):
    self.add_bytes(bytes_to_add, "M")

  def add_bytes(self, bytes_to_add: bytes, tag: str):
    while len(bytes_to_add) != 0:
      bytes_to_add = self.packages[-1].add_bytes(bytes_to_add, tag)
      if self.packages[-1].get_empty_space() == 0:
        self.packages.append(Package())
     
  def send(self):
    for package in self.packages:
      package.send()

  def __str__(self):
    return "\n".join(map(str, self.packages))