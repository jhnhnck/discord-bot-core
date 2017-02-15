# Global Definitions
RELEASE_TYPES = ['develop', 'alpha', 'beta', 'preview', 'release']
RELEASE_TYPE = 0
RELEASE_TYPE_NAME = RELEASE_TYPES[RELEASE_TYPE]

VERSION = '0.0.1'
FULL_VERSION = '{}-{}'.format(VERSION, RELEASE_TYPE_NAME)

DESCRIPTION = 'A simple, easily expandable, and well documented framework to add custom commands and \
               interactions to Discord'
