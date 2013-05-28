# -*- coding: utf-8 -*-

from optparse import OptionParser, OptionGroup
from yumtoolslib import io
from yumtoolslib import config
from yumtoolslib import net
from yumtoolslib.client import YumtoolsClient

class CommandBase(object):

    def __init__(self):
        self.parser = OptionParser()

        cfg = config.ClientConfig()
        self.cfg = cfg

        self.parser.add_option("-v", "--verbose", dest="verbose",
                action="store_true",
                help="show debug infomation.",
                default=cfg.verbose)

        self.parser.add_option("-H", "--host",
                help="server host, default is %s" % cfg.server_host,
                default=cfg.server_host,
                metavar="HOST")

        self.parser.add_option("-p", "--port",
                help="server port, default is %d" % cfg.server_port,
                default=cfg.server_port,
                type="int",
                metavar="PORT")

        self.parser.add_option("-U", "--username",
                help="login user name",
                type="str",
                metavar="USERNAME")

        self.parser.add_option("-P", "--password",
                help="login password",
                type="str",
                metavar="PASSWORD")

        _parser = self.getOptionParser()
        self.parser.usage = _parser.usage.rstrip()
        for option in _parser.option_list:
            if not self.parser.has_option(option.get_opt_string()):
                self.parser.add_option(option)

    def login(self, options):
        user_name, password = self._getLoginInfo(options)
        client = YumtoolsClient()
        if client.connect(options.host, options.port):
            io.debug("upload", "yum server %s:%d connected." % (self.cfg.server_host, self.cfg.server_port))
        else:
            io.error("upload", "server %s:%d connect error." % (self.cfg.server_host, self.cfg.server_port))
            return False, None
        if not client.login(user_name, password):
            io.error('upload', 'auth failed')
            return False, None
        else:
            return True, client

    def execute(self, args):
        options, args = self.parser.parse_args(args)
        if options.verbose:
            io.use_debug = True
        return self.run(options, args)

    def getOptionParser(self):
        raise NotImplementedError

    def run(self, options, args):
        raise NotImplementedError

    def showHelp(self):
        self.parser.print_help()

    def _getLoginInfo(self, options):
        user_name   = options.username
        password    = options.password
        if not user_name:
            user_name = io.get("username: ")
        if not password:
            password = io.getPassword("password: ")
        return user_name, password

