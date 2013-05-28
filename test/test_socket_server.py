#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '/usr/share/yumtools')
import yumtoolslib.net as net

t = net.SafeTCP()
t.bind(('0.0.0.0', 10031))
t.listen(2)
print dir(t)
a = t.accept()
print a


