# -*- coding: utf-8 -*-

import sys, os
sys.path.insert(0, '/usr/share/yumtools')
import time
import subprocess
import threading
from yumtoolslib import daemon
from yumtoolslib import config
from yumtoolslib.server.createrepoworker import CreaterepoWorker
from yumtoolslib.server.servworker import ServWorker
from yumtoolslib.server.cmdprocworker import CmdprocWorker
from yumtoolslib.server.application import Application
from yumtoolslib import io


class YumtoolsServDaemon(daemon.Daemon):

    def run(self):
        cfg = config.ServerConfig()
        cfg.load('/etc/yumtools-serv.conf')


        # push all repo files
        app = Application()
        for branch_key, branch_path in cfg.branches.items():
            for el_ver in cfg.os_version_list:
                for arch in cfg.arch_list:
                    repo_path = os.path.join(cfg.base_dir, branch_path, str(el_ver), arch)
                    app.queue_createrepo.put(repo_path)

        # start workers
        crworker = CreaterepoWorker()
        servworker = ServWorker()
        cmdprocworker = CmdprocWorker()

        crworker.start()
        servworker.start()
        cmdprocworker.start()

        crworker.join()
        servworker.join()
        cmdprocworker.join()






def main():
    cfg = config.ServerConfig()
    io.use_colored = False
    if not cfg.load('/etc/yumtools-serv.conf'):
        io.error('yumtools-serv', 'load config failed.')
        return
    d = YumtoolsServDaemon("yumtools-serv", cfg.pid_file, cfg.verbose)
    d.doshell(sys.argv)


if __name__ == '__main__':
    main()


