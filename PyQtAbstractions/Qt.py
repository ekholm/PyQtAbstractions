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
import dbus.mainloop.qt

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

if Qt.isPySide: import PyQtAbstractions.pyside_resource
if Qt.isPyQt4:  import PyQtAbstractions.pyqt4_resource

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Not used...
class __MetaClass__(type):
    def __new__(mcs, name, bases, dict):
        obj = type.__new__(mcs, name, bases, dict)
        return obj

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Common base class for Widgets and widget users 
class WidgetBase(object):
    def run(self):
        res = self.exec_()
        if res == self.Accepted:
            self._saveSettings()
        return res

    def _setParent(self, parent):
        """
        Method that sets the parent attribute
        """
        
        # signal.signal(signal.SIGINT, self.sigint)
        
        self._parent   = parent
        self._settings = parent._settings

    def _restoreSettings(self):
        # Restore window size and geometry
        self._settings.beginGroup(self.objectName())
        self.move(self._settings.value("pos", QtCore.QPoint(0, 0)))
        self.resize(self._settings.value("size", QtCore.QSize(0, 0)))
        if isinstance(self, QtGui.QMainWindow):
            self.restoreState(self._settings.value("state"))
        self._settings.endGroup()

    def _saveSettings(self):
        # Save windows size and geometry
        self._settings.beginGroup(self.objectName())
        self._settings.setValue("pos",   self.pos())
        self._settings.setValue("size",  self.size())
        if isinstance(self, QtGui.QMainWindow):
            self._settings.setValue("state", self.saveState())
        self._settings.endGroup()
    
    def _connectUI(self):
        pass

    def closeEvent(self, event):
        print 'closeevet'
        # TODO: connect this event
        if not self._parent._closeUI():
            event.ignore()
            return
        
        self._saveSettings()
        event.accept()

