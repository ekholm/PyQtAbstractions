# -*- coding: iso-8859-15 -*-
# Copyrighted 2011 - 2012 Mattias Ekholm <code@ekholm.se>
# Licence is LGPL 2, with following restriction
# * Modications to this file must be reported to above email

import sys

try:
    from   PyQtAbstractions.__qt_modules__ import *
except:
    import os
    sys.path.append(os.path.dirname(__file__))
    from   __qt_modules__ import *

if sys.version_info.major == 2:
    if Qt.isPySide: import PyQtAbstractions.pyside_resource2
    if Qt.isPyQt4:  import PyQtAbstractions.pyqt4_resource2
elif sys.version_info.major == 3:
    if Qt.isPySide: import PyQtAbstractions.pyside_resource3
    if Qt.isPyQt4:  import PyQtAbstractions.pyqt4_resource3
    if Qt.isPyQt5:  import PyQtAbstractions.pyqt5_resource3
