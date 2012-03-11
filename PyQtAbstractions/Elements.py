#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Copyrighted 2011 - 2012 Mattias Ekholm <code@ekholm.se>
# Licence is LGPL 2, with following restriction
# * Modications to this file must be reported to above email

"""
This module contains the base class for the element handler
"""

__all__ = []

from inka import *

# This table is from PyMca
Elements = [
   ["H",   1,    "Hydrogen",   1.00800,     1008.00   ],
   ["He",  2,    "Helium",     4.00300,     0.118500  ],
   ["Li",  3,    "Lithium",    6.94000,     534.000   ],
   ["Be",  4,    "Beryllium",  9.01200,     1848.00   ],
   ["B",   5,    "Boron",      10.8110,     2340.00   ],
   ["C",   6,    "Carbon",     12.0100,     1580.00   ],
   ["N",   7,    "Nitrogen",   14.0080,     1.25      ],
   ["O",   8,    "Oxygen",     16.0000,     1.429     ],
   ["F",   9,    "Fluorine",   19.0000,     1108.00   ],
   ["Ne",  10,   "Neon",       20.1830,     0.9       ],
   ["Na",  11,   "Sodium",     22.9970,     970.000   ],
   ["Mg",  12,   "Magnesium",  24.3200,     1740.00   ],
   ["Al",  13,   "Aluminium",  26.9700,     2720.00   ],
   ["Si",  14,   "Silicon",    28.0860,     2330.00   ],
   ["P",   15,   "Phosphorus", 30.9750,     1820.00   ],
   ["S",   16,   "Sulphur",    32.0660,     2000.00   ],
   ["Cl",  17,   "Chlorine",   35.4570,     1560.00   ],
   ["Ar",  18,   "Argon",      39.9440,     1.78400   ],
   ["K",   19,   "Potassium",  39.1020,     862.000   ],
   ["Ca",  20,   "Calcium",    40.0800,     1550.00   ],
   ["Sc",  21,   "Scandium",   44.9600,     2992.00   ],
   ["Ti",  22,   "Titanium",   47.9000,     4540.00   ],
   ["V",   23,   "Vanadium",   50.9420,     6110.00   ],
   ["Cr",  24,   "Chromium",   51.9960,     7190.00   ],
   ["Mn",  25,   "Manganese",  54.9400,     7420.00   ],
   ["Fe",  26,   "Iron",       55.8500,     7860.00   ],
   ["Co",  27,   "Cobalt",     58.9330,     8900.00   ],
   ["Ni",  28,   "Nickel",     58.6900,     8900.00   ],
   ["Cu",  29,   "Copper",     63.5400,     8940.00   ],
   ["Zn",  30,   "Zinc",       65.3800,     7140.00   ],
   ["Ga",  31,   "Gallium",    69.7200,     5903.00   ],
   ["Ge",  32,   "Germanium",  72.5900,     5323.00   ],
   ["As",  33,   "Arsenic",    74.9200,     5.73000   ],
   ["Se",  34,   "Selenium",   78.9600,     4790.00   ],
   ["Br",  35,   "Bromine",    79.9200,     3120.00   ],
   ["Kr",  36,   "Krypton",    83.8000,     3.74000   ],
   ["Rb",  37,   "Rubidium",   85.4800,     1532.00   ],
   ["Sr",  38,   "Strontium",  87.6200,     2540.00   ],
   ["Y",   39,   "Yttrium",    88.9050,     4405.00   ],
   ["Zr",  40,   "Zirconium",  91.2200,     6530.00   ],
   ["Nb",  41,   "Niobium",    92.9060,     8570.00   ],
   ["Mo",  42,   "Molybdenum", 95.9500,     10220.00  ],
   ["Tc",  43,   "Technetium", 99.0000,     11500.0   ],
   ["Ru",  44,   "Ruthenium",  101.0700,    12410.0   ],
   ["Rh",  45,   "Rhodium",    102.9100,    12440.0   ],
   ["Pd",  46,   "Palladium",  106.400,     12160.0   ],
   ["Ag",  47,   "Silver",     107.880,     10500.00  ],
   ["Cd",  48,   "Cadmium",    112.410,     8650.00   ],
   ["In",  49,   "Indium",     114.820,     7280.00   ],
   ["Sn",  50,   "Tin",        118.690,     5310.00   ],
   ["Sb",  51,   "Antimony",   121.760,     6691.00   ],
   ["Te",  52,   "Tellurium",  127.600,     6240.00   ],
   ["I",   53,   "Iodine",     126.910,     4940.00   ],
   ["Xe",  54,   "Xenon",      131.300,     5.90000   ],
   ["Cs",  55,   "Caesium",    132.910,     1873.00   ],
   ["Ba",  56,   "Barium",     137.360,     3500.00   ],
   ["La",  57,   "Lanthanum",  138.920,     6150.00   ],
   ["Ce",  58,   "Cerium",     140.130,     6670.00   ],
   ["Pr",  59,   "Praseodymium",140.920,    6769.00   ],
   ["Nd",  60,   "Neodymium",  144.270,     6960.00   ],
   ["Pm",  61,   "Promethium", 147.000,     6782.00   ],
   ["Sm",  62,   "Samarium",   150.350,     7536.00   ],
   ["Eu",  63,   "Europium",   152.000,     5259.00   ],
   ["Gd",  64,   "Gadolinium", 157.260,     7950.00   ],
   ["Tb",  65,   "Terbium",    158.930,     8272.00   ],
   ["Dy",  66,   "Dysprosium", 162.510,     8536.00   ],
   ["Ho",  67,   "Holmium",    164.940,     8803.00   ],
   ["Er",  68,   "Erbium",     167.270,     9051.00   ],
   ["Tm",  69,   "Thulium",    168.940,     9332.00   ],
   ["Yb",  70,   "Ytterbium",  173.040,     6977.00   ],
   ["Lu",  71,   "Lutetium",   174.990,     9842.00   ],
   ["Hf",  72,   "Hafnium",    178.500,     13300.0   ],
   ["Ta",  73,   "Tantalum",   180.950,     16600.0   ],
   ["W",   74,   "Tungsten",   183.920,     19300.0   ],
   ["Re",  75,   "Rhenium",    186.200,     21020.0   ],
   ["Os",  76,   "Osmium",     190.200,     22500.0   ],
   ["Ir",  77,   "Iridium",    192.200,     22420.0   ],
   ["Pt",  78,   "Platinum",   195.090,     21370.0   ],
   ["Au",  79,   "Gold",       197.200,     19370.0   ],
   ["Hg",  80,   "Mercury",    200.610,     13546.0   ],
   ["Tl",  81,   "Thallium",   204.390,     11860.0   ],
   ["Pb",  82,   "Lead",       207.210,     11340.0   ],
   ["Bi",  83,   "Bismuth",    209.000,     9800.00   ],
   ["Po",  84,   "Polonium",   209.000,     0         ],
   ["At",  85,   "Astatine",   210.000,     0         ],
   ["Rn",  86,   "Radon",      222.000,     9.73000   ],
   ["Fr",  87,   "Francium",   223.000,     0         ],
   ["Ra",  88,   "Radium",     226.000,     0         ],
   ["Ac",  89,   "Actinium",   227.000,     0         ],
   ["Th",  90,   "Thorium",    232.000,     11700.0   ],
   ["Pa",  91,   "Proactinium",231.03588,   0         ],
   ["U",   92,   "Uranium",    238.070,     19050.0   ],
   ["Np",  93,   "Neptunium",  237.000,     0         ],
   ["Pu",  94,   "Plutonium",  239.100,     19700.0   ],
   ["Am",  95,   "Americium",  243,         0         ],
   ["Cm",  96,   "Curium",     247,         0         ],
   ["Bk",  97,   "Berkelium",  247,         0         ],
   ["Cf",  98,   "Californium",251,         0         ],
   ["Es",  99,   "Einsteinium",252,         0         ],
   ["Fm",  100,  "Fermium",    257,         0         ],
   ["Md",  101,  "Mendelevium",258,         0         ],
   ["No",  102,  "Nobelium",   259,         0         ],
   ["Lr",  103,  "Lawrencium", 262,         0         ],
   ["Rf",  104,  "Rutherfordium",261,       0         ],
   ["Db",  105,  "Dubnium",    262,         0         ],
   ["Sg",  106,  "Seaborgium", 266,         0         ],
   ["Bh",  107,  "Bohrium",    264,         0         ],
   ["Hs",  108,  "Hassium",    269,         0         ],
   ["Mt",  109,  "Meitnerium", 268,         0         ],
   ["Ds",  110,  "Darmstadtium", 0, 0],
   ["Rg",  111,  "Roentgenium", 0, 0],
   ["Cn",  112,  "Copernicum", 0, 0],
   ["Uut", 113,  "Ununtrium", 0, 0],
   ["Uuq", 114,  "Ununquadium", 0, 0],
   ["Uup", 115,  "Ununpentium", 0, 0],
   ["Uuh", 116,  "Ununhexium", 0, 0],
   ["Uus", 117,  "Ununseptium", 0, 0],
   ["Uuo", 118,  "Ununoctium", 0, 0],
]

Elems = [e[0] for e in Elements]

import PyMca.Elements
import PyMca.ElementHtml

def createWidget(self = None):
    elements = Qt.loadUI(':/forms/elements.ui')
    if self:
        elements.restore(self._settings)
    
    elements.setInfoProvider(PyMca.ElementHtml.ElementHtml())
    elements.DetailedElementInfo.hide()
    elements.Energy.setValidator(QtGui.QDoubleValidator())

    decorators.addActions(elements)

    return elements

@ui_class
class ElementWidget(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.element   = 0
        self._settings = None

        PyMca.Elements.registerUpdate(self.updateCallback)

    @on_ui_short_cut('Ctrl+Q')
    def _(self):
        self.close()

    @on_ui_finished('Energy')
    def _(self):
        energy = float(self.Energy.text())

        PyMca.Elements.updateDict(energy = energy)

    def updateCallback(self):
        element =  Elements[self.element][0]
        energy = PyMca.Elements.Element[element]['buildparameters']['energy']
        if energy is not None:
            self.Energy.setText("%.3f" % energy)
        else:
            self.Energy.setText("")
        self.showElement(self.element + 1)

    def setInfoProvider(self, provider):
        self.infoProvider = provider

    def restore(self, settings):
        self._settings = settings

        self._settings.beginGroup("Elements")
        self.move(self._settings.value("pos", QtCore.QPoint(0, 0)))
        self.resize(self._settings.value("size", QtCore.QSize(0, 0)))
        self._settings.endGroup()

    def closeEvent(self, event):
        event.accept()

        if not self._settings:
            return

        self._settings.beginGroup("Elements")
        self._settings.setValue("pos",  self.pos())
        self._settings.setValue("size", self.size())

        self._settings.beginGroup("Info")
        self._settings.setValue("pos",  self.DetailedElementInfo.pos())
        self._settings.setValue("size", self.DetailedElementInfo.size())

        self._settings.endGroup()
        self._settings.endGroup()

        self.DetailedElementInfo.close()

    def showElement(self, element):
        self.DetailedElementInfo.show()
        self.element = element - 1

        #self._settings.beginGroup("Elements")
        #self._settings.beginGroup("Info")
        #self.DetailedElementInfo.move(self._settings.value("pos", QtCore.QPoint(0, 0)))
        #self.DetailedElementInfo.resize(self._settings.value("size", QtCore.QSize(0, 0)))
        #self._settings.endGroup()
        #self._settings.endGroup()

        self.ElementInfo.clear()
        
        if self.infoProvider:
            self.ElementInfo.insertHtml(self.infoProvider.gethtml(Elements[self.element][0]))
        
@ui_class
class ElementInfo(QtGui.QFrame):
    def __init__(self, parent = None):
        QtGui.QFrame.__init__(self, parent)
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)

    def populate(self, element):
        element -= 1
        self.Number.setText("%s" % Elements[element][1])
        self.Name.setText("%s" % (Elements[element][2]))
        self.Atom.setText("%s" % (Elements[element][0]))
        self.Mass.setText("%.0f" % (Elements[element][3]))
        self.Density.setText("%.2f g/l" % (Elements[element][4]))

@ui_class
class ElementButton(QtGui.QPushButton):
    def __init__(self, parent = None):
        QtGui.QPushButton.__init__(self, parent)
        # self.info = ElementInfo()
                
    def keyPressEvent(self, event):
        self.parent().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() != QtCore.Qt.LeftButton:
            QtGui.QPushButton.mousePressEvent(self, event)
            return
        event.accept()

        element = int(self.objectName().split('_')[-1])
        self.parent().showElement(element)

    def enterEvent(self, event):
        event.accept()

        element = self.objectName().split('_')[-1]
        if not Qt.isPySide or not hasattr(self, 'info'):
            self.info = Qt.loadUI(':/forms/elementInfo.ui')

        pos = event.screenPos() + QtCore.QPoint(50, 0)
        self.info.populate(int(element))
        self.info.move(pos)
        self.info.show()
        
    def mouseMoveEvent(self, event):
        event.accept()
        pos = self.mapToGlobal(event.pos() + QtCore.QPoint(15, -50))
        self.info.move(pos)

    def leaveEvent(self, event):
        event.accept()

        self.info.hide()
        if not Qt.isPySide:
            self.info.deleteLater()
            self.info = None
