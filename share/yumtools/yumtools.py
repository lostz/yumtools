# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '/usr/share/yumtools')
import yumtoolslib
import yumtoolslib.commands
import yumtoolslib.commands.helpcommand
from yumtoolslib import config
from yumtoolslib import io
from yumtoolslib import error


YUMTOOLS_CONF_FILE              =   '/etc/yumtools.conf'

def showUsage():
    command = yumtoolslib.commands.helpcommand.HelpCommand()
    command.showHelp()


def loadClientConfig():
    if config.ClientConfig().load(YUMTOOLS_CONF_FILE):
        io.use_debug = config.ClientConfig().verbose
        return True
    else:
        return False


def checkArgs():
    if len(sys.argv) <= 1:
        return False
    else:
        return True


def getArgs():
    return sys.argv[1], sys.argv[2:]


def getCommandInstance(command_name):
    return yumtoolslib.commands.getCommand(command_name)


def execCommand(command, args):
    exit_code = error.EXIT_SUCCEED
    try:
        exit_code = command.execute(args)
    except KeyboardInterrupt, _ex:
        io.error("", "yumtools has been terminated.")
        exit_code = error.EXIT_INTERRUPTED
    return exit_code


def main():
    if not loadClientConfig():
        return error.EXIT_LOAD_CONFIG_FAILED;

    if not checkArgs():
        showUsage()
        return error.EXIT_INVALID_PARAMETER;

    command_name, command_args = getArgs()

    command = getCommandInstance(command_name)
    if command is None:
        showUsage()
        return error.EXIT_COMMAND_NOT_FOUND

    return execCommand(command, command_args)


if __name__ == '__main__':
    main()


