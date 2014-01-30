import PyQtAbstractions
import PyQtAbstractions.__decorators__ as __decorators__

from PyQtAbstractions.__qt_modules__ import *

import os
import sys

if Qt.isPySide: 
    import xml.sax
    import __pyside__

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
            xml.sax.parse(fp, __pyside__.Handler(loader))
            widget = loader.load(form)
        elif Qt.isPyQt4:
            widget = QtUiTools.loadUi(fp)
        else:
            print("don't know what to do...")
            sys.exit(1)
    except Exception as e:
        print('Failed to load form: "{:s}"'.format(form))
        print('Parser returned: {}'.format(e))
        sys.exit(1)
        
    finally:
        fp.close()

    return widget

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Settings
class _Settings(QtCore.QSettings):
    """
    Help class for our application settings
    """

    def __init__(self, appName = None, orgDom = None):
        """
        Constructor that creates the storage location for the application settings
        """

        if appName == None: appName = QtGui.QApplication.applicationName()
        if orgDom  == None: orgDom  = QtGui.QApplication.organizationDomain()
        
        if os.name == 'posix':
            format = QtCore.QSettings.NativeFormat
            location = QtGui.QDesktopServices.HomeLocation
            settingsFile = QtGui.QDesktopServices.storageLocation(location)
            settingsFile += "/.{:s}".format(orgDom)
            settingsFile += "/{:s}.conf".format(appName)
            print(settingsFile)
            QtCore.QSettings.__init__(self, settingsFile, QtCore.QSettings.NativeFormat)
        else:
            #format = QtCore.QSettings.IniFormat
            #location = QtGui.QDesktopServices.DataLocation
            #settingsFile = QtGui.QDesktopServices.storageLocation(location)
            #settingsFile += "/{:s}".format(QtGui.QApplication.organizationDomain())
            #settingsFile += "/{:s}.conf".format(QtGui.QApplication.applicationName())
            QtCore.QSettings.__init__(self)

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
#             print attr, attr.currentText(), attr.objectName(), attr.currentIndex()
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
            print('Type not handled: {:s}'.format(type(attr)))
            sys.exit()

    @classmethod
    def _setVal(cls, attr, val):
        """
        Abstraction for setting the current data for a UI element
        """

        if   isinstance(attr, QtGui.QCheckBox):
            return attr.setCheckState(QtCore.Qt.CheckState(int(val)))
        elif isinstance(attr, QtGui.QComboBox):
#            print attr, attr.currentText(), attr.objectName(), attr.currentIndex(), val
            attr.setCurrentIndex(int(val))
#            print attr, attr.currentText(), attr.objectName(), attr.currentIndex(), val
        elif isinstance(attr, QtGui.QDoubleSpinBox):
            attr.setValue(float(val))
        elif isinstance(attr, QtGui.QLineEdit):
            attr.setText(val)
        elif isinstance(attr, QtGui.QSpinBox):
            attr.setValue(int(val))
        elif isinstance(attr, QtGui.QSlider):
            attr.setValue(int(val))
        else:
            print('Type not handled: {:s}'.format(type(attr)))
            sys.exit()

    def save(self, ui, grp, pre, *items):
        """
        Saves the values from a list of UI elements
        """

        self.beginGroup(grp)
        for e in items:
            attr = getattr(ui, "{:s}{:s}".format(pre, e))
            val = self._getVal(attr)
            # print 'Saving', e, val, attr
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
            print(k, vars[k])
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
                attr = getattr(ui, "{:s}{:s}".format(pre, e))
                self._setVal(attr, val)
        self.endGroup()

    def restoreAll(self, ui, grp, pre = None):
        """
        Restore all settings in a group
        """

        self.beginGroup(grp)
        for e in self.allKeys():
            val = self.value(e, None)

            if pre != None:
                attr = getattr(ui, "{:s}{:s}".format(pre, e))
                self._setVal(attr, val)
            else:
                try:
                    val = int(val)
                except:
                    try:
                        val = float(val)
                    except:
                        pass

            setattr(ui, e, val)
        self.endGroup()


# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Common base class for Widgets and widget users 

class Base(object):
    """Common base class for all objects containing a GUI"""
    def __init__(self, form = None):
        if not form:
            if hasattr(self, '_mainForm'):
                self._mainForm = self._mainForm
            else:
                print("Error: form is missing")
                sys.exit(1)
        
    def run(self):
        res = self._ui.exec_()
        if res == QtGui.QDialog.Accepted:
            self._saveSettings()
        return res

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
        self._settings = _Settings()
        
        if isinstance(self._ui, PyQtAbstractions.Qt.MainWindow)     \
                or isinstance(self._ui, PyQtAbstractions.Qt.Dialog) \
                or Qt.isPyKDE4 and isinstance(self._ui, PyQtAbstractions.Qt.Applet):

            self._ui._setParent(self)
            self._ui._restoreSettings()
            
            __decorators__.addActions(self)

        # Call the a user implemented method that can do any special UI bindings
        self._ui._connectUI()
        self._connectUI()

    def _setParent(self, parent):
        """
        Method that sets the parent attribute
        """

        print('set parent not called')
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
# Common base class for Widgets and widget users 
class WidgetBase(object):
    def run(self):
        res = self.exec_()
        if QtGui.QDialog.Accepted:
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
            state = self._settings.value("state")
            if state:
                self.restoreState(state)
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
        if not self._parent._closeUI():
            event.ignore()
            return
        
        self._saveSettings()
        event.accept()
