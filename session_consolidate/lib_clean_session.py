from reaper_python import *

BUFFERSIZE = 4096
VIDEO_TRACK_NAME = "#!VIDEO"

def _get_session_map():
    track_count = RPR_CountTracks(0)
    tracks = []
    for idx in range(0, track_count):
        track = RPR_GetTrack(0, idx)
        tracks.append(track)
    tracks_map = {}
    for track in tracks:
        status, track, name, size = RPR_GetTrackName(track, "", BUFFERSIZE)
        if name not in tracks_map.keys():
            tracks_map[name] = [track]
        else:
            tracks_map[name].append(track)
    return tracks_map

def _merge_tracks(session_map):
    for key, value in session_map.items():
        merge_track = value[0]
        for track in value[1:]:
            item_count = RPR_CountTrackMediaItems(track)
            items = [RPR_GetTrackMediaItem(track, idx) for idx in range(0, item_count)]
            print(items)
            for item in items:
                RPR_MoveMediaItemToTrack(item, merge_track)

def _clean_empty_tracks():
    track_count = RPR_CountTracks(0)
    tracks = [RPR_GetTrack(0, idx) for idx in range(0, track_count)]
    for track in tracks:
        if RPR_CountTrackMediaItems(track) == 0:
            RPR_DeleteTrack(track)

def _add_video_markers():
    track_count = RPR_CountTracks(0)
    tracks = [RPR_GetTrack(0, idx) for idx in range(0, track_count)]
    for track in tracks:
        status, track, name, size = RPR_GetTrackName(track, "", BUFFERSIZE)
        if name == VIDEO_TRACK_NAME:
            videotrack = track
            break
    item_count = RPR_CountTrackMediaItems(track)
    items = [RPR_GetTrackMediaItem(track, idx) for idx in range(0, item_count)]
    for item in items:
        start = RPR_GetMediaItemInfo_Value(item, "D_POSITION")
        end = start + RPR_GetMediaItemInfo_Value(item, "D_LENGTH")
        take = RPR_GetMediaItemTake(item, 0)
        name = RPR_GetTakeName(take)
        RPR_AddProjectMarker2(0, True, start, end, name, False, 0)

def main():
    session_map = _get_session_map()
    _merge_tracks(session_map)
    _clean_empty_tracks()
    _add_video_markers()


if __name__ == "__main__":
    main()
    RPR_UpdateArrange()
