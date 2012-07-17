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
from yumtoolslib.config import ClientConfig
from yumtoolslib.client import YumtoolsClient

USAGE_MSG = """
    yumtools {upload | up} [options] file
"""


class UploadCommand(CommandBase):

    def getOptionParser(self):
        result = OptionParser(USAGE_MSG)
        return result

    def run(self, options, args):

        # check arguments
        if len(args) != 1:
            io.error('upload', 'no such package name.')
            return 1

        pkg_name = args[0]
        io.log('upload', 'checking %s ...' % pkg_name)
        pkg_infos = utils.getPackageInfos(pkg_name)
        if pkg_infos is None:
            io.error('upload', 'package name is not a valid format. format: <package_name>-<package_version>-<release>.el<os_version>.<arch>.rpm')
            return 2

        if not os.access(pkg_name, os.O_RDONLY):
            io.error('upload', '%s is not accessable' % pkg_name)
            return 2

        # get username/password
        user_name = options.username
        password = options.password
        if not user_name:
            user_name = io.get("username: ")
        if not password:
            password = io.getPassword("password: ")
        password = utils.passwordHash(password)

        # init yumtools client
        client = YumtoolsClient()

        # connect
        if client.connect(options.host, options.port):
            io.debug("upload", "yum server %s:%d connected." % (self.cfg.server_host, self.cfg.server_port))
        else:
            io.error("upload", "server %s:%d connect error." % (self.cfg.server_host, self.cfg.server_port))
            return 99

        if not client.login(user_name, password):
            return 99

        # upload
        io.log('upload', 'start upload %s ...' % pkg_name)

        pkg_infos = utils.getPackageInfos(pkg_name)
        if pkg_infos is None:
            io.error('upload', 'package name is not a valid format. format: <package_name>-<package_version>-<release>.el<os_version>.<arch>.rpm')
            return 2

        pdu = net.UploadInfoPdu()
        pdu.set("package_name", pkg_infos["package_name"])
        pdu.set("version", pkg_infos["version"])
        pdu.set("release", int(pkg_infos["release"]))
        pdu.set("os_version", int(pkg_infos["os_version"]))
        pdu.set("arch", pkg_infos["arch"])
        file_size = os.stat(pkg_name).st_size
        pdu.set("file_size", int(file_size))
        if not client.invokeRemote(pdu): return 5

        with open(pkg_name, 'rb') as fp:
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
                if not client.invokeRemote(pdu, output=False): return 6

                if len(read_bin) != block_size:
                    break

            # md5
            md5_code = md5_hash.hexdigest().upper()

            pdu = net.UploadEndPdu()
            pdu.set("md5", md5_code)
            if not client.invokeRemote(pdu, output=False): return 7

        # ok
        return 0


