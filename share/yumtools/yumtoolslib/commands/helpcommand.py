# -*- coding: utf-8 -*-

from commandbase import CommandBase
from optparse import OptionParser
from yumtoolslib.commands import getCommand
from yumtoolslib import io
from yumtoolslib import error

USAGE_MSG = """
    yumtools [upload|setbranch|remove] [options] [parameters]

Branchs:
    test beta prod
    test stable [OPS ONLY]

Oprations:
    yumtools {upload | up} [options] file
    yumtools {setbranch | sb} [options] package_name from_branch to_branch
    yumtools {remove | rm} [options] package_name branch
		example:
			yumtools upload nagios-plugins-openmanage-3.7.6-1.el6.x86_64.rpm 
			yumtools setbranch nagios-plugins-openmanage-3.7.6-1.el6.x86_64.rpm test stable
			yumtools remove nagios-plugins-openmanage-3.7.6-1.el6.x86_64.rpm stable
    yumtools {help | h} command

More infomation:
    http://wiki.corp.qunar.com/display/opswiki/YumServer

"""

class HelpCommand(CommandBase):

    def getOptionParser(self):
        result = OptionParser(USAGE_MSG)
        return result

    def run(self, options, args):
        if not self._checkArgs(args):
            return error.ERROR_COMMAND_PARM_INVALID
        command = getCommand(args[0])
        if command is None:
            io.error('', 'command %s not supported.' % args[0])
            return error.ERROR_UNSUPPORT_COMMAND
        command.showHelp()
        return error.ERROR_SUCCEED

    def _checkArgs(slef, args):
        if len(args) != 1:
            io.error('', "Usage: yumtools {help | h} command")
            return False
        else:
            return True

