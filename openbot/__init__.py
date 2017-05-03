import sys
import subprocess
from shutil import move
from os import path as os_path

class VersionInfo:

  def __init__(self, release_type, major, minor=0, micro=0, serial=0):
    self.release_type = release_type
    self.major = major
    self.minor = minor
    self.micro = micro
    self.serial = serial

  def __str__(self):
    string = '{major}.{minor}.{micro}-{release_type}'.format(**self.__dict__)
    if self.serial > 0:
      string += 'v{}'.format(self.serial)
    return string


# Handles restart calls
class OpenbotRestart(Exception):
  pass


def _latest_git_commit():
  """Try to find latest git commit"""
  try:
    return subprocess.check_output(["git", "describe", "--always"]).decode()[:-1]
  except:
    return 'unknown'


def _block_modules(*blocked):
  """
  Disable some of Discord.py's features from working 
   -> http://stackoverflow.com/a/1350574
  """
  for item in blocked:
    sys.modules[item] = None

  return list(blocked)


def _bootstrap_user():
  import discord.user
  import openbot.user

  if '__dict__' not in discord.user.User.__slots__:
    # import what's need here
    from tempfile import mkstemp
    from os import remove, close

    # Create temp file
    fh, temp_path = mkstemp()
    with open(temp_path, 'w') as new_file:
      with open(discord.user.__file__) as old_file:
        for line in old_file:
          if '__slots__ = ' in line:
            ws = len(line) - len(line.lstrip(' '))
            new_file.write(' ' * ws + '# discord-bot-core patched file\n')
            new_file.write(line.rstrip()[:-1] + ', \'__dict__\']\n')
          else:
            new_file.write(line)
    close(fh)
    # Remove original file
    remove(discord.user.__file__)
    # Move new file
    move(temp_path, discord.user.__file__)

  discord.user.User.__init__ = openbot.user.User.__init__


# Global Definitions
__title__ = 'discord-bot-core'
__author__ = 'jhnhnck'
__license__ = 'GNU GPLv3'
__copyright__ = 'Copyright 2016-2017 jhnhnck'
__commit__ = _latest_git_commit()
__description__ = 'A simple, easily expandable, and well documented framework to add custom commands and \
                   interactions to Discord'

__release_types__ = ['develop', 'alpha', 'beta', 'preview', 'release']
__release_level__ = 0

version_info = VersionInfo(major=0,
                           micro=4,
                           release_type=__release_types__[__release_level__])
__version__ = str(version_info)


"""
Reasons for blocking.
discord.ext: This framework implements more structured and easy to understand 
"""
__blocked__ = _block_modules('discord.ext')


# Add plugin directory to path
sys.path.insert(0, os_path.abspath('plugins'))

try:
  _bootstrap_user()
except Exception as e:
  print('> error. {}'.format(e),
        '> Usually this means you don\'t have permission to write to the discord.py library.',
        '  You have some options to fix this...',
        '   - (easiest) remove discord.py and re-install locally using the following command',
        '     sudo pip uninstall discord.py && pip install --user \'discord.py[voice]\'',
        '   - run discord-bot-core as the root/admin user (this may mess up permissions)',
        '   - manually patch the file yourself by adding \'__dict__\' (with the quotes)',
        '     to the __slots__ list in the discord.py/user.py file.',
        '     where this is at is probably in the error message above', sep='\n')
  exit(-1)
