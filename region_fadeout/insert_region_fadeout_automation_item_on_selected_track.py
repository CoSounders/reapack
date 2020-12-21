"""
@noindex true
"""

from reaper_python import *
from lib_region_fadeout import fadeout_region_at_cursor

if __name__ == "__main__":
    RPR_Undo_BeginBlock()
    fadeout_region_at_cursor()
    RPR_Undo_EndBlock("region fadeout", 0)
