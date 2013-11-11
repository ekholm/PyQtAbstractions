#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Copyrighted 2011 - 2012 Mattias Ekholm <code@ekholm.se>
# Licence is LGPL 2, with following restriction
# * Modications to this file must be reported to above email

import sys

# First, deduce what bindings are choosed
__pyside4__ = ('PySide' in sys.modules) and (sys.modules['PySide'] != None)
__pyqt4__   = ('PyQt4'  in sys.modules) and (sys.modules['PyQt4']  != None)
__pykde4__  = ('PyKDE4' in sys.modules) and (sys.modules['PyKDE4'] != None)

#print('PySide' in sys.modules)
#print('PyQt4'  in sys.modules)
#print('PyKDE4' in sys.modules)

# We can't have both PySide and PyQt4 at the same time
if (__pyside4__ and __pyqt4__) or (__pyside4__ and __pykde4__):
    print('Both PySide and PyQt4 is loaded')
    sys.exit(1)

# No bindings are loaded
if not (__pyside4__ or __pyqt4__ or __pykde4__):
    print('No QT bindings are loaded')
    sys.exit(1)
    
# we choose to only export the selected Qt bindings
__all__ = ['PyQt', 'Qt', 'QtCore', 'QtGui', 'QtSvg', 'QtOpenGL', 'QtUiTools']

# Import the PySide modules
if __pyside4__:  
    import PySide
    import PySide as PyQt

    from PySide.QtCore import Qt
    from PySide import QtCore
    from PySide import QtGui
    from PySide import QtSvg
    from PySide import QtOpenGL
    from PySide import QtUiTools 

    __all__ += ['QtDeclarative', 'QtXml']
    from PySide import QtDeclarative
    from PySide import QtXml

# Import the PyQt4 modules
if __pyqt4__ or __pykde4__:
    import PyQt4
    import PyQt4 as PyQt

    from PyQt4.QtCore import Qt
    from PyQt4 import QtCore
    from PyQt4 import QtGui
    from PyQt4 import QtSvg
    # from PyQt4 import QtOpenGL 
    def QtOpenGL(): pass
    from PyQt4 import uic as QtUiTools

    PyQt.__version__ = QtCore.PYQT_VERSION_STR

    QtCore.Signal        = QtCore.pyqtSignal
    QtCore.Slot          = QtCore.pyqtSlot
    QtCore.QSize.toTuple = lambda self : (self.width(), self.height())

    QtGui.QMessageBox.StandardButton.Yes    = QtGui.QDialogButtonBox.Yes
    QtGui.QMessageBox.StandardButton.No     = QtGui.QDialogButtonBox.No
    QtGui.QMessageBox.StandardButton.Ok     = QtGui.QDialogButtonBox.Ok
    QtGui.QMessageBox.StandardButton.Cancel = QtGui.QDialogButtonBox.Cancel

    QtCore.Qt.CheckState.Checked          = QtCore.Qt.Checked
    QtCore.Qt.CheckState.Unchecked        = QtCore.Qt.Unchecked
    QtCore.Qt.CheckState.PartiallyChecked = QtCore.Qt.PartiallyChecked

# Set varuable in Qt for user to test on
Qt.isPySide = __pyside4__
Qt.isPyQt4  = __pyqt4__
Qt.isPyKDE4 = __pykde4__

# KDE4 bindings selected, import common modules
if __pykde4__:
    import PyKDE4

    __all__ += ['PyKDE4', 'plasmascript', 'Plasma', 'kdecore', 'kdeui']

    from PyKDE4.plasma import Plasma
    from PyKDE4        import plasmascript
    from PyKDE4        import kdecore
    from PyKDE4        import kdeui
