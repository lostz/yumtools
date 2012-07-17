# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '/usr/share/yumtools')
import yumtoolslib
import yumtoolslib.commands
import yumtoolslib.commands.helpcommand
from yumtoolslib import config
from yumtoolslib import io

def showUsage():
    command = yumtoolslib.commands.helpcommand.HelpCommand()
    command.showHelp()

def main():
    args = sys.argv
    if not config.ClientConfig().load('/etc/yumtools.conf'):
        return False

    io.use_debug = config.ClientConfig().verbose

    command = None

    # check first parameter
    if len(args) <= 1:
        showUsage()
        sys.exit(1)

    first_arg = args[1]
    other_args = args[2:]

    #parse command class
    command = yumtoolslib.commands.getCommand(first_arg)
    if command is None:
        showUsage()
        sys.exit(2)

    # do execute
    exec_code = 0
    try:
        exec_code = command.execute(other_args)
    except KeyboardInterrupt, _ex:
        print
        io.error("", "yumtools has been terminationed.")
        exec_code = -1

    sys.exit(exec_code)

if __name__ == '__main__':
    main()


