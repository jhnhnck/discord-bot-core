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


locale = None


def setup(locale_name):
  global locale
  locale = _load_locale(locale_name)


def _load_locale(locale_name):
  try:
    with open('locale/{}.json'.format(locale_name), "r") as file:
      return json.loads(file.read())
  except FileNotFoundError:
    if locale_name != 'en_us':
      _print('\u001B[92mError loading locale "{}", trying "en_us"\u001B[0m'.format(locale_name))
      return _load_locale('en_us')
    else:
      _print('\u001B[92mError loading locale "{}", exiting\u001B[0m'.format(locale_name))
      exit(66)


def log(message, parent='core.info.plaintext', type=LogLevel.info, error_point=None, send_to_chat=True):
  try:
    parent_string = get_locale_string(parent)\
      .format(message=message, error_point=error_point)
    cli_base_string = get_locale_string("base.cli.{}_base".format(type.name))\
      .format(message=parent_string, **locale['colors'], **locale['format'])
    # TODO: Fix something here

    _print(cli_base_string)

    if send_to_chat:
      chat_base_string = get_locale_string("base.chat.{}_base".format(type.name))\
        .format(message=parent_string)
      # TODO: Handle chat messages
      pass

  except ParentNotFoundException:
    # TODO: Fix this, don't to this ever -jhnhnck
    log("\"{}\" with level \"{}\"".format(message, type.name),
        parent="core.error.locale_missing",
        type=LogLevel.error,
        error_point=parent,
        send_to_chat=send_to_chat)
  except ParentScopeException:
    # TODO: Fix this, don't to this ever -jhnhnck
    log("\"{}\" with level \"{}\"".format(message, type.name),
        parent="core.error.locale_early_termination",
        type=LogLevel.error,
        error_point=parent,
        send_to_chat=send_to_chat)
  except IndexError:
    log("Error")


def _print(message):
  sys.stdout.write(message + '\n')


def get_locale_string(parent):
  if locale is None:
    setup('en_us')

  store = locale

  try:
    for branch in parent.split('.'):
      store = store[branch]
    if not isinstance(store, str):
      raise ParentScopeException
  except KeyError:
    raise ParentNotFoundException

  return store


def self_test():
  log("This is a test trace message", type=LogLevel.trace, send_to_chat=True)
  log("This is a test debug message", type=LogLevel.debug, send_to_chat=True)
  log("This is a test info message", type=LogLevel.info, send_to_chat=True)
  log("This is a test warning message", type=LogLevel.warn, send_to_chat=True)
  log("This is a test error message", type=LogLevel.error, send_to_chat=True)
  log("This is a test fatal message", type=LogLevel.fatal, send_to_chat=True)
  _print('')
