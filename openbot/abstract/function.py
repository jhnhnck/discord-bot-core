from abc import ABC, abstractmethod

class BotFunction(ABC):

  fnc_help_test = None
  fnc_name = None
  fnc_allowed_args_length = "0"
  fnc_allowed_modifiers = None


  def __init__(self, core):
    self.core = core


  @abstractmethod
  def call(self, args, mod):
    pass
