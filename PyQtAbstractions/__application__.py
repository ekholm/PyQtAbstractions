from PyQtAbstractions.decorators     import *
from PyQtAbstractions.__qt_modules__ import *
from PyQtAbstractions.__bases__      import *

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Main
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
        Qt.Base.__init__(self, form)

        # Load the UI form that represents the main window
        self._createUI(self._mainForm)

        self.showMessage("Unknown") 

    def _about(self):
        return ""

    def showMessage(self, msg, tmo = 0):
        if not hasattr(self._ui, 'statusBar'):
            return

        return
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
# MainWindow
@ui_class
class _MainWindow(QtGui.QMainWindow, WidgetBase):
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

