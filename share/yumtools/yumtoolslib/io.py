# -*- coding: utf-8 -*-

import getpass
import clint
from clint.textui import colored, puts

use_colored = True
use_debug = True
use_log = True
use_error = True

def debug(mod, msg):
    if mod: mod = mod + ' '
    if not use_debug:
        return
    if use_colored:
        puts("%s%s" % (colored.yellow("DEBUG %s" % mod), msg))
    else:
        print "DEBUG %s%s" % (mod, msg)

def log(mod, msg):
    if mod: mod = mod + ' '
    if not use_log:
        return
    if use_colored:
        puts("%s%s" % (colored.cyan("LOG %s" % mod), msg))
    else:
        print "LOG %s%s" % (mod, msg)

def error(mod, msg):
    if mod: mod = mod + ' '
    if not use_error:
        return
    if use_colored:
        puts("%s%s" % (colored.magenta("ERROR %s" % mod), msg))
    else:
        print "ERROR %s%s" % (mod, msg)

def get(label):
    return raw_input(label)

def getPassword(label):
    return getpass.getpass(label)

