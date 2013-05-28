# -*- coding: utf-8 -*-

from yumtoolslib import io

def makeCommandName(qstr):
    return "%sCommand" % qstr.title()

def getCommand(qstr):
    cmd_name = makeCommandName(qstr)
    try:
        module_name = "yumtoolslib.commands.%scommand" % qstr
        module_ = __import__(module_name, globals(), locals(), [cmd_name])
        if hasattr(module_, cmd_name):
            return getattr(module_, cmd_name)()
        else:
            return None
    except Exception, _ex:
        return None



