import states.base_state as base_state
import states.empty as empty
import states.changing as changing

class SendingState(base_state.BaseState):
  def __init__(self, context):
    super().__init__(context)

  def next_experiment(self):
    self.context.buffer.next_experiment()
    self.context.state = changing.ChangingState(self.context)
    return ""

  def stop_communication(self):
    self.context.buffer.empty()
    self.context.state = empty.EmptyState(self.context)
    return ""

  def firmware_state(self):
    return "Sending"
  
  def start(self):
    return ""