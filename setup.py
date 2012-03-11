#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# Copyrighted 2011 - 2012 Mattias Ekholm <code@ekholm.se>

import distutils.core 
import glob

try:
    import PySide
    
except ImportError:
    raise ImportError, "You must have PySide installed"

scripts = []
data_files = [ 
    ('PyQtAbstractions', glob.glob('src/*'))
    ]
 
distutils.core.setup(
    name="PyQtAbstractions",
    version      = "1.0",
    author       = "Mattias Ekholm",
    author_email = "code@ekholm.se",
    url          = "http://www.ekholm.se/code/",
    
    license  = "GPL v2 with restriction rights reserved",
    
    description      = "PyQtAbstractions software package",
    long_description = "PyQtAbstractions software package",
    
    packages  = ['PyQtAbstractions'],
    
    platforms = "any",
    
    scripts     = scripts,
    data_files  = data_files,
    )
