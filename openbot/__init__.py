import sys
import os
import subprocess

# Global Definitions
NAME = 'discord-bot-core'
RELEASE_TYPES = ['develop', 'alpha', 'beta', 'preview', 'release']
RELEASE_TYPE = 0
RELEASE_TYPE_NAME = RELEASE_TYPES[RELEASE_TYPE]

VERSION = '0.0.1'
FULL_VERSION = '{}-{}'.format(VERSION, RELEASE_TYPE_NAME)

DESCRIPTION = 'A simple, easily expandable, and well documented framework to add custom commands and \
               interactions to Discord'

# Try to find latest git commit
try:
  GIT_VERSION = subprocess.check_output(["git", "describe", "--always"]).decode('utf-8')[:-1]
except:
  GIT_VERSION = 'unknown'

# Add plugin directory to path
sys.path.insert(0, os.path.abspath('plugins'))
