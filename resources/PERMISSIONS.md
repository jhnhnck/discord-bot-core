# Permissions #

## Behavior ##
  - Deny permissions take president over allow permissions of the same priority
  - User defined permissions are always higher priority than that of built-ins
  - Custom groups can be defined and all permissions but all will be considered denied unless specified otherwise
  - Discord permission groups will auto-match same names

## Default Groups ##
  + Owner
    - All permissions
    - Defaults to server owner (can be disabled)
  + Admin
    - All permissions
    - Auto-summon takes priority to owner first
  + Moderator
    - Some permissions (defined by plugins)
    - No access to built-in or coreftns plugins except help
    + Auto escalates permissions if no admin present
      - Two types: Based on online status and based on voice channel presence
  + User
    - Permissions same as moderator but doesn't auto escalate
  + Restricted
    - Commands are completely ignored

## Available Keys ##
  + `grand_to`
    - array of user ids
  + `full_access`
    - True or False 
    - Warning --- This makes all commands acceptable regardless of whitelist/blacklist
  + `command_whitelist` and `command_blacklist`
    - array of commands
    - omit command_prefix
    - this will match any valid command with that name
  + `voice_auto_summon`
    - True or False
    - Warning --- Higher permission groups take priority
  + `permission_whitelist` and `permission_blacklist`
    - array of permissions
    

