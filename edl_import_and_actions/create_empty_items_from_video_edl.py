"""
@noindex true
"""

from reaper_python import *
from lib_edl import EDL
import pathlib
import logging

ACTIVE_PROJ = 0
FPS = str(29.97)
BUF_SZ = 4096
CUT_TRACK_NAME = "#!VIDEOCUTS"

def _get_selected_video_fps():
    """TODO make it actually work"""
    item = RPR_GetSelectedMediaItem(ACTIVE_PROJ, 0)
    take = RPR_GetMediaItemTake(item, 0)
    source = RPR_GetMediaItemTake_Source(take)
    source, filename, buf_sz = RPR_GetMediaSourceFileName(source, "", BUF_SZ)
    return FPS

def _get_selected_video_position():
    item = RPR_GetSelectedMediaItem(ACTIVE_PROJ, 0)
    pos = RPR_GetMediaItemInfo_Value(item, "D_POSITION")
    return pos

def _ask_for_edl_file():
    retval, filename, title, defext = RPR_GetUserFileNameForRead("", "open EDL file", "edl")
    filepath = pathlib.Path(filename)
    # filename = "/home/waldek/Downloads/EXPORT_EDL_1.edl"
    edl = EDL()
    edl.load_from_edl_file(filepath)
    # edl.fps = _get_selected_video_fps()
    edl.offset = _get_selected_video_position()
    return edl

def _ask_for_fps():
    status = RPR_GetUserInputs("import EDL settings", 1, "source video fps", "", BUF_SZ)
    retval, title, num_inputs, captions_csv, retvals_csv, retvals_csv_sz = status
    return retvals_csv

def _insert_empty_item(start, end, offset=0):
    position = start + offset
    length = end - start
    item = RPR_AddMediaItemToTrack(_get_track_by_name(CUT_TRACK_NAME))
    RPR_SetMediaItemPosition(item, position, False)
    RPR_SetMediaItemLength(item, length, False)

def _get_track_by_name(name):
    count = RPR_GetNumTracks()
    bus = None
    for idx in range(0, count):
        track = RPR_GetTrack(0, idx)
        status, mediatrack, trackname, size = RPR_GetTrackName(
            track, "", 100)
        if trackname == name:
            return track
    if bus is None:
        RPR_InsertTrackAtIndex(0, True)
        track = RPR_GetTrack(0, 0)
        RPR_GetSetMediaTrackInfo_String(track, "P_NAME", name, True)
        return track

if __name__ == "__main__":
    edl = _ask_for_edl_file()
    edl.fps = _ask_for_fps()
    offset = _get_selected_video_position()
    for start, end in edl.get_start_and_end_times():
        _insert_empty_item(start, end, offset)
    RPR_UpdateArrange()


