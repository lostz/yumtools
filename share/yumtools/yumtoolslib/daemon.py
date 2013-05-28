# -*- coding: utf-8 -*-

import sys
import os
import time
import atexit
import signal

class Daemon(object):
    """A generic daemon class.

    Usage: subclass the daemon class and override the run() method."""

    def __init__(self, appname, pidfile, def_output=False):
        self.appname = appname
        self.pidfile = pidfile
        self.def_output = def_output

    def _firstFork():
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, err:
            sys.stderr.write('fork #1 failed: %s\n' % str(err))
            sys.exit(1)

        # decouple from parent environment
        os.chdir('/')
        os.setsid()

    def _secondFork():
        # do second fork
        try:
            pid = os.fork()
            if pid > 0:

                # exit from second parent
                sys.exit(0)
        except OSError, err:
            sys.stderr.write('fork #2 failed: %s\n' % str(err))
            sys.exit(1)

    def _initOutput():
        # redirect standard file descriptors
        if not self.def_output:
            sys.stdout.flush()
            sys.stderr.flush()
            si = open(os.devnull, 'r')
            so = open(os.devnull, 'a+')
            se = open(os.devnull, 'a+')

            os.dup2(si.fileno(), sys.stdin.fileno())
            os.dup2(so.fileno(), sys.stdout.fileno())
            os.dup2(se.fileno(), sys.stderr.fileno())

    def _writePidFile():
        try:
            pid = str(os.getpid())
            fp = open(self.pidfile,'w+')
            fp.write(pid + '\n')
            fp.close()
        except Exception, _ex:
            sys.stderr.write(str(_ex))

    def _readPidFile():
        # Check for a pidfile to see if the daemon already runs
        try:
            fp = open(self.pidfile,'r')
            pid = int(fp.read().strip())
            fp.close()
        except IOError:
            pid = None
        return pid

    def daemonize(self):
        """Deamonize class. UNIX double fork mechanism."""

        self._firstFork()
        self._secondFork()
        self._initOutput()

        # write pidfile
        atexit.register(self.delpid)

        self._writePidFile()


    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """Start the daemon."""

        pid = self._readPidFile()
        if pid is not None:
            message = "pidfile %s already exist. " + \
                    "Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        sys.stdout.write("Service starting .. [OK]\n")
        sys.stdout.flush()
        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """Stop the daemon."""

        pid = self._readPidFile()
        if pid is None:
            message = "pidfile %s does not exist. " + \
                    "Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart

        sys.stdout.write("Service stopping ")
        sys.stdout.flush()
        # Try killing the daemon process    
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
                sys.stdout.write(".")
                sys.stdout.flush()
        except OSError, err:
            e = str(err.args)
            if e.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print (str(err.args))
                sys.exit(1)

        sys.stdout.write("  [OK]\n")


    def restart(self):
        """Restart the daemon."""
        self.stop()
        self.start()

    def run(self):
        """You should override this method when you subclass Daemon.

        It will be called after the process has been daemonized by 
        start() or restart()."""
        raise NotImplementedError

    def doshell(self, argv):
        prog_name = self.appname

        def usage():
            print >>sys.stderr, "Usage: %(prog)s start|stop|restart" % {
                    "prog": prog_name }
            sys.exit(0)

        if len(argv) != 2:
            usage()
            print

        command = argv[1]
        if command == "start":
            self.start()
        elif command == "stop":
            self.stop()
        elif command == "restart":
            self.restart()
        else:
            usage()



