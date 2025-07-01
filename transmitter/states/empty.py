import states.base_state as base_state
import states.sending as sending

class EmptyState(base_state.BaseState):
  def __init__(self, context):
    super().__init__(context)

  def next_experiment(self):
    return ""
  
  def stop_communication(self):
    return ""
  
  def firmware_state(self) -> str:
    return "Idle"
  
  def start(self):
    self.context.state = sending.SendingState(self.context)
    return ""