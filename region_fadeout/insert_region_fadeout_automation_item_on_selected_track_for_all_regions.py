"""
@noindex true
"""

from reaper_python import *
from lib_region_fadeout import fadeout_all_project_regions

if __name__ == "__main__":
    RPR_Undo_BeginBlock()
    fadeout_all_project_regions()
    RPR_Undo_EndBlock("region fadeout", 0)
