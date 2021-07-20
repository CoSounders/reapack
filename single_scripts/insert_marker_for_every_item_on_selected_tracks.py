"""
@description insert marker for every item on selected tracks
@about 
    TODO
@version 0.2
@author Wouter Gordts
"""

from reaper_python import *

ACTIVE_PROJ = 0
NAME = ""

def add_unique_markers_for_all_items_on_selected_tracks():
    RPR_Main_OnCommandEx(40421, 0, ACTIVE_PROJ)
    count = RPR_CountSelectedMediaItems(ACTIVE_PROJ)
    items = {}
    for i in range(0, count):
        item = RPR_GetSelectedMediaItem(ACTIVE_PROJ, i)
        pos = RPR_GetMediaItemInfo_Value(item, "D_POSITION")
        items[pos] = item
    for pos in sorted(items.keys()):
        item = items[pos]
        color = RPR_ColorToNative(173,216,230)
        RPR_AddProjectMarker2(ACTIVE_PROJ, False, pos, 0, NAME, -1, color|0x1000000)


if __name__ == "__main__":
    RPR_Undo_BeginBlock()
    add_unique_markers_for_all_items_on_selected_tracks()
    RPR_Undo_EndBlock("undo insert markers", 0)
