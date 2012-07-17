# -*- coding: utf-8 -*-

import os
from yumtoolslib.singleton import Singleton
from yaml import load
from yumtoolslib import io


class LoadConfigError(Exception): pass


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
        if not os.access(file_name, os.R_OK):
            io.error('config', '%s not found.' % file_name)
            return False

        try:
            fp = open(file_name, 'r')
            lines = fp.read()
            fp.close()
            obj = load(lines)
        except Exception, _ex:
            io.error('config', str(_ex))
            return False

        if obj is None:
            io.error('config', '[%s] not a config syntax' % file_name)
            return False

        result = False
        try:
            if not self._global_process(obj): return False
            result = self.process(obj)
        except LoadConfigError, _ex:
            io.error('config', '%s|%s' % (file_name, str(_ex)))
            return False

        return result

    def process(self, obj):
        raise NotImplementedError

    def _global_process(self, obj):
        self.verbose = loadAttr(obj, "verbose", type=bool, default=False)
        return True

# server config
class ServerConfig(Config):

    def init(self):
        super(ServerConfig, self).init()

    def process(self, obj):
        self.base_dir = loadAttr(obj, "server", "base_dir", type=str)
        self.serv_host = loadAttr(obj, "server", "serv_host", type=str)
        self.serv_port = loadAttr(obj, "server", "serv_port", type=int)
        self.pid_file = loadAttr(obj, "server", "pid_file", type=str)
        self.stdout_file = loadAttr(obj, "server", "stdout_file", type=str)
        self.stderr_file = loadAttr(obj, "server", "stderr_file", type=str)
        self.max_file_size = loadAttr(obj, "server", "max_file_size", type=int)
        self.upload_branch = loadAttr(obj, "server", "upload_branch", type=str)

        # branches
        self.branches = {}
        _branches = loadAttr(obj, "server", "branch_list", type=dict)
        for k, v in _branches.items():
            self.branches[str(k)] = str(v)
        if len(self.branches) < 1:
            io.error("config", "branch_list not found.")
            return False

        # os version list
        self.os_version_list = []
        _os_version_list = loadAttr(obj, "server", "os_version_list", type=list)
        for o in _os_version_list:
            self.os_version_list.append(int(o))
        if len(self.os_version_list) < 1:
            io.error("config", "os_version_list not found.")
            return False

        # arch list
        self.arch_list = []
        _arch_list = loadAttr(obj, "server", "arch_list", type=list)
        for o in _arch_list:
            self.arch_list.append(str(o))
        if len(self.arch_list) < 1:
            io.error("config", "arch_list not found.")
            return False

        # auth
        self.auth_method = loadAttr(obj, "auth_method", type=str)
        if self.auth_method == 'admin_list':
            self.admin_list = {}
            _admin_list = loadAttr(obj, "admin_list", type=dict)
            for k, v in _admin_list.items():
                self.admin_list[str(k)] = str(v)

        return True

# client config
class ClientConfig(Config):

    def init(self):
        super(ClientConfig, self).init()

    def process(self, obj):
        self.server_host = loadAttr(obj, "client", "server_host", type=str)
        self.server_port = loadAttr(obj, "client", "server_port", type=int)
        return True


