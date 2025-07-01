import states.base_state as base_state
import states.empty as empty
import states.sending as sending

class ChangingState(base_state.BaseState):
  def __init__(self, context):
    super().__init__(context)

  def next_experiment(self):
    self.context.buffer.next_experiment()
    return ""
  
  def stop_communication(self):
    self.context.buffer.empty()
    self.context.state = empty.EmptyState(self.context)
    return ""

  def firmware_state(self):
    self.context.state = sending.SendingState(self.context)
    return "Idle" # Make the firmware stop sending the current experiment
  
  def start(self):
    return ""