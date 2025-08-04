class BaseState:
  def __init__(self, context):
    self.context = context

  def next_experiment(self):
    pass

  def stop_communication(self):
    pass

  def firmware_state(self) -> str:
    pass

  def start(self):
    pass