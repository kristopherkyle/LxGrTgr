import os
from importlib_resources import files #add to required dependencies
os.chdir('/Users/kristopherkyle/Desktop/Programming/GitHub/LCR-ADS-Lab/LxGrTgr/python_package/src/lxgrtgr/')

nominal_stop = files('lists_LGR').joinpath('nom_stop_list_edited.txt').read_text().strip().split("\n")
l1[:25]

import LxGrTgr_05_28 as lxgr

lxgr.printer(lxgr.tag("They said they wanted to eat pizza.")) #nonfinite to- clause not tagged here [need to check]