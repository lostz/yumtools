# -*- coding: utf-8 -*-

import os
import re
import md5
import clint
from commandbase import CommandBase
from optparse import OptionParser
from yumtoolslib import io
from yumtoolslib import utils
from yumtoolslib import net
from yumtoolslib import error
from yumtoolslib.config import ClientConfig
from yumtoolslib.client import YumtoolsClient

USAGE_MSG = """
    yumtools {upload | up} [options] file
"""


class UploadCommand(CommandBase):

    def getOptionParser(self):
        return OptionParser(USAGE_MSG)

    def run(self, options, args):
        if not self._checkArgs(args):
            return error.ERROR_NO_SUCH_PACKAGE_NAME

        package_name        = args[0]
        io.log('upload', 'checking %s ...' % package_name)
        if not self._checkRpmFileAccess(package_name):
            return error.ERROR_ACCESS_PACKAGE_ERROR
        if not self._checkRpmInfo(package_name):
            return error.ERROR_INVALID_PACKAGE

        is_login_succeed, client    =   self.login(options)
        if not is_login_succeed:
            return error.ERROR_AUTH_FAILED

        io.log('upload', 'start upload %s ...' % package_name)
        package_info        = utils.getPackageInfoByName(package_name)
        pdu                 = self._getUploadPdu(package_info, package_name)

        if not client.invokeRemote(pdu):
            return error.ERROR_PDU_ERROR

        if not self._uploadPackage(client, package_name):
            return error.ERROR_PDU_ERROR

        return True

    def _checkArgs(slef, args):
        if len(args) != 1:
            io.error('upload', 'no such package name.')
            return False
        else:
            return True

    def _checkRpmInfo(self, package_name):
        package_info            = utils.getPackageInfoByName(package_name)
        if package_info is None:
            io.error('upload', 'package name is not a valid format. format: <package_name>-<package_version>-<release>.el<os_version>.<arch>.rpm')
            return False
        package_name_from_file  = utils.getPackageNameFromFile(package_name)
        if package_name_from_file is None:
            io.error('upload', 'not a rpm file')
            return False
        if not utils.isPackageAccord(package_name_from_file, package_infos=package_info):
            io.error('upload', 'rpm filename disaccord with real package name')
            return False
        return True


    def _checkRpmFileAccess(self, package_name):
        if not os.access(package_name, os.F_OK):
            io.error('upload', '%s not found.' % package_name)
            return False
        elif not os.access(package_name, os.R_OK):
            io.error('upload', '%s permission denied.' % package_name)
            return False
        else:
            return True

    def _getUploadPdu(self, package_info, package_name):
        pdu = net.UploadInfoPdu()
        pdu.set("package_name", package_info["package_name"])
        pdu.set("version", package_info["version"])
        pdu.set("release", int(package_info["release"]))
        pdu.set("os_version", int(package_info["os_version"]))
        pdu.set("arch", package_info["arch"])
        file_size = os.stat(package_name).st_size
        pdu.set("file_size", int(file_size))
        return pdu

    def _uploadPackage(self, client, package_name):
        file_size = os.stat(package_name).st_size
        with open(package_name, 'rb') as fp:
            md5_hash = md5.new()
            block_size = 1024 * 9
            progress_bar = clint.textui.progress.bar(range(file_size / block_size), 'upload ')
            while True:
                try:
                    progress_bar.next()
                except:
                    pass
                read_bin = fp.read(block_size)
                md5_hash.update(read_bin)
                pdu = net.UploadBlockPdu()
                pdu.set("binary", read_bin)
                if not client.invokeRemote(pdu, output=False): 
                    return False
                if len(read_bin) != block_size:
                    break
            md5_code = md5_hash.hexdigest().upper()
            pdu = net.UploadEndPdu()
            pdu.set("md5", md5_code)
            if not client.invokeRemote(pdu, output=False):
                return False
        return True



