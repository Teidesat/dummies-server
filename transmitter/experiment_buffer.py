import json
from collections import OrderedDict

class ExperimentBuffer:
  # Treat as a queue
  def __init__(self):
    # Tuple of stripped_experiment_id, settings and dict of messages
    self.experiments = []
    # Index to know which message to retrieve from the current experiment
    self.message_ind = 0
    self.end_of_experiment = False
  
  def next_experiment(self):
    """
    Change to the next experiment in the queue
    """
    if (len(self.experiments) != 0):
      self.experiments.pop(0)
      self.message_ind = 0
    self.end_of_experiment = False

  def empty(self):
    """
    Clear the buffer
    """
    self.experiments = []
    self.message_ind = 0
    self.end_of_experiment = False


  def insert(self, data):
    message = "TEIDESAT" + data["message"] + "TASEDIET"
    settings = data["settings"]
    experiment_id = data["experiment_id"]
    stripped_experiment_id = experiment_id[:experiment_id.find("M")]
    forming_experiment = None if len(self.experiments) == 0 else self.experiments[-1]
    if not forming_experiment or experiment_id in forming_experiment[2] or forming_experiment[0] != stripped_experiment_id:
      # New experiment
      self.experiments.append((stripped_experiment_id, settings, {}))
      forming_experiment = self.experiments[-1]
    # Add message
    forming_experiment[2][experiment_id] = message

  def get_message(self):
    if len(self.experiments) == 0:
      return None
    messages = list(self.experiments[0][2].items())
    print(self.message_ind)
    print(self.experiments) 
    message = messages[self.message_ind][1]
    self.message_ind += 1
    if self.message_ind >= len(messages):
      self.end_of_experiment = True
    print(message)
    return message

  def get_frequency(self):
    if len(self.experiments) == 0:
      return None
    return self.experiments[0][1]["blinking_frequency"]

  def status(self):
    """
    Returns current status in JSON format
    """
    if len(self.experiments) == 0:
      data = {
      "experiment_id": "",
      "experiments": 0,
      "messages": 0
      }
    else : 
      data = {
        "experiment_id": self.experiments[0][0],
        "experiments": len(self.experiments),
        "messages": len(self.experiments[0][2]) - self.message_ind
      }
    return json.dumps(data)