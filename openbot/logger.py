import sys
import json

from enum import Enum


class ParentNotFoundException(Exception):
  pass


class ParentScopeException(Exception):
  pass


class LogLevel(Enum):
  trace = -2
  debug = -1
  info = 0
  warn = 1
  error = 2
  fatal = 5


class Logger:
  def __init__(self, core, locale):
    self.locale = self._load_locale(locale)
    self.core = core


  def _load_locale(self, locale):
    try:
      with open('../locale/{}.json'.format(locale), "r") as file:
        return json.loads(file.read())
    except FileNotFoundError:
      if locale != 'en_us':
        self._print('\u001B[92mError loading locale "{}", trying "en_us"\u001B[0m'.format(locale))
        return self._load_locale('en_us')
      else:
        self._print('\u001B[92mError loading locale "{}", exiting\u001B[0m'.format(locale))
        exit(66)


  def log(self, message, parent='core.info.plaintext', type=LogLevel.info, error_point=None):
    parent_string = self._get_locale_string(parent)\
      .format(message=message, error_point=error_point)
    base_string = self._get_locale_string("base.{}_base".format(type.name))\
      .format(message=parent_string, **self.locale['colors'], **self.locale['format'])

    self._print(base_string)


  @staticmethod
  def _print(message):
    sys.stdout.write(message + '\n')


  def _get_locale_string(self, parent):
    store = self.locale

    try:
      for branch in parent.split('.'):
        store = store[branch]
      if not isinstance(store, str):
        raise ParentScopeException
    except IndexError:
      raise ParentNotFoundException

    return store
