import json
import os
import re
import sys
from enum import Enum

import openbot.core

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


def log(message,
        parent='core.info.plaintext',
        log_type=None,
        error_point=None,
        send_to_chat=True,
        pad_newlines=True,
        send_newline=True,
        delete_after=None):
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
    send_newline: Append '/n' to the end of message
    delete_after: Duration to delete send_to_chat messages after in seconds
  """
  log_type = _type_from_parent(parent, log_type)

  # Adds spaces so that wrapped lines line up
  if pad_newlines:
    message = _pad_message(str(message), log_type)

  try:
    # Gets the locale string from the json file
    parent_string = get_locale_string(parent)\
        .format(message=message, error_point=error_point)

    # Handles sending to discord and prepending the chat message
    if send_to_chat:
      if openbot.core.server is not None and openbot.core.server:
        # Gets formatting of that particular chat message type
        chat_base_string = get_locale_string('base.chat.{}_base'.format(log_type.name))
        chat_message = chat_base_string.format(message=parent_string)

        if type(delete_after) is int:
          openbot.core.server.print_message(chat_message, delete_after=delete_after)
        else:
          openbot.core.server.print_message(chat_message)

        # Modify message to include chat descriptor
        parent_string = get_locale_string('base.cli.chat_message').format(cli_base=parent_string)
      else:
        # Sends warning if message was sent to chat before client was connected
        log(parent,
            parent='core.warn.chat_message_no_init',
            send_to_chat=False)

    # Gets formatting of that particular terminal message type
    cli_base_string = get_locale_string('base.cli.{}_base'.format(log_type.name))
    cli_message = cli_base_string.format(message=parent_string, **locale['colors'], **locale['format'])

    if send_newline: cli_message += '\n'
    _print(cli_message)

  except ParentNotFoundException:
    log(get_locale_string('core.segments.with_level').format(message, log_type),
        parent='core.error.locale_missing',
        log_type=LogLevel.error,
        error_point=parent,
        send_to_chat=send_to_chat)
  except ParentScopeException:
    log(get_locale_string('core.segments.with_level').format(message, log_type),
        parent='core.error.locale_early_termination',
        log_type=LogLevel.error,
        error_point=parent,
        send_to_chat=send_to_chat)
  except IndexError:
    # TODO: Error?
    _print('Does this error actually occur? Sorry -jhnhnck\n')


def self_test(send_to_chat=False):
  """
  Self Test.
  Prints a all the LogLevels with a test message
  """
  log("This is a test blank message; Don't use this",
      log_type=LogLevel.blank,
      send_to_chat=send_to_chat)
  log('This is a test trace message',
      log_type=LogLevel.trace,
      send_to_chat=send_to_chat)
  log('This is a test debug message',
      log_type=LogLevel.debug,
      send_to_chat=send_to_chat)
  log('This is a test info message',
      log_type=LogLevel.info,
      send_to_chat=send_to_chat)
  log('This is a test warning message',
      log_type=LogLevel.warn,
      send_to_chat=send_to_chat)
  log('This is a test error message',
      log_type=LogLevel.error,
      send_to_chat=send_to_chat)
  log('This is a test fatal message',
      log_type=LogLevel.fatal,
      send_to_chat=send_to_chat)
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
  _print('\n')


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
    with open('locale/{}.json'.format(locale_name), 'r') as file:
      return json.loads(file.read())
  except FileNotFoundError:
    if locale_name != 'en_us':
      _print('\u001B[92mError loading locale "{}", trying "en_us"\u001B[0m\n'.
             format(locale_name))
      return _load_locale('en_us')
    else:
      _print('\u001B[92mError loading locale "{}", exiting\u001B[0m\n'.format(
          locale_name))
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
  Add spacing to multi-line messages so that it aligns to the base length and terminal width

  Args:
    message: String to fill {message} section of parent string
    log_type: LogLevel for base length

  Returns:
    Space padded message
  """
  try:
    # Sometimes this isn't a thing (Actually maybe)
    _, columns = os.popen('stty size', 'r').read().split()
  except ValueError:
    columns = 80
    log(columns, parent='core.debug.col_value_error')

  split = message.splitlines(keepends=True)
  split_length = int(columns) - log_base_lengths[log_type.name]
  lines = []

  for line in range(len(split)):
    if len(split[line]) > split_length:
      # Splits each line on length
      lines.append((split[line][0 + i:split_length + i] for i in range(0, len(split[line]), split_length)))
    else:
      lines.append(split[line])

  pad_part = ' ' * log_base_lengths[log_type.name]
  # Don't space first line
  pad_message = lines[0]

  for i in range(1, len(lines)):
    pad_message += pad_part + lines[i]

  return pad_message


def _print(message):
  """
  Print.
  Prints the message to the command line output in a thread safe manner

  Args:
    message: String to be printed
  """
  sys.stdout.write(message)