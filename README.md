# discord-bot-core
WIP: simple, easily expandable, and well documented framework to add custom commands and interactions to Discord

### Objectives ###
  -	Use and/or modify multiple third party APIs
  -	Multi-threaded
  - Well documented code
  -	Layers of abstraction:
    - Expandable without having or needing an in-depth knowledge of internal structure
    - Beginner should be able to create their own plugins without having to deal with advanced topics such as thread-safety, api-keys, and HTTP requests
  - Expandable and modular code
  - Emphasis on code styling (Probably not PEP8 but at least consistent)
  - Object-oriented programming
  - Use of abstract base classes
  - Well formatted and consistent text output (All plugins should feel like they fit together)
  - Use of python dictionaries, custom objects, and custom error types
  - Make use of a version control system ([git](https://en.wikipedia.org/wiki/Git))

### Basic Features ###
  - Simple and expandable document-driven plugin format
  -	Augment program via the use of configuration files
  -	Provide the basis to provide basic language translation
  - Basic permissions system
    - Allow or deny certain commands per user or role
    - Allow or deny certain tasks (i.e. User not allowed to perform tasks that involve audio)
  - Handle conflict errors that would occur with many plugins
    - Same function names
    - Same plugin names
    - Plugins with same or similar features

### Core Functions ###
  -	**Clean**: Remove any commands that have been sent previously
  -	**Shutdown**: Completely stops the program
  - **Restart**: Completely stops the program and [flushes](https://blog.petrzemek.net/2014/03/23/restarting-a-python-script-within-itself/) all files before starting again
  - **Reload**: Reloads config and plugins from file; Faster but will not notice changes with code
  - **Update**: Looks for changes to plugins and core from GitHub url in plugin json file
  - **Help**: provide a list of commands and detailed info if a specific command is provided
  - **Config**: Change certain values in the config file
  - **Sleep**: Ignore commands for a certain amount of time
  - **Stats**: Print useful information such as up-time and loaded plugins


### Additional Core Functions ###
  *Only loaded if audio plugins are loaded*
  - **Summon**: Join the bot to the command executor's channel
  - **Dismiss**: Disconnect the bot from all audio channels
  - **Mute**: Stops the transmission of audio but does not alert plugins
  - **Volume**: Sets the volume of the transmission on scale of 0%-200% where 100% is equal to average talking volume

### Development Setup ###
Run the following command to setup the plugins directory:
```git
cd plugins
git clone -b develop git@github.com:jhnhnck/discord-bot-coreftns.git jhnhnck_coreftns

# Optional
git clone -b develop git@github.com:stphnduvall/discord-musicbot.git stphn_musicbot
```
