"""
Defines a class representing the experiments in the optical communications experiment.
"""

class Experiment:
  def __init__(self, id: str):
    self.id = id
    self.messages = {}

  def addMessage(self, message_id: str, message: str):
    self.messages[message_id] = message
  
  def hasMessage(self, message_id: str):
    """
    Checks if the current experiment has the given message.
    """
    return message_id in self.messages
  
  def toDict(self):
    """
    Returns the Experiment as a dictionary.
    """
    formatted_messages = [[id, message] for id, message in self.messages.items()]
    return {
      "id": self.id + "Mm",
      "messages": formatted_messages
    }