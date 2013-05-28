# -*- coding: utf-8 -*-

import unittest
import random
from yumtoolslib import commands
import yumtoolslib.commands.helpcommand as helpcommand
import yumtoolslib.commands.uploadcommand as uploadcommand
from yumtoolslib.config import ClientConfig

class CommandsTest(unittest.TestCase):

    def test_get_command(self):
        ClientConfig().load('/etc/yumtools.conf')
        self.assertTrue(isinstance(commands.getCommand("help"), helpcommand.HelpCommand))
        self.assertTrue(isinstance(commands.getCommand("upload"), uploadcommand.UploadCommand))

