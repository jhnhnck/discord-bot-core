import argparse
import sys

import openbot
from openbot import core

if sys.version_info < (3, 6):
  print('error > ' + openbot.__title__ + ' requires python version 3.6 or greater')
  exit()

parser = argparse.ArgumentParser(description=openbot.__description__)
parser.add_argument('-c', '--config', nargs=1, default='config/openbot.yml',
                    help='location of config file')
parser.add_argument('-l', '--locale', nargs=1, default='en_us',
                    help='language')
parser.add_argument('--offline', default=False, action='store_true',
                    help='disables server connection')
core_args = parser.parse_args()

try:
  core.startup(core_args.config, core_args.locale)

  if not core_args.offline:
    core.run()
except openbot.OpenbotRestart:
  import os
  os.execl(sys.executable, sys.executable, *sys.argv)
except KeyboardInterrupt:
  # Try to logout on ^c
  try:
    core.server.execute('logout')
  except:
    sys.exit()