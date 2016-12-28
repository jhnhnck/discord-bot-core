# Discord Bot Plugin Base Abstraction Layer Outline and Planning #
Purpose: Create a simple, easily expandable, and well documented framework to add custom commands and interactions to Discord

## Base ##

  - ## `openbot.core` ##
    + Class BotCore
      - load plugin packages
      - handle tasks
      - handle connections to discord
    + Class FunctionManager
      - Checks chat for command
    + Class BotSetup
      - First time setup guide

  - ### `openbot.chat` ###
    + Class BotChatOutput
      - Send messages
    + Class BotChatInput
      - Receive messages (in theory this shouldn't be used except internally)
    + Class BotStatus
      - Handles the "Playing ..." message gracefully (like on radio stations)
      - Define pages that scroll overflow text and switch between displays on a timer

  - ### `openbot.voice` ###
    + Class BotVoiceOutput
      - Send audio (this may be too complex to abstract)
    + Class BotVoiceInput
      - Recieve and interpret audio
      - Voice commands (God help you; I'm not doing it)

  - ### `openbot.permissions` ###
    + Class BotPerms
      - Defines some basic permissions that are applicable to all bot plugins

  - ### `openbot.config` ###
    + Class ConfigStream
      - Load config from file config/openbot.json

## Plugin Framework ##

  - ### `openbot.abstract.plugin` ###
    + Class BotPlugin
      - abstract class that all plugins must inherit from in order to be loaded
      - defines the functions, tasks, and config settings that are to be expected
      - shouldn't handle functionality of plugin; only configurations

  - ### `openbot.abstract.function` ###
    + Class BotFunction
      - abstract class that each function must inherit from

  - ### `openbot.abstract.task` ###
    + Class BotTask
      - abstract class that each task must inherit from

## Core Functions ##

  - ### `openbot.coreftns.clean` ###
    + Class FunctionClean
      - Default Function that removes bot conversations

  - ### `openbot.coreftns.restart` ###
    + Class FunctionRestart
      - Default Function that restarts the bot and reloads configs

  - ### `openbot.coreftns.shutdown` ###
    + Class FunctionShutdown
      - Default Function that stops the bot from running

  - ### `openbot.coreftns.help` ###
    + Class FunctionHelp
      - Default Function that prints a help message

  - ### `openbot.coreftns.config` ###
    + Class FunctionConfig
      - Default Function that sets name, nickname, avatar, and other settings
