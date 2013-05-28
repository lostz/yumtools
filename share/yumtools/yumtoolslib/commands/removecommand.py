# -*- coding: utf-8 -*-

import os
import re
import md5
from optparse import OptionParser
from validate import validate
from yumtoolslib.commands.commandbase import CommandBase
from yumtoolslib import io
from yumtoolslib import utils
from yumtoolslib import net
from yumtoolslib import error
from yumtoolslib.config import ClientConfig
from yumtoolslib.client import YumtoolsClient

USAGE_MSG = """
yumtools {remove | rm} [options] package_name branch
"""

class RemoveCommand(CommandBase):

    def getOptionParser(self):
        result = OptionParser(USAGE_MSG)
        return result

    def _checkArgs(self, args):
        if len(args) != 2:
            io.error('remove', 'arguments count is not correct.')
            return False
        else:
            return True

    def _checkRpmInfo(self, package_name):
        package_info    = utils.getPackageInfoByName(package_name) 
        if package_info is None:
            io.error('remove', utils.PACKAGE_NAME_FORMAT)
            return False
        else:
            return True

    def _checkBranch(self, branch):
        try:
            validate.is_string(branch)
            return True
        except Exception:
            io.error('remove', 'branch is not valid')
            return False

    def _getRemovePdu(self, package_info, branch):
        pdu = net.RemovePdu()
        pdu.set('package_name', package_info['package_name'])
        pdu.set('version', package_info['version'])
        pdu.set('release', int(package_info['release']))
        pdu.set('os_version', int(package_info['os_version']))
        pdu.set('arch', package_info['arch'])
        pdu.set('branch', branch)
        return pdu

    def run(self, options, args):
        if not self._checkArgs(args):
            return error.ERROR_INVALID_PARAM_COUNT

        io.debug("remove", "checking arguments...")

        package_name    = args[0]
        branch          = args[1]
        if not self._checkRpmInfo(package_name):
            return error.ERROR_NO_SUCH_PACKAGE_NAME 
        if not self._checkBranch(branch):
            return error.ERROR_INVALID_BRANCH

        is_login_succeed, client    =   self.login(options)
        if not is_login_succeed:
            return error.ERROR_AUTH_FAILED

        package_info    = utils.getPackageInfoByName(package_name)
        pdu             = self._getRemovePdu(package_info, branch)
        if not client.invokeRemote(pdu):
            return error.ERROR_PDU_ERROR

        return error.ERROR_SUCCEED


