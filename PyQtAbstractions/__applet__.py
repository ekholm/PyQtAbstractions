from PyQtAbstractions.decorators     import *
from PyQtAbstractions.__qt_modules__ import *
from PyQtAbstractions.__bases__      import *

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# Applet

# For a plasma applet we have a base class that provide some nice features
class _Object(plasmascript.Applet, Base):
    def __init__(self, parent, args = None):        
        plasmascript.Applet.__init__(self, parent)
        Qt.Base.__init__(self)

    def init(self):
        self._createUI(self._mainForm)
        
    def _createUI(self, form):
        self._ui = Qt.loadUI(form)
        self._ui.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self._settings = Qt.Settings()

        widget = QtGui.QGraphicsProxyWidget(self.applet)
        widget.setWidget(self._ui)
        layout = QtGui.QGraphicsGridLayout(self.applet)
        layout.addItem(widget, 0, 0)
        
        self.setLayout(layout)
        
        self._ui._setParent(self)
        self._ui._restoreSettings()
        
        self._connectUI()

@ui_class
class _MainWindow(QtGui.QWidget, WidgetBase):
    pass

# def __init__(self, parent = None):        
#        QtGui.QWidget.__init__(self, parent)

