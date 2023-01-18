from __future__ import print_function

import sys
import os
pj = os.path.join

for (ui, dst) in [ ('mainwindow.ui', pj('..','ui_mainwindow.py')),
                   ('newgraph.ui', pj('..','ui_newgraph.py')),
                   ('newpackage.ui', pj('..','ui_newpackage.py')),
                   ('tofactory.ui', pj('..','ui_tofactory.py')),
                   ('preferences.ui', pj('..','ui_preferences.py')),
                   ('ioconfig.ui', pj('..','ui_ioconfig.py')),
                   ('tableedit.ui', pj('..','ui_tableedit.py')),
                   ]:
    cmd = "pyuic5 --from-imports -x %s -o %s "%(ui, dst)
    print(cmd)
    os.system(cmd)

# resources 
os.system("pyrcc5 %s > %s "%("images.qrc", "..%simages_rc.py"%(os.sep,)))