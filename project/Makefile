# Copyrighted 2011 - 2012 Mattias Ekholm <code@ekholm.se>

all: ../PyQtAbstractions/pyqt4_resource.py ../PyQtAbstractions/pyside_resource.py

../PyQtAbstractions/pyqt4_resource.py: resource.qrc forms/pyMcaDBus.ui forms/elements.ui forms/elementInfo.ui
	@pyrcc4 -o $@ $<

../PyQtAbstractions/pyside_resource.py: resource.qrc forms/pyMcaDBus.ui forms/elements.ui forms/elementInfo.ui
	@pyside-rcc -o $@ $<

clean:
	@find . -name '.pyc' -exec rm '{}' \;
	@find . -name '*~'   -exec rm '{}' \;
	@find . -name 'pyside_resource.*'   -exec rm '{}' \;
	@find . -name 'pyqt4_resource.*'   -exec rm '{}' \;

install: all
	echo "Nothing to do: start server first and then client"

tar: clean
	tar --exclude PyQtAbstractions -zcvf $(HOME)/PyQtAbstractions.tgz *
