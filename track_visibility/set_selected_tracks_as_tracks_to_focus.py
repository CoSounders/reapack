"""
@noindex
"""

from reaper_python import *
from lib_track_visibility import *

TRACK_COUNT = RPR_CountSelectedTracks2(ACTIVE_PROJ, False)
TRACKS = [RPR_GetTrackGUID(RPR_GetSelectedTrack(ACTIVE_PROJ, idx)) for idx in range(0, TRACK_COUNT)]
DATA = " ".join(TRACKS)
RPR_SetProjExtState(ACTIVE_PROJ, OWNER, GUID_KEY, DATA)
RPR_SetProjExtState(ACTIVE_PROJ, OWNER, TOGGLE_KEY, "0")

