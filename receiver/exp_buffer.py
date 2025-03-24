"""
Module defining the ExperimentBuffer class
"""

class ExperimentBuffer:
  """
  Class handling the reception of the experiments. Extraction order is FIFO
  """
  def __init__(self):
    # Used to mantain a FIFO ordering
    self.__experiment_ids__ = []
    # Associating ID without message tag with their respective messages in __messages__
    self.__messages__ = {}

  def push(self, experiment_id: str, message: str):
    """
    Inserts new experiment in the buffer
    """
    id_without_message_number = experiment_id[:experiment_id.find("M")]
    if id_without_message_number in self.__messages__: # Updating existing entry
      self.__messages__[id_without_message_number].append((experiment_id, message))
    else: # New entry in the buffer
      self.__experiment_ids__.append(id_without_message_number)
      self.__messages__[id_without_message_number] = [(experiment_id, message)]

  def pop(self) -> tuple[str, list[tuple[str, str]]]:
    """
    Removes one experiment and its related messages from the buffer
    """
    if len(self.__experiment_ids__) == 0:
      raise "Error: Can't pop buffer if it is empty!"
    id = self.__experiment_ids__[0]
    messages = self.__messages__.pop(id)
    self.__experiment_ids__ = self.__experiment_ids__[1:]
    return id, messages
    

  def size(self) -> int:
    """
    Returns the number of elements in the buffer
    """
    return len(self.__experiment_ids__)