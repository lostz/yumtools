# -*- coding: utf-8 -*-

import os
import yaml
from yumtoolslib.singleton import Singleton
from yumtoolslib import io

class LoadConfigError(Exception):
    pass

# @param kwargs
# @param default
# @param raise_error
# @param type
def loadAttr(dt, *args, **kwargs):
    default = None
    raise_error = True
    tpe = None
    if kwargs.has_key('default'):
        default = kwargs['default']
    if kwargs.has_key('raise_error') and kwargs['raise_error'] == False:
        raise_error = False
    if kwargs.has_key('type'):
        tpe = kwargs['type']

    tmp_val = dt

    # check default values type
    if (default is not None) and (tpe is not None):
        if not isinstance(default, tpe):
            if raise_error:
                raise LoadConfigError, "default is not %s type" % str(tpe)
            else:
                return None

    # fetch value
    for arg in args:
        if not tmp_val.has_key(arg):
            if default is not None:
                return default
            if raise_error:
                raise LoadConfigError, "not found config option %s" % "->".join(args)
            return None
        tmp_val = tmp_val[arg]

    # check type
    if tpe is not None:
        if not isinstance(tmp_val, tpe):
            if default is not None:
                return default
            if raise_error:
                raise LoadConfigError, "result is not a %s type" % str(tpe)
            return None

    return tmp_val


# config base
class Config(Singleton):

    def init(self):
        self.verbose = True

    def load(self, file_name):
        if not self._checkConfigFile(file_name):
            return False

        file_content = self._getFileContent(file_name)
        if file_content is None:
            io.error('config', '[%s] is not in valid config syntax' % file_name)
            return False
        else:
            return self._parseAllConfig(file_content, file_name)

    def parseAttr(self, file_content):
        raise NotImplementedError

    def _checkConfigFile(self, file_name):
        if not os.access(file_name, os.F_OK):
            io.error('config', '%s not found.' % file_name)
            return False
        elif not os.access(file_name, os.R_OK):
            io.error('config', '%s permission denied.' % file_name)
            return False
        else:
            return True

    def _getFileContent(self, file_name):
        try:
            fp = open(file_name, 'r')
            lines = fp.read()
            fp.close()
            file_content = yaml.load(lines)
        except Exception, _ex:
            io.error('config', str(_ex))
            return None
        else:
            return file_content

    def _parseGlobalConfig(self, file_content):
        self.verbose = loadAttr(file_content, "verbose", type=bool, default=False)
        return True

    def _parseAllConfig(self, file_content, file_name):
        result = True
        try:
            if not self._parseGlobalConfig(file_content):
                return False
            result = self.parseAttr(file_content)
        except LoadConfigError, _ex:
            io.error('config', '%s | %s' % (file_name, str(_ex)))
            result = False
        else:
            return result

# server config
class ServerConfig(Config):

    def init(self):
        super(ServerConfig, self).init()

    def parseAttr(self, file_content):
        if not self._parseBasicAttr(file_content):
            return False
        if not self._parseBranchAttr(file_content):
            return False
        if not self._parseOSVersionAttr(file_content):
            return False
        if not self._parseArchAttr(file_content):
            return False
        if not self._parseAuthAttr(file_content):
            return False
        return True

    def _parseBasicAttr(self, file_content):
        self.base_dir       = loadAttr(file_content, "server", "base_dir", type=str)
        self.serv_host      = loadAttr(file_content, "server", "serv_host", type=str)
        self.serv_port      = loadAttr(file_content, "server", "serv_port", type=int)
        self.pid_file       = loadAttr(file_content, "server", "pid_file", type=str)
        self.stdout_file    = loadAttr(file_content, "server", "stdout_file", type=str)
        self.stderr_file    = loadAttr(file_content, "server", "stderr_file", type=str)
        self.max_file_size  = loadAttr(file_content, "server", "max_file_size", type=int)
        self.upload_branch  = loadAttr(file_content, "server", "upload_branch", type=str)
        self.mail_receiver  = loadAttr(file_content, "server", "mail_receiver", type=str)
        self.mail_sender    = loadAttr(file_content, "server", "mail_sender", type=str)
        return True

    def _parseBranchAttr(self, file_content):
        self.branches = {}
        branches = loadAttr(file_content, "server", "branch_list", type=dict)
        for k, v in branches.items():
            self.branches[str(k)] = str(v)
        if len(self.branches) < 1:
            io.error("config", "branch_list not found.")
            return False
        else:
            return True

    def _parseOSVersionAttr(self, file_content):
        self.os_version_list = []
        os_version_list = loadAttr(file_content, "server", "os_version_list", type=list)
        for o in os_version_list:
            self.os_version_list.append(int(o))
        if len(self.os_version_list) < 1:
            io.error("config", "os_version_list not found.")
            return False
        else:
            return True

    def _parseArchAttr(self, file_content):
        self.arch_list = []
        arch_list = loadAttr(file_content, "server", "arch_list", type=list)
        for o in arch_list:
            self.arch_list.append(str(o))
        if len(self.arch_list) < 1:
            io.error("config", "arch_list not found.")
            return False
        else:
            return True

    def _parseAuthAttr(self, file_content):
        self.auth_method = loadAttr(file_content, "auth_method", type=str)
        if self.auth_method == 'admin_list':
            self.admin_list = {}
            admin_list = loadAttr(file_content, "admin_list", type=dict)
            for k, v in admin_list.items():
                self.admin_list[str(k)] = str(v)
        else:
            pass
        return True


# client config
class ClientConfig(Config):

    def init(self):
        super(ClientConfig, self).init()

    def parseAttr(self, file_content):
        return self._parseAttr(file_content)

    def _parseAttr(self, file_content):
        self.server_host = loadAttr(file_content, "client", "server_host", type=str)
        self.server_port = loadAttr(file_content, "client", "server_port", type=int)
        return True



