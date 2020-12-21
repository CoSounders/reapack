"""
@description Fadeout all regions on selected track
@about
  This is a single action that inserts an automation item at the final 25% of a region for each region in the project.
  [More information](https://86thumbs.mooo.com/waldek/reapack_cosounders/src/branch/master/region_fadeout)
@version 0.1
@author Wouter Gordts
@provides
    [nomain] ./lib_region_fadeout.py > lib_region_fadeout.py
"""

from reaper_python import *
from lib_region_fadeout import fadeout_all_project_regions

if __name__ == "__main__":
    RPR_Undo_BeginBlock()
    fadeout_all_project_regions()
    RPR_Undo_EndBlock("region fadeout", 0)