class Base(object):
    def show(self):
        self._ui.show()

    def _connectUI(self):
        """
        Method that can be overloaded when sub class need additional preparation 
        of the UI elements after their creation
        """

        pass
    
    def _closeUI(self):
        """
        Method that can be overloaded by the subclass if some final 
        processing is required
        """

        return True

    def _createUI(self, form):
        """
        This function creates the user interfaces from the XML form file
        """

        self._ui = _load_ui(form)
        self._settings = Settings()
        
        if isinstance(self._ui, PyQtAbstractions.Qt.MainWindow)     \
                or isinstance(self._ui, PyQtAbstractions.Qt.Dialog) \
                or Qt.isPyKDE and isinstance(self._ui, PyQtAbstractions.Qt.Applet):

            self._ui._setParent(self)
            self._ui._restoreSettings()
            
            __decorators__.addActions(self)

        # Call the a user implemented method that can do any special UI bindings
        self._connectUI()

    def _setParent(self, parent):
        """
        Method that sets the parent attribute
        """

        print 'set parent not called'
        # signal.signal(signal.SIGINT, self.sigint)
        
        self._parent   = parent
        self._settings = parent._settings

    def _restoreSettings(self):
        """
        Method that restores common settings for the UI elements
        """

        pass

    def _saveSettings(self):
        """
        Method that restores common settings for the UI elements
        """

        pass

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Applet
if Qt.isPyKDE4:
    # For a plasma applet we have a base class that provide some nice features
    class Applet(plasmascript.Applet, Base):
        def __init__(self, parent, args = None):        
            plasmascript.Applet.__init__(self, parent)

        def init(self):
            self._createUI(self._mainForm)

        def _createUI(self, form):
            self._ui = _load_ui(form)
            self._ui.setAttribute(QtCore.Qt.WA_NoSystemBackground)

            widget = QtGui.QGraphicsProxyWidget(self.applet)
            widget.setWidget(self._ui)
            layout = QtGui.QGraphicsGridLayout(self.applet)
            layout.addItem(widget, 0, 0)
            
            self.setLayout(layout)

            self._connectUI()

    @ui_class
    class AppWidget(QtGui.QWidget, WidgetBase):
        pass
        # def __init__(self, parent = None):        
        #        QtGui.QWidget.__init__(self, parent)

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Application
class _Application(QtGui.QApplication):
    """
    The common base class for a Qt application
    """
    
    def __init__(self, app, ver, domain, org, argv, use_dbus = True):
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
        if use_dbus:
            dbus.mainloop.qt.DBusQtMainLoop(set_as_default = True)

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# MainWindow
@ui_class
class Dialog(QtGui.QDialog, WidgetBase):
    def _connectUI(self):
        WidgetBase._connectUI(self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# MainWindow
@ui_class
class MainWindow(QtGui.QMainWindow, WidgetBase):
    """
    Base class for an applications main window
    """

    def sigint(self, signum, frame):
         self.close()

    @on_ui_action('action_Quit')
    @on_ui_clicked('Quit')
    def _(self):
        """
        Just exits the application...
        """

        self.close()
        
    @on_ui_action('action_Print_preview')
    def _(self):
        """
        Handles the print preview request from the UI
        """

        if not self._printer:
            self.onPrinterSetttings()

        preview = PrintPreview(self._printer, self, QtCore.Qt.Window)
        __decorators__.addActions(preview)

        preview.paintRequested.connect(self._parent.doPrint)
        
        self._settings.beginGroup("PrintPreview")
        preview.move(self._settings.value("pos", QtCore.QPoint(0, 0)))
        preview.resize(self._settings.value("size", QtCore.QSize(100, 150)))
        self._settings.endGroup()
        
        preview.exec_()

    @on_ui_action('action_Printer_settings')
    def _(self):
        """
        Handles the print setting request from the UI
        """

        # TODO: here we use a dialog to set application specific settings 
        pass
        
    @on_ui_action('action_Print')
    def _(self):
        """
        Handles the print request from the UI
        """
        
        # Now let use select a printer
        printDialog = QtGui.QPrintDialog(self._printer, self)
        if printDialog.exec_() != QtGui.QDialog.Accepted:
            return 

        printer = printDialog.printer()
        
        # printer is not valid, bail our
        # TODO: do a fancy dialog here...
        if not printer.isValid():
            return
            
        self._printer = printer

        # For some reason we have to force dublex mode...
        self._printer.setDoubleSidedPrinting(True)
        self._printer.setDuplex(QtGui.QPrinter.DuplexAuto)

        # change printer resolution
        printer = QtGui.QPrinter(printer, mode = QtGui.QPrinter.HighResolution)

        # Call application to print
        self._parent.doPrint(printer, res = 300)

    @on_ui_action('action_About')
    def _(self):
        """
        Handles the about request from the UI
        """

        txt = '<b>%s</b> v %s<p>Copyright &copy; 2011-2012 %s<br>' % (
            QtGui.QApplication.applicationName(),
            QtGui.QApplication.applicationVersion(),
            QtGui.QApplication.organizationName())
        txt += 'All rights reserved<hr><p>'
        txt += 'Additional license information:<p>'

        txt += self._parent._about()

        txt += 'This program uses icons from the Crystal Clear icon set<br>'
        txt += 'The Crystal Project is released under LGPL<br>'
        txt += 'By Everaldo Coelho '
        txt += '<a href="http://www.everaldo.com/">http://www.everaldo.com/</a><p>'

        name = 'Qt toolkit'
        ver  = QtCore.qVersion()
        url  = 'http://qt.nokia.com/'
        txt += 'This program uses %s v %s<br>' % (name, ver)
        txt += '<a href="%s">%s</a><p>' % (url, url)

        if Qt.isPySide: url  = 'http://www.pyside.org/'
        if Qt.isPyQt4:  url  = 'http://www.riverbankcomputing.co.uk/software/pyqt/'
        txt += 'This program uses %s v %s<br>' % (PyQt.__name__, PyQt.__version__)
        txt += '<a href="%s">%s</a><p>' % (url, url)
            
        QtGui.QMessageBox.about(self, " " + self.windowTitle() + " ", txt)

    @on_ui_action('action_About_Qt')
    def _(self):
        """
        Handles the about Qt request from the UI
        """

        QtGui.QMessageBox.aboutQt(self, " " + self.windowTitle() + " ")

    def _restoreSettings(self):
        """
        Method that restores common settings for the UI elements
        """

        WidgetBase._restoreSettings(self)

        # Restore last printer used
        printer = QtGui.QPrinter()

        # Now find out if we have a printer already used 
        self._settings.beginGroup("Printer")
        printerName = self._settings.value("current", printer.printerName())
        self._settings.endGroup()

        # Try to find it amongst the available ones
        for p in QtGui.QPrinterInfo.availablePrinters():
            if printerName == p.printerName():
                printer = QtGui.QPrinter(p) # , mode = QtGui.QPrinter.HighResolution)
                break

        if printer.isValid():
            self._printer = printer
        else:
            self._printer = None

    def _saveSettings(self):
        WidgetBase._saveSettings(self)

        # Save the slected printer
        self._settings.beginGroup("Printer")
        self._settings.setValue("current", self._printer.printerName())
        self._settings.endGroup()
        
    def closeEvent(self, event):
        """
        Handles the close event 
        """
        
        ret = QtGui.QMessageBox.question(self, " " + self.windowTitle() + " ",
                                         "Do you really want to quit the application",
                                         QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default,
                                         QtGui.QMessageBox.No)

        if ret != QtGui.QMessageBox.StandardButton.Yes:
            event.ignore()
            return

        if not self._parent._closeUI():
            event.ignore()
            return
            
        self._saveSettings()

        event.accept()

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Object
class _Object(QtCore.QObject, Base):
    """
    Base class for UI capable class
    """

    # __metaclass__ = MetaClass

    def __init__(self, form = None):
        """
        Constructor the creates the UI elements
        """

        QtCore.QObject.__init__(self)

        if not form:
            if hasattr(self, '_mainForm'):
                self._mainForm = self._mainForm
            else:
                print "Error: form is missing"
                sys.exit(1)

        # Load the UI form that represents the main window
        self._createUI(self._mainForm)

        self.showMessage("Unknown") 

    def _about(self):
        return ""

    def showMessage(self, msg, tmo = 0):
        if Qt.isPySide:
            self._ui.statusBar().showMessage(msg, tmo)         
        else:
            self._ui.statusBar.showMessage(msg, tmo) 

    def _addLogo(self, view):
        """
        Internal method that adds the graphical logo to the logo UI element
        """

        if not hasattr(view, 'Logo'):
            return

        scene = QtGui.QGraphicsScene()
        image = QtGui.QPixmap(":/images/logo.png")
        image = image.scaled(500, 325, aspectMode = QtCore.Qt.KeepAspectRatio)
        scene.addPixmap(image)
        view.Logo.setScene(scene)

    def getWord(self, data, start, size, divisor = None, mask = None):
        """
        Returns the data bytes from a vector
        """
        
        res = 0
        if size == 2:
            r = range(size)
        else:
            r = range(size - 1, -1, -1)
             
        for i in r:
            res <<= 8
            res += data[start + i]

        if mask:
            res &= mask

        if divisor:
            res /= divisor

        return res

    def setBits(self, pre, mask, bits = None):
        """
        Updates UI check boxes accoring to a bit vector
        """

        if bits == None:
            bits = [128, 64, 32, 16, 8, 4, 2, 1]

        for a in bits:
            if not hasattr(self._ui, pre + "_%d" % a):
                continue
            o = getattr(self._ui, pre + "_%d" % a)
            if (mask & a) != 0:
                o.setCheckState(QtCore.Qt.CheckState.Checked)
            else:
                o.setCheckState(QtCore.Qt.CheckState.Unchecked)

    def fileSaveSelectDialog(self, caption, fileFilter, extDef):
        self._settings.beginGroup("File")
        state = self._settings.value("save")
        self._settings.endGroup()

        dialog = QtGui.QFileDialog(self._ui, caption)

        # TODO: why does action not work?!
        action = QtGui.QAction(dialog)
        action.setShortcut(QtGui.QKeySequence("Ctrl+Q"))
        action.triggered.connect(dialog.rejected)
        dialog.addAction(action)

        if state:
            dialog.restoreState(state)
        else:
            dialog.setDirectory(".")
            
        # dialog.selectNameFilter()
        dialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        dialog.setNameFilter(fileFilter)
        dialog.setDefaultSuffix(extDef)
        dialog.setFileMode(QtGui.QFileDialog.AnyFile)
        dialog.setOption(QtGui.QFileDialog.HideNameFilterDetails, False)
        dialog.setOption(QtGui.QFileDialog.ReadOnly, True)
        dialog.setViewMode(QtGui.QFileDialog.Detail)
        # dialog.setNameFilterDetailsVisible(True)
        # dialog.setHistory(paths)

        if dialog.exec_():
            fileName = dialog.selectedFiles()[0]
            self._settings.beginGroup("File")
            self._settings.setValue("save", dialog.saveState())
            self._settings.endGroup()

            return fileName
        else:
            return None
        
# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Print Preview
@ui_class
class PrintPreview(QtGui.QPrintPreviewDialog, WidgetBase):
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
# Settings
class Settings(QtCore.QSettings):
    """
    Help class for our application settings
    """

    def __init__(self):
        """
        Constructor that creates the storage location for the application settings
        """

        location = QtGui.QDesktopServices.HomeLocation
        settingsFile = QtGui.QDesktopServices.storageLocation(location)
        if QtGui.QApplication.organizationDomain() != None:
            settingsFile += "/.%s" % QtGui.QApplication.organizationDomain()
        settingsFile += "/%s.conf" % QtGui.QApplication.applicationName()

        QtCore.QSettings.__init__(self, settingsFile, QtCore.QSettings.NativeFormat)

    def value(self, key, defaultValue = None):
        val = QtCore.QSettings.value(self, key, defaultValue)
        if Qt.isPySide:
            return val
        else:
            return val.toPyObject()

    @classmethod
    def _getVal(cls, attr):
        """
        Abstraction for retrieving the current data from a UI element
        """

        if   isinstance(attr, QtGui.QCheckBox):
            return attr.checkState()
        elif isinstance(attr, QtGui.QComboBox):
            return attr.currentIndex()
        elif isinstance(attr, QtGui.QDoubleSpinBox):
            return attr.value()
        elif isinstance(attr, QtGui.QLineEdit):
            return attr.text()
        elif isinstance(attr, QtGui.QSpinBox):
            return attr.value()
        elif isinstance(attr, QtGui.QSlider):
            return attr.value()
        else:
            print 'Type not handled: %s' % (type(attr))
            sys.exit()

    @classmethod
    def _setVal(cls, attr, val):
        """
        Abstraction for setting the current data for a UI element
        """

        if   isinstance(attr, QtGui.QCheckBox):
            return attr.setCheckState(QtCore.Qt.CheckState(int(val)))
        elif isinstance(attr, QtGui.QComboBox):
            attr.setCurrentIndex(int(val))
        elif isinstance(attr, QtGui.QDoubleSpinBox):
            attr.setValue(float(val))
        elif isinstance(attr, QtGui.QLineEdit):
            attr.setText(val)
        elif isinstance(attr, QtGui.QSpinBox):
            attr.setValue(int(val))
        elif isinstance(attr, QtGui.QSlider):
            attr.setValue(int(val))
        else:
            print 'Type not handled: %s' % (type(attr))
            sys.exit()

    def save(self, ui, grp, pre, *items):
        """
        Saves the values from a list of UI elements
        """

        self.beginGroup(grp)
        for e in items:
            attr = getattr(ui, "%s%s" % (pre, e))
            val = self._getVal(attr)
            self.setValue(e, val)
        self.endGroup()

    def loadVars(self, grp, *items):
        vars = dict()
        self.beginGroup(grp)
        for var in items:
            (e, d) = var.split(':')
            val = self.value(e, d)
            vars[e] = val
        self.endGroup()
        return vars
        
    def saveVars(self, grp, **vars):
        self.beginGroup(grp)
        for k in vars.keys():
            print k, vars[k]
            self.setValue(k, vars[k])
        self.endGroup()

    def restore(self, ui, grp, pre, *items):
        """
        Restores the saved values for a list of UI elements
        """

        self.beginGroup(grp)
        for e in items:
            val = self.value(e, None)
            if val:
                attr = getattr(ui, "%s%s" % (pre, e))
                self._setVal(attr, val)
        self.endGroup()

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Form loading 
def _load_ui(form):
    """
    A Method that can be used when loading 
    Internal method that load a form representing an UI element
    """
        
    fp = QtCore.QFile(form)
    fp.open(QtCore.QIODevice.ReadOnly)
        
    try:
        if Qt.isPySide:
            loader = QtUiTools.QUiLoader()
            xml.sax.parse(fp, Handler(loader))
            widget = loader.load(form)
        elif Qt.isPyQt4:
            widget = QtUiTools.loadUi(fp)
        else:
            print "don't know what to do..."
            sys.exit(1)
    except Exception, e:
        print 'Failed to load form: "%s"' % (form)
        print 'Parser returned: ', e
        sys.exit(1)
        
    finally:
        fp.close()

    return widget

# For PySide we need to manually add the propagating objects
if Qt.isPySide:
    import imp
    import re

    import xml
    import xml.sax
    import xml.sax.xmlreader

    class Handler(xml.sax.handler.ContentHandler):
        """
        This class extracts and registers the modules that are used in ui files
        for promoted widgets
        """

        def __init__(self, loader):
            xml.sax.handler.ContentHandler.__init__(self)

            self._loader = loader

        def startDocument(self):
            self.white = re.compile(r'[ \r\n\t]')
            self._inside = False

        def startElement(self, name, attrs):
            if name == 'customwidget':
                self._inside = True
                self._class  = ""
                self._header = ""

            if self._inside:
                self._current = name
            
        def characters(self, content):
            if self._inside:
                name = '_%s' % self._current
                if not hasattr(self, name):
                    setattr(self, name, "")
                attr = getattr(self, name)
                attr += content
                setattr(self, name, attr)

        def endElement(self, name):
            if name == 'customwidget':
                self.inside = False

                name = self._header.strip()
                cls  = self._class.strip()

                (fp, path, desc) = imp.find_module(name)

                loaded = (name in sys.modules) and (sys.modules[name] != None)
                if not loaded:
                    imp.load_module(name, fp, path, desc)
                fp.close()

                self._loader.registerCustomWidget(getattr(sys.modules[name], cls))

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
Qt.Application   = _Application
Qt.MainWindow    = MainWindow
Qt.Object        = _Object
Qt.PrintPreview  = PrintPreview
Qt.Settings      = Settings
Qt.signal        = staticmethod(_Signal)
Qt.loadUI        = staticmethod(_load_ui)

if Qt.isPyKDE4:
    PyKDE4.Applet    = Applet
    PyKDE4.AppWidget = AppWidget

