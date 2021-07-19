"""
@description fade selected clips in/out
@version 0.1
@author Wouter Gordts
"""

from reaper_python import *


ACTIVE_PROJECT = 0
FADE_LENGHT = 0.04


def get_all_selected_items():
    count = RPR_CountSelectedMediaItems(ACTIVE_PROJECT)
    items = []
    if count != 0:
        for i in range(0, count):
            item = RPR_GetSelectedMediaItem(0, i)
            items.append(item)
    return items


def apply_fade_to_items(items, fade_lenght):
    for item in items:
        RPR_SetMediaItemInfo_Value(item, "D_FADEINLEN", fade_lenght)
        RPR_SetMediaItemInfo_Value(item, "D_FADEOUTLEN", fade_lenght)


def fade_selected_clips():
    items = get_all_selected_items()
    apply_fade_to_items(items, FADE_LENGHT)
    RPR_UpdateArrange()


if __name__ == "__main__":
    RPR_Undo_BeginBlock()
    fade_selected_clips()
    RPR_Undo_EndBlock("region fadeout", 0)
