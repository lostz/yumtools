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
    yumtools {setbranch | sb} [options] package_name from_branch to_branch
"""


class SetbranchCommand(CommandBase):

    def getOptionParser(self):
        result = OptionParser(USAGE_MSG)
        return result

    def _checkArgs(slef, args):
        if len(args) != 3:
            io.error('setbranch', 'arguments count is not correct')
            return False
        else:
            return True

    def _checkRpmInfo(self, package_name):
        package_info    = utils.getPackageInfoByName(package_name) 
        if package_info is None:
            io.error('setbranch', utils.PACKAGE_NAME_FORMAT)
            return False
        else:
            return True

    def _checkBranch(self, from_branch, to_branch):
        try:
            validate.is_string(from_branch)
            validate.is_string(to_branch)
            return True
        except Exception:
            io.error('setbranch', 'branch is not valid')
            return False

    def _getSetBranchPdu(self, package_info, from_branch, to_branch):
        pdu = net.SetBranchPdu()
        pdu.set('package_name', package_info['package_name'])
        pdu.set('version', package_info['version'])
        pdu.set('release', int(package_info['release']))
        pdu.set('os_version', int(package_info['os_version']))
        pdu.set('arch', package_info['arch'])
        pdu.set('from_branch', from_branch)
        pdu.set('to_branch', to_branch)
        return pdu


    def run(self, options, args):
        if not self._checkArgs(args):
            return error.ERROR_INVALID_PARAM_COUNT

        io.debug("setbranch", "checking arguments...")

        package_name    = args[0]
        from_branch     = args[1]
        to_branch       = args[2]
        if not self._checkRpmInfo(package_name):
            return error.ERROR_NO_SUCH_PACKAGE_NAME
        if not self._checkBranch(from_branch, to_branch):
            return error.ERROR_INVALID_BRANCH

        is_login_succeed, client    =   self.login(options)
        if not is_login_succeed:
            return error.ERROR_AUTH_FAILED

        package_info    = utils.getPackageInfoByName(package_name)
        pdu             = self._getSetBranchPdu(package_info, from_branch, to_branch)
        if not client.invokeRemote(pdu):
            return error.ERROR_PDU_ERROR

        return error.ERROR_SUCCEED

