## Plugin JSON Commented ##

```
    {
      "description": {                          -> SECTION: Appearance of the plugin
        "plugin_name": "coreftns",               -> name of plugin (should match directory name)
        "domain_name": "jhnhnck",                -> developer identifier
        "plugin_prefix": "core",                 -> used in case of function name conflicts
        "plugin_description":                    -> provided to the end user via the help function
          "Core functions included with discord-bot-core"
      },
      "versioning": {                           -> SECTION: Handles compatibility and updating
        "plugin_version": "1.0.0r0",             -> plugin version: defaults to major.minor.patch with optional revision
                                                    for beta versions; if you wish to use a different form, you must
                                                    override the '_compare_versions' function in your 'plugin_name.py'
        "release_type": "stable",                -> valid options are stable, preview, beta, alpha, and internal
        "requires": "[*]",                       -> bot-core compatible versions; available symbols are "[]()<>=!,*"
        "update_check_url": "",                  -> url to json formatted update description (see update.json)
        "beta_update_check_url": "",             -> same as above
      },
      "user": {                                 -> SECTION: User options (leave at default settings)
        "enabled": true,                         -> if enabled, plugin will load
        "auto_update": true,                     -> if enabled, check update url on start
        "beta_testing": false                    -> if enabled, download beta releases if provided
      },
      "config_template": {},                    -> SECTION: Default config that will be copied to master config upon
                                                   first load or update
      "functions": {                            -> SECTION: Each function definition
        "example": {                             -> internal name of function
          "help_text": "provides an example",     -> provided to the end user via the help function
          "function_name": "example",             -> name of function as it will be called
          "allowed_args_length": "0,>7,<9",       -> number of comma-delimited arguments to allow; available symbols are 
                                                     "<>=!,*"; If any evaluate to true then it will be allowed
          "args_description": [                   -> Description of each valid syntax layout
            "",
            "[query]"
          ],
          "allowed_modifiers": {                  -> modifiers that do not count toward arguments; key should contain
            "-a=": "file to use",                    actual modifier (trailing equals allows for '-a=myfile.txt' or
            "--list": "list available files"         '-a myfile.txt') and value should be a brief description
          }
        }
      }
    }
```