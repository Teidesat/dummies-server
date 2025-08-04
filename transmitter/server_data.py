from states.empty import EmptyState
from experiment_buffer import ExperimentBuffer

class ServerData:
  def __init__(self):
    self.state = EmptyState(self)
    self.buffer = ExperimentBuffer()

  def change_to_next_experiment(self):
    return self.state.next_experiment()

  def stop_communication(self):
    return self.state.stop_communication()
  
  def return_firmware_state(self):
    return self.state.firmware_state()
  
  def start(self):
    return self.state.start()
  
  def get_status(self):
    return self.buffer.status()