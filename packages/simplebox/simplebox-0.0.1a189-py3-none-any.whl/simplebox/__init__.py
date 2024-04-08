#!/usr/bin/env python
# -*- coding:utf-8 -*-
__version__ = "0.0.1.alpha189"

banner = f"""
 .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------. 
| .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |
| |    _______   | || |     _____    | || | ____    ____ | || |   ______     | || |   _____      | || |  _________   | || |   ______     | || |     ____     | || |  ____  ____  | |
| |   /  ___  |  | || |    |_   _|   | || ||_   \  /   _|| || |  |_   __ \   | || |  |_   _|     | || | |_   ___  |  | || |  |_   _ \    | || |   .'    `.   | || | |_  _||_  _| | |
| |  |  (__ \_|  | || |      | |     | || |  |   \/   |  | || |    | |__) |  | || |    | |       | || |   | |_  \_|  | || |    | |_) |   | || |  /  .--.  \  | || |   \ \  / /   | |
| |   '.___`-.   | || |      | |     | || |  | |\  /| |  | || |    |  ___/   | || |    | |   _   | || |   |  _|  _   | || |    |  __'.   | || |  | |    | |  | || |    > `' <    | |
| |  |`\____) |  | || |     _| |_    | || | _| |_\/_| |_ | || |   _| |_      | || |   _| |__/ |  | || |  _| |___/ |  | || |   _| |__) |  | || |  \  `--'  /  | || |  _/ /'`\ \_  | |
| |  |_______.'  | || |    |_____|   | || ||_____||_____|| || |  |_____|     | || |  |________|  | || | |_________|  | || |  |_______/   | || |   `.____.'   | || | |____||____| | |
| |              | || |              | || |              | || |              | || |              | || |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------' 

Version::   {__version__}\n
"""

import sys
import os

from ._internal import _argparser
from ._internal._argparser import _options_hook_func


def __print_help():
    msg = """
simplebox cli:
    set simplebox inbuilt configure.
    the option is to add the configuration of the setting parameter, the value is the configuration parameter, 
    the properties.json and values of each configuration, passed in in the form of key:value.
    If the key contains an underscore, you can also use a hyphen in the command, ex k-ey:value = k_ey:value
    multiple values use semicolons ';'Spaced.
    command:
        ex: python xxx.py --options=key1=value2;key2=value2
        --sb-help  show simplebox cli help information, then exit.so do not use with other commands.
        
        --sb-log   LogConfig set by cli, 
                   ex: python xxx.py --sb-log=name:xxx_name;level:INFO
                   See the LogConfig property for details
        --sb-rest  RestConfig set by cli, 
                   ex: python xxx.py --sb-rest=only_body:True
                   See the RestConfig property for details
        --sb-property   PropertyConfig set by cli,
                        ex: python xxx.py --sb-property=resources:xxx
                        See the PropertyConfig property for details
    environment variable:
        export SBLOG="name:xxx_name;level:INFO"
        export SBREST="only_body:True"
        export SBPROPERTY="resources:xxx"
    
    Arguments are obtained from the command line first, and environment variables are not obtained.
    """
    print(msg)
    exit(0)


def __args_handler():
    def executor(option, prefix, params):
        getattr(_argparser, option)(params.split(prefix))
        if params in sys.argv:
            sys.argv.remove(params)

    args = sys.argv[1:]
    env_args = []
    done_args = []
    if "--sb-help" in args:
        __print_help()

    # get args form env
    for opt in _options_hook_func:
        env_key = opt.replace("_", "").upper()
        env_value = os.environ.get(env_key, "")
        option_key = f'{opt.replace("_", "-")}='
        if env_value:
            env_args.append(f"{option_key}{env_value}")

    for opt in _options_hook_func:
        option_key = f'{opt.replace("_", "-")}='
        env_flag = False
        # get args from cli
        for index, arg in enumerate(args[:]):
            if arg.startswith(option_key):
                executor(opt, option_key, arg)
                env_flag = True
                args.pop(index)
                done_args.append(arg)
                break
        # if not args form cli, get from env
        if env_flag:
            for index, arg in enumerate(env_args[:]):
                # if the option is handled in the CLI, it is not being processed here
                if arg.startswith(option_key) and args not in done_args:
                    executor(opt, option_key, arg)
                    env_args.pop(index)
                    break


__all__ = []

__args_handler()
