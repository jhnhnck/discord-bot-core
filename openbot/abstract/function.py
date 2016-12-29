from abc import ABC, abstractmethod

class BotFunction(ABC):

  @abstractmethod
  def __init__(self):
    pass

  @abstractmethod
  def call(self, core, args):
    pass