"""
@description Fadeout region at cursor on selected track
@about
  This is a single action that inserts an automation item at the final 25% of a region.
  [More information](https://86thumbs.mooo.com/waldek/reapack_cosounders/src/branch/master/region_fadeout)
@version 0.1
@author Wouter Gordts
@provides
    [nomain] ./lib_region_fadeout.py > lib_region_fadeout.py
"""

from reaper_python import *
from lib_region_fadeout import fadeout_region_at_cursor

if __name__ == "__main__":
    RPR_Undo_BeginBlock()
    fadeout_region_at_cursor()
    RPR_Undo_EndBlock("region fadeout", 0)
