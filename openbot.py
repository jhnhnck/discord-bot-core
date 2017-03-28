import argparse
import sys

import openbot
from openbot import core

if sys.version_info < (3, 6):
  print('error > ' + openbot.NAME + ' requires python version 3.6 or greater')
  exit()

parser = argparse.ArgumentParser(description=openbot.DESCRIPTION)
parser.add_argument('-c', '--config', nargs=1, default='config/openbot.yml',
                    help='location of config file')
parser.add_argument('-l', '--locale', nargs=1, default='en_us',
                    help='language')
parser.add_argument('--offline', default=False, action='store_true',
                    help='disables server connection')
core_args = parser.parse_args()

core.startup(core_args.config, core_args.locale)

"""
TODO: Figure out why this doesn't work...
for i in range(0, 5):
  logger.log(5 - i, parent='core.info.settle', send_newline=False)
  time.sleep(1000)
logger.newline()
"""

if not core_args.offline:
  core.run()