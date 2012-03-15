# Copyrighted 2011 - 2012 Mattias Ekholm <code@ekholm.se>

UI=pyMcaDBus elements elementInfo
RES=pyqt4 pyside

UI_FILES=$(patsubst %,forms/%.ui,$(UI))
RES_FILES=$(patsubst %,../PyQtAbstractions/%_resource.py,$(RES)) 

SRC=../PyQtAbstractions

all: $(RES_FILES) $(UI_FILES)

resources: $(RES_FILES)
$(SRC)/pyqt4_resource.py: resource.qrc $(UI_FILES)
	@pyrcc4 -o $@ $<

$(SRC)/pyside_resource.py: resource.qrc $(UI_FILES)
	@pyside-rcc -o $@ $<

.PHONY: resource.qrc
resource.qrc: cleanRes
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
	@find .. -name '.pyc' -exec rm '{}' \;
	@find .. -name '*~'   -exec rm '{}' \;
	@find .. -name '*_resource.*' -exec rm '{}' \;



install: all
	@(cd ..; python setup.py install)

tar: clean
	tar --exclude PyQtAbstractions -zcvf $(HOME)/PyQtAbstractions.tgz *

#forms: $(patsubst %,src/contents/code/form_%.py,$(UI))
#src/contents/code/form_%.py: forms/%.ui
#	@echo buildning ui form file: $@
#	@pykdeuic4 -o $@ $<

