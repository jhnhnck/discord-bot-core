import sys
import os
import subprocess

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
sys.path.insert(0, os.path.abspath('plugins'))


