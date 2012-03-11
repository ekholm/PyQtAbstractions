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
    ('inka', glob.glob('src/*'))
    ]
 
distutils.core.setup(
    name="inka",
    version      = "1.0",
    author       = "Mattias Ekholm",
    author_email = "code@ekholm.se",
    url          = "http://www.ekholm.se/",
    
    license  = "All rights reserved",
    
    description      = "Inka software package",
    long_description = "Inka software package",
    
    packages  = ['inka'],
    
    platforms = "any",
    
    scripts     = scripts,
    data_files  = data_files,
    )
