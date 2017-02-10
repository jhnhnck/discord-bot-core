import json
import re
import sys
from enum import Enum


class ParentNotFoundException(Exception):
  pass


class ParentScopeException(Exception):
  pass


class LogLevel(Enum):
  blank = -3
  trace = -2
  debug = -1
  info = 1
  warn = 2
  error = 3
  fatal = 5


locale = None
# ['blank', 'trace', 'debug', 'info', 'warn', 'error', 'fatal']
log_base_lengths = None


def setup(locale_name):
  """
  Setup.
  Loads the correct info for the logger; This is handled by the core and not needed for plugins and other classes that
  use the logger after core has finished the startup

  Args:
    locale_name: Name of locale
  """
  global locale
  locale = _load_locale(locale_name)

  global log_base_lengths
  log_base_lengths = _count_base_lengths()


def log(message, parent='core.info.plaintext', log_type=None, error_point=None, send_to_chat=True, pad_newlines=True):
  """
  Logger.
  Prints a log message to the command-line output and to the server chat

  Args:
    message: String to fill {message} section of parent string
    parent: Parent Locale Identifier
    log_type: Alert level of message of type enum LogLevel (openbot.logger.LogLevel)
    error_point: String to fill {error_point} section of parent string
    send_to_chat: False if the message should only print to command line output
    pad_newlines: Add spacing to multi-line messages so that it aligns to the base length
  """
  log_type = _type_from_parent(parent, log_type)

  if pad_newlines:
    message = _pad_message(message, log_type)

  try:
    parent_string = get_locale_string(parent) \
        .format(message=message, error_point=error_point)
    cli_base_string = get_locale_string("base.cli.{}_base".format(log_type.name)) \
        .format(message=parent_string, **locale['colors'], **locale['format'])
    # TODO: Fix something here

    _print(cli_base_string)

    if send_to_chat:
      chat_base_string = get_locale_string("base.chat.{}_base".format(log_type.name)) \
          .format(message=parent_string)
      # TODO: Handle chat messages
      pass

  except ParentNotFoundException:
    log(get_locale_string('core.segments.with_level').format(message, log_type),
        parent="core.error.locale_missing",
        log_type=LogLevel.error,
        error_point=parent,
        send_to_chat=send_to_chat)
  except ParentScopeException:
    log(get_locale_string('core.segments.with_level').format(message, log_type),
        parent="core.error.locale_early_termination",
        log_type=LogLevel.error,
        error_point=parent,
        send_to_chat=send_to_chat)
  except IndexError:
    log("Error")


def self_test():
  """
  Self Test.
  Prints a all the LogLevels with a test message
  """
  log("This is a test blank message; Don't use this", log_type=LogLevel.blank, send_to_chat=True)
  log("This is a test trace message", log_type=LogLevel.trace, send_to_chat=True)
  log("This is a test debug message", log_type=LogLevel.debug, send_to_chat=True)
  log("This is a test info message", log_type=LogLevel.info, send_to_chat=True)
  log("This is a test warning message", log_type=LogLevel.warn, send_to_chat=True)
  log("This is a test error message", log_type=LogLevel.error, send_to_chat=True)
  log("This is a test fatal message", log_type=LogLevel.fatal, send_to_chat=True)
  newline()


def get_locale_string(parent):
  """
  Get Locale String.
  Gets the value of the parent locale identifier

  Args:
    parent: Parent locale identifier

  Returns:
    Value of parent string
  """
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


def newline():
  """
  Newline.
  Outputs a new line to the command line output
  """
  _print('')


def _load_locale(locale_name):
  """
  Locale Loading.
  Loads the locale from the locale directory within the current directory and within the locale directory for each
  enabled plugin

  Args:
    locale_name: Name of the Locale

  Returns:
    Dictionary of all locale parent strings
  """
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


def _type_from_parent(parent, log_type):
  """
  LogLevel from Parent String.

  Args:
    parent: Parent locale identifier
    log_type: Provided LogLevel or None

  Returns:
    If LogLevel is a valid LogLevel (i.e. not None) then it is returned;
    Otherwise, determine the LogLevel from a matching segment of the parent and LogLevel name;
    Else, return an info LogLevel
  """
  if isinstance(log_type, LogLevel):
    return log_type

  elif log_type is None:
    split = parent.split('.')
    if split[1] in log_base_lengths:
      return LogLevel[split[1]]
    else:
      for part in split[2:]:
        if part in log_base_lengths:
          return LogLevel[part]

  else:
    return LogLevel.info


def _count_base_lengths():
  """
  Count Base Lengths.
  Counts the length of the base strings without formatting for command line output for use with new line wrapping

  Returns:
    Dictionary with matched base and length key pairs

  """
  lengths = {}

  for base, value in locale.get('base').get('cli').items():
    lengths[base.replace('_base', '')] = len(re.sub('{.*?}', '', value))

  return lengths


def _pad_message(message, log_type):
  """
  Pad Message.
  Add spacing to multi-line messages so that it aligns to the base length

  Args:
    message: String to fill {message} section of parent string
    log_type: LogLevel for base length

  Returns:
    Space padded message
  """
  # TODO: Handle console length overlap (http://stackoverflow.com/a/943921)
  split = message.splitlines(keepends=True)
  pad_part = ' ' * log_base_lengths[log_type.name]
  pad_message = split[0]

  for i in range(1, len(split)):
    pad_message = pad_message + pad_part + split[i]

  return pad_message


def _print(message):
  """
  Print.
  Prints the message to the command line output in a thread safe manner

  Args:
    message: String to be printed
  """
  sys.stdout.write(message + '\n')
