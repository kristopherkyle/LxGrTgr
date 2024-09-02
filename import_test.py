from importlib_resources import files #add to required dependencies

l1 = files('lists_LGR').joinpath('phrasalVerbList.txt').read_text().strip().split("\n")
l1[:25]

import LxGrTgr_05_28 as lxgr
import LxGrTgr_05_27 as lxgr
import LxGrTgr_05_26 as lxgr