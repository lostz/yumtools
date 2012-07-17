# -*- coding: utf-8 -*-

from commandbase import CommandBase
from optparse import OptionParser
from yumtoolslib.commands import getCommand
from yumtoolslib import io

USAGE_MSG = """
    yumtools [upload|setbranch|remove] [options] [parameters]

Oprations:
    yumtools {upload | up} [options] file
    yumtools {setbranch | sb} [options] package_name package_version release os_version arch to_branch
    yumtools {remove | rm} [options] package_name package_version release os_version arch branch
    yumtools {help | h} command
"""

class HelpCommand(CommandBase):

    def getOptionParser(self):
        result = OptionParser(USAGE_MSG)
        return result

    def run(self, options, args):
        if len(args) != 1:
            io.error('', "Usage: yumtools {help | h} command")
            return 1
        command = getCommand(args[0])
        if command is None:
            io.error('', 'command %s not supported.' % args[0])
            return 2
        command.showHelp()
        return 0


