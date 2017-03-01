import argparse

import openbot
from openbot import core

parser = argparse.ArgumentParser(description=openbot.DESCRIPTION)
parser.add_argument('-c', '--config', nargs=1, default='config/openbot.json',
                    help='location of config file')
parser.add_argument('-l', '--locale', nargs=1, default='en_us',
                    help='language')
parser.add_argument('-p', '--perms', nargs=1, default='config/permissions.json',
                    help='location of permissions file')
parser.add_argument('--testing', default=False, action='store_true',
                    help='disables server connection')
core_args = parser.parse_args()

core.startup(core_args.config, core_args.perms, core_args.locale)

"""
TODO: Figure out why this doesn't work...
for i in range(0, 5):
  logger.log(5 - i, parent='core.info.settle', send_newline=False)
  time.sleep(1000)
logger.newline()
"""

if not core_args.testing:
  core.run()