"""
@description Clear track or item envelopes
@about
  This is a single action that clear the envelopes of selected tracks or items.
  [More information](https://86thumbs.mooo.com/waldek/reapack_cosounders/src/branch/master/envelopes)
@version 0.1.1
@author Wouter Gordts
"""

from reaper_python import *

PROJ = 0
IGNORE_TIME_SELECTION = True

class ProjectTime(object):
    def __init__(self, project=PROJ):
        self.project = project
        self._start = 0.0
        self._end = RPR_GetProjectLength(self.project)
        self._inpoint = None
        self._outpoint = None
        self._get_time_selection()

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    def _get_time_selection(self):
        status = RPR_GetSet_LoopTimeRange2(self.project, False, False, 0.0, 0.0, False)
        inpoint = status[3]
        outpoint = status[4]
        if outpoint > 0.0:
            self._inpoint = inpoint
            self._outpoint = outpoint

    def has_time_selection(self):
        if self._outpoint is None or IGNORE_TIME_SELECTION:
            return False
        return True

    def get_time_tuple(self):
        if IGNORE_TIME_SELECTION:
            return self._start, self._end
        elif self.has_time_selection():
            return self._inpoint, self._outpoint
        else:
            return self._start, self._end


def _get_selected_items():
    items = []
    item_count = RPR_CountSelectedMediaItems(PROJ)
    for idx in range(0, item_count):
        item = RPR_GetSelectedMediaItem(PROJ, idx)
        items.append(item)
    return items

def _remove_all_envelopes_from_item(item, project):
    inpoint = project.start
    outpoint = project.end
    take_count = RPR_CountTakes(item)
    for take in range(0, take_count):
        take = RPR_GetMediaItemTake(item, take)
        env_count = RPR_CountTakeEnvelopes(take)
        for env in range(0, env_count):
            env = RPR_GetTakeEnvelope(take, env)
            RPR_DeleteEnvelopePointRange(env, inpoint, outpoint)

def _get_selected_tracks():
    track_count = RPR_CountSelectedTracks2(0, True)
    tracks = []
    for track in range(0, track_count):
        track = RPR_GetSelectedTrack(0, track)
        tracks.append(track)
    return tracks

def _remove_all_envelopes_from_track(track, project):
    count = RPR_CountTrackEnvelopes(track)
    if count == 0:
        return False
    for idx in range(0, count):
        env = RPR_GetTrackEnvelope(track, idx)
        inpoint, outpoint = project.get_time_tuple()
        if not project.has_time_selection():
            points = RPR_CountEnvelopePoints(env)
            last_point = points - 1
            point = RPR_GetEnvelopePoint(env, points - 1, 0, 0, 0, 0, 0)
            outpoint = point[3] + 100
        status = RPR_DeleteEnvelopePointRangeEx(env, -1, inpoint, outpoint)

def main():
    items = _get_selected_items()
    project = ProjectTime()
    if len(items) > 0:
        for item in items:
            _remove_all_envelopes_from_item(item, project)
    tracks = _get_selected_tracks()
    if len(tracks) > 0:
        for track in tracks:
            _remove_all_envelopes_from_track(track, project)
    
main()
RPR_UpdateArrange()
