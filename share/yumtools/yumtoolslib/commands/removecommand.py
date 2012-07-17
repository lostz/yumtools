# -*- coding: utf-8 -*-

import os
import re
import md5
from optparse import OptionParser
from validate import validate
from yumtoolslib.commands.commandbase import CommandBase
from yumtoolslib import io, utils, net
from yumtoolslib.config import ClientConfig
from yumtoolslib.client import YumtoolsClient

USAGE_MSG = """
    yumtools {remove | rm} [options] package_name package_version release os_version arch branch
"""


class RemoveCommand(CommandBase):

    def getOptionParser(self):
        result = OptionParser(USAGE_MSG)
        return result

    def run(self, options, args):

        # check arguments
        if len(args) != 6:
            io.error('remove', 'arguments count is not enough.')
            return 1

        io.debug("remove", "checking arguments...")

        try:
            package_name = validate.is_string(args[0])
            package_version = validate.is_string(args[1])
            release = validate.is_integer(args[2])
            os_version = validate.is_integer(args[3])
            arch = validate.is_string(args[4])
            branch = validate.is_string(args[5])
        except Exception, _ex:
            io.error('', 'parameter format error.')
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
            io.debug("remove", "yum server %s:%d connected." % (self.cfg.server_host, self.cfg.server_port))
        else:
            io.error("remove", "server %s:%d connect error." % (self.cfg.server_host, self.cfg.server_port))
            return 99

        if not client.login(user_name, password):
            return 99

        # invoke remove
        pdu = net.RemovePdu()
        pdu.set('package_name', package_name)
        pdu.set('version', package_version)
        pdu.set('release', release)
        pdu.set('os_version', os_version)
        pdu.set('arch', arch)
        pdu.set('branch', branch)
        if not client.invokeRemote(pdu): return 5

        return 0


