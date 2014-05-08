# Copyrighted 2011 - 2012 Mattias Ekholm <code@ekholm.se>

NAME=PyQtAbstractions
RES=pyqt4 pyqt5 pyside 

SRC=../PyQtAbstractions

UI_FILES=$(wildcard forms/*.ui)
RES_FILES=$(patsubst %,$(SRC)/%_resource2.py,$(RES)) $(patsubst %,$(SRC)/%_resource3.py,$(RES)) 

all: $(RES_FILES) $(UI_FILES)

resources: $(RES_FILES)
$(SRC)/pyqt4_resource%.py: resource.qrc $(UI_FILES)
	@echo "Buildning resource file: \"$@\""
	@(which pyrcc4 > /dev/null 2>&1 && pyrcc4 -py$* -o $@ $<) || echo "Skipped: $@"

$(SRC)/pyqt5_resource2.py:
	@true

$(SRC)/pyqt5_resource3.py: resource.qrc $(UI_FILES)
	@echo "Buildning resource file: \"$@\""
	@(which pyrcc5 > /dev/null 2>&1 && pyrcc5 -o $@ $<) || echo "Skipped: $@"

$(SRC)/pyside_resource%.py: resource.qrc $(UI_FILES)
	@echo "Buildning resource file: \"$@\""	
	@(which pyside-rcc > /dev/null 2>&1 && pyside-rcc -py$* -o $@ $<) || echo "Skipped: $@"

.PHONY: resource.qrc
resource.qrc: cleanRes
	@echo "Generating resource file \"$@\""
	@echo "<RCC>" > $@
	@echo "  <qresource prefix=\"/\">" >> $@
	@find forms  -type f | awk  '{printf("    <file>%s</file>\n", $$1)}' >> $@
	@find images -type f | awk  '{printf("    <file>%s</file>\n", $$1)}' >> $@
	@find icons  -type f | awk  '{printf("    <file>%s</file>\n", $$1)}' >> $@
	@echo "  </qresource>" >> $@
	@echo "</RCC>" >> $@

cleanRes:
	@find . -name '*~'         -exec rm '{}' \;

clean:
	@echo "Cleaning"
	@rm -rf ../build
	@find .. -name 'resource.qrc' -exec rm '{}' \;
	@find .. -name '*.pyc'        -exec rm '{}' \;
	@find .. -name '*~'           -exec rm '{}' \;
	@find .. -name '*_resource.*' -exec rm '{}' \;

install: all
	@(cd ..; python setup.py install)

tar: clean
	tar --exclude PyQtAbstractions -zcvf $(HOME)/PyQtAbstractions.tgz *

#forms: $(patsubst %,src/contents/code/form_%.py,$(UI))
#src/contents/code/form_%.py: forms/%.ui
#	@echo buildning ui form file: $@
#	@pykdeuic4 -o $@ $<

