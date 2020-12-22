"""
@noindex
"""

from reaper_python import *
from lib_track_visibility import *

ALL_TRACKS_COUNT = RPR_CountTracks(ACTIVE_PROJ)

def _get_tracks_from_ext_state():
    status, proj, extname, key, value, value_length = RPR_GetProjExtState(ACTIVE_PROJ, OWNER, GUID_KEY, "", BUF_SIZE)
    guids = value.split()
    selected_tracks = [RPR_GetTrack(ACTIVE_PROJ, idx) for idx in range(0, ALL_TRACKS_COUNT) if RPR_GetTrackGUID(RPR_GetTrack(ACTIVE_PROJ, idx)) in guids]
    other_tracks = [RPR_GetTrack(ACTIVE_PROJ, idx) for idx in range(0, ALL_TRACKS_COUNT) if RPR_GetTrackGUID(RPR_GetTrack(ACTIVE_PROJ, idx)) not in guids]
    return selected_tracks, other_tracks

def _get_tracks_to_never_hide_from_ext_state():
    status, proj, extname, key, value, value_length = RPR_GetProjExtState(ACTIVE_PROJ, OWNER, NEVER_HIDE_GUID_KEY, "", BUF_SIZE)
    guids = value.split()
    selected_tracks = [RPR_GetTrack(ACTIVE_PROJ, idx) for idx in range(0, ALL_TRACKS_COUNT) if RPR_GetTrackGUID(RPR_GetTrack(ACTIVE_PROJ, idx)) in guids]
    return selected_tracks
 
def _toggle_focus_ext_state():
    status, proj, extname, key, value, value_length = RPR_GetProjExtState(ACTIVE_PROJ, OWNER, TOGGLE_KEY, "", BUF_SIZE)
    try:
        value = int(value)
    except:
        value = 0
    RPR_SetProjExtState(ACTIVE_PROJ, OWNER, TOGGLE_KEY, "{}".format(1 - value))
    return value


if __name__ == "__main__":
    TOGGLE_STATE = _toggle_focus_ext_state()
    SELECTED_TRACKS, OTHER_TRACKS = _get_tracks_from_ext_state()
    NEVER_HIDE_TRACKS = _get_tracks_to_never_hide_from_ext_state()
    
    for track in SELECTED_TRACKS:
      status = RPR_GetMediaTrackInfo_Value(track, "B_SHOWINTCP")
      RPR_SetMediaTrackInfo_Value(track, "B_SHOWINTCP", 1)
    
    for track in OTHER_TRACKS:
      status = RPR_GetMediaTrackInfo_Value(track, "B_SHOWINTCP")
      RPR_SetMediaTrackInfo_Value(track, "B_SHOWINTCP", TOGGLE_STATE)

    for track in NEVER_HIDE_TRACKS:
      status = RPR_GetMediaTrackInfo_Value(track, "B_SHOWINTCP")
      RPR_SetMediaTrackInfo_Value(track, "B_SHOWINTCP", 1)
    
    RPR_TrackList_AdjustWindows(True)
    RPR_UpdateArrange()
    
