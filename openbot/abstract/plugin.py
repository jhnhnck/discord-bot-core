from abc import ABC, abstractmethod


class BotPlugin(ABC):

  def __init__(self, core):
    self.core = core


  def _compare_versions(self):
    pass
