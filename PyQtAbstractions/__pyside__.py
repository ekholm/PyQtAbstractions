import imp
import re
import sys

import xml.sax

# ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
# For PySide we need to manually add the propagating objects

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
