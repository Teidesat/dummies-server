"""
Utility functions for the receiver server on the Optical Communications Experiment
"""
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