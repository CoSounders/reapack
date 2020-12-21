"""
@noindex true
"""
from reaper_python import *

ACTIVE_PROJ = 0
CURSOR_POS = RPR_GetCursorPositionEx(ACTIVE_PROJ)
UNITY_VOL = 716.2178503126559
BLANK = 0.1
PERCENT = 0.25

def _get_all_markers_and_regions():
    num_regions = 0
    num_markers = 0
    status, proj, num_markers, num_regions = RPR_CountProjectMarkers(ACTIVE_PROJ, num_markers, num_regions)
    all_data = []
    all_regions = []
    for i in range(0, num_regions + num_markers):
        isrgnOut = False
        posOut = 0.0
        rgnendOut = 0.0
        nameOut = ""
        markrgnindexnumberOut = 10
        colorOut = 10
        result = RPR_EnumProjectMarkers3(ACTIVE_PROJ, i, isrgnOut, posOut, rgnendOut, nameOut, markrgnindexnumberOut, colorOut)
        all_data.append(result)
    all_markers = [result for result in all_data if result[3] is 0]
    all_regions = [result for result in all_data if result[3] is 1]
    return all_markers, all_regions

def _get_region_surrounding_cursor():
    marker, regions = _get_all_markers_and_regions()
    for region in regions:
        start = region[4]
        end = region[5]
        if CURSOR_POS >= start and CURSOR_POS <= end:
            return region
    return None

def _insert_automation_item(env, region):
    pool_id = RPR_CountAutomationItems(env)
    region_start = region[4]
    region_end = region[5]
    region_length = region[5] - region[4]
    auto_length = region_length * PERCENT
    auto_position = region_start + region_length - auto_length
    idx = RPR_InsertAutomationItem(env, pool_id, auto_position, auto_length)
    auto_start = auto_position
    auto_end = auto_start + auto_length - BLANK
    auto_end_1 = auto_start + auto_length
    RPR_InsertEnvelopePointEx(env, idx, auto_start, UNITY_VOL, 0, 0.5, False, True)
    RPR_InsertEnvelopePointEx(env, idx, auto_end, 0, 1, 0.0, False, True)
    RPR_InsertEnvelopePointEx(env, idx, auto_end_1, UNITY_VOL, 1, 0.0, False, True)
    RPR_Envelope_SortPointsEx(env, idx)

def _get_first_selected_track_volume_envelope():
    track_count = RPR_CountSelectedTracks(ACTIVE_PROJ)
    if track_count != 0:
        track = RPR_GetSelectedTrack(ACTIVE_PROJ, 0)
        RPR_Main_OnCommandEx(40297, 0, ACTIVE_PROJ) # unselect all tracks
        RPR_SetTrackSelected(track, True)
        RPR_Main_OnCommandEx(41866, 0, ACTIVE_PROJ) # show volume of selected tracks
        vol_env = RPR_GetTrackEnvelopeByName(track, "Volume")
        return vol_env
    return None

def fadeout_region_at_cursor():
    vol_env = _get_first_selected_track_volume_envelope()
    if vol_env is None:
        return False
    region = _get_region_surrounding_cursor()
    if region is None:
        return False
    _insert_automation_item(vol_env, region)

def fadeout_all_project_regions():
    vol_env = _get_first_selected_track_volume_envelope()
    if vol_env is None:
        return False
    marker, regions = _get_all_markers_and_regions()
    for region in regions:
        _insert_automation_item(vol_env, region)

def tester():
    print("goooo")
    track_count = RPR_GetNumTracks()
    track = RPR_GetSelectedTrack(ACTIVE_PROJ, 0)
    idx = int(RPR_GetMediaTrackInfo_Value(track, "IP_TRACKNUMBER"))
    for i in range(idx, track_count):
        track = RPR_GetTrack(ACTIVE_PROJ, i)
        result = RPR_GetMediaTrackInfo_Value(track, "I_FOLDERDEPTH")
        if result < 0:
            break
    print(result)
    track = RPR_GetSelectedTrack(ACTIVE_PROJ, 0)
    parent = RPR_GetParentTrack(track)
    RPR_Main_OnCommandEx(40297, 0, ACTIVE_PROJ) # unselect all tracks
    RPR_SetTrackSelected(parent, True)

