#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Copyrighted 2011 - 2012 Mattias Ekholm <code@ekholm.se>
# Licence is LGPL 2, with following restriction
# * Modications to this file must be reported to above email

"""
This module provides an abstraction level on top on Qt. It consolidates 
nice to have features into base clases on top of Qt classes.
"""

import sys
try:
    import dbus.mainloop.qt
    _use_dbus = True
except:
    _use_dbus = False


try:
    from   PyQtAbstractions.decorators     import *
    import PyQtAbstractions.decorators     as decorators
    import PyQtAbstractions.__decorators__ as __decorators__
    from   PyQtAbstractions.__qt_modules__ import *

    import PyQtAbstractions.Spectrum

except:
    import os
    sys.path.append(os.path.dirname(__file__))

    from   decorators     import *
    import decorators     as decorators
    import __decorators__ as __decorators__
    from   __qt_modules__ import *

# choose resource file 
from resources import *

# choose application
if Qt.isPyKDE4: 
    import PyQtAbstractions.__applet__      as __app__
    import PyQtAbstractions.__application__ 
    Object = PyQtAbstractions.__application__._Object
elif Qt.isPySide or Qt.isPyQt4:
    import PyQtAbstractions.__application__ as __app__
    import PyQtAbstractions.__application__ as __app__
    Object = __app__._Object

class MainObject(__app__._Object):     pass 
class MainWindow(__app__._MainWindow): pass

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Not used...
class __MetaClass__(type):
    def __new__(mcs, name, bases, dict):
        obj = type.__new__(mcs, name, bases, dict)
        return obj


# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Application
class _Application(QtGui.QApplication):
    """
    The common base class for a Qt application
    """
    
    def __init__(self, app, ver, domain, org, argv, use_dbus = False):
        """
        The constructor that handles the common data
        """
        
        QtGui.QApplication.setOrganizationDomain(domain)
        QtGui.QApplication.setOrganizationName(org)
        QtGui.QApplication.setApplicationName(app)
        QtGui.QApplication.setApplicationVersion(ver)

        QtGui.QApplication.__init__(self, argv)

        # QtGui.QFontDatabase.addApplicationFont(<font path>)

        # let dbus us the Qt main loop
        if use_dbus and _use_dbus:
            dbus.mainloop.qt.DBusQtMainLoop(set_as_default = True)

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# MainWindow
@ui_class
class Dialog(QtGui.QDialog, PyQtAbstractions.__bases__.WidgetBase):
    def _connectUI(self):
        PyQtAbstractions.__bases__.WidgetBase._connectUI(self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)


# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Print Preview
@ui_class
class PrintPreview(QtGui.QPrintPreviewDialog, PyQtAbstractions.__bases__.WidgetBase):
    """
    The print preview dialog
    """

    def __init__(self, printer, parent, flags):
        """
        Constructor
        """

        QtGui.QPrintPreviewDialog.__init__(self, printer, parent, flags)

        self._settings = parent._settings

    @on_ui_short_cut('Ctrl+Q')
    def _(self):
        self.close()
        
    def closeEvent(self, event):
        """
        Called when dialog is closed and stores window geometry
        """

        self._settings.beginGroup("PrintPreview")
        self._settings.setValue("pos",  self.pos())
        self._settings.setValue("size", self.size())
        self._settings.endGroup()
        event.accept()

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Signal handling
def _Signal(*args, **kargs):
    sig = QtCore.Signal(*args, **kargs)
    decorators._signal_types[sig] = (args, kargs)

    return sig

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
Qt.Application   = _Application
Qt.Base          = PyQtAbstractions.__bases__.Base
Qt.Dialog        = Dialog
Qt.PrintPreview  = PrintPreview
Qt.Settings      = PyQtAbstractions.__bases__._Settings
Qt.signal        = staticmethod(_Signal)
Qt.loadUI        = staticmethod(PyQtAbstractions.__bases__._load_ui)

Qt.Object     = Object
Qt.MainObject = MainObject
Qt.MainWindow = MainWindow
