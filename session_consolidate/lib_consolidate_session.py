import pathlib

from reaper_python import *

AAT_MATCH = "-AAT.rpp"
VIDEO_SRC_EXT = "mp4"
VIDEO_TRACK_NAME = "#!VIDEO"
SOURCE_TRACK_NAME = "#!SOURCE"
BUFFERSIZE = 4096
ACTIVE_PROJECT = 0


def _find_video_file(rpp_file):
    videofile = pathlib.Path(
        rpp_file.parent,
        rpp_file.name.replace(AAT_MATCH, ".") + VIDEO_SRC_EXT)

    return videofile


def _add_video(videofile):
    RPR_InsertTrackAtIndex(0, False)
    track = RPR_GetTrack(0, 0)
    RPR_GetSetMediaTrackInfo_String(track, "P_NAME", VIDEO_TRACK_NAME, True)
    RPR_SetOnlyTrackSelected(track)
    RPR_InsertMedia(str(videofile), 0)
    item = RPR_GetMediaItem(0, 0)
    RPR_SetMediaItemPosition(item, 0.0, False)


def _put_tracks_in_bus(busname):
    track_count = RPR_CountTracks(ACTIVE_PROJECT)
    RPR_InsertTrackAtIndex(0, False)
    bus = RPR_GetTrack(ACTIVE_PROJECT, 0)
    RPR_GetSetMediaTrackInfo_String(bus, "P_NAME", busname, True)
    RPR_SetMediaTrackInfo_Value(bus, "I_FOLDERDEPTH", 1)
    last_track = RPR_GetTrack(ACTIVE_PROJECT, track_count)
    RPR_SetMediaTrackInfo_Value(last_track, "I_FOLDERDEPTH", -1)


def _get_data_struct_of_project():
    pointer, rel_id, path, length = RPR_EnumProjects(-1, "", BUFFERSIZE)
    project = {
        "pointer": pointer,
        "rel_id": rel_id,
        "path": path,
        "length": length,
    }

    return project


def _create_main_session(path):
    RPR_Main_openProject(pathlib.Path(path, "consolidate.RPP"))
    proj_data = _get_data_struct_of_project()
    #RPR_Main_SaveProject(0, False)

    return proj_data


def _load_files(files):
    all_projects = {}
    RPR_Main_OnCommandEx(40886, 0, 0)  # close all projects
    proj_data = _create_main_session(path)
    all_projects["main"] = proj_data

    for rpp_file in files:
        RPR_Main_OnCommandEx(40859, 0, 0)  # new project tab
        RPR_Main_openProject(str(rpp_file))
        proj_data = _get_data_struct_of_project()
        # _put_tracks_in_bus(SOURCE_TRACK_NAME)
        videofile = _find_video_file(rpp_file)
        _add_video(videofile)
        proj_data["videofile"] = videofile
        all_projects[rpp_file] = proj_data
        # RPR_Main_SaveProject(pointer, False)

    return all_projects


def _get_main_length():
    seconds = RPR_GetProjectLength(MAIN["pointer"])

    return seconds


def _move_all_items_by(seconds):
    item_count = RPR_CountMediaItems(ACTIVE_PROJECT)
    items = [
        RPR_GetMediaItem(ACTIVE_PROJECT, idx) for idx in range(0, item_count)
    ]

    for item in items:
        position = RPR_GetMediaItemInfo_Value(item, "D_POSITION")
        position_with_offset = position + seconds
        RPR_SetMediaItemInfo_Value(item, "D_POSITION", position_with_offset)


def _move_all_tracks_to_main_project(project):
    RPR_Main_OnCommand(40296, 0)  # select all tracks
    RPR_Main_OnCommand(40210, 0)  # copy all tracks
    RPR_SelectProjectInstance(MAIN["pointer"])
    RPR_Main_OnCommand(42398, 0)  # paste all tracks


def _calculate_offset():
    offset = 60
    seconds = _get_main_length()

    if seconds == 0:
        return seconds
    seconds = int((seconds / offset) + 1) * offset

    return seconds


def _get_folder_path():
    title = "Input folder containing AATransator sessions"
    captions = "Path:,extrawidth=200"
    status, title, num, captions, results, size = RPR_GetUserInputs(
        title, 1, captions, "", BUFFERSIZE)

    if not status:
        return None
    path = pathlib.Path(results)

    return path


def _get_session_map():
    track_count = RPR_CountTracks(ACTIVE_PROJECT)
    tracks = [
        RPR_GetTrack(ACTIVE_PROJECT, idx) for idx in range(0, track_count)
    ]
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
            items = [
                RPR_GetTrackMediaItem(track, idx)
                for idx in range(0, item_count)
            ]
            print(items)

            for item in items:
                RPR_MoveMediaItemToTrack(item, merge_track)


def _clean_empty_tracks():
    track_count = RPR_CountTracks(ACTIVE_PROJECT)
    tracks = [
        RPR_GetTrack(ACTIVE_PROJECT, idx) for idx in range(0, track_count)
    ]

    for track in tracks:
        if RPR_CountTrackMediaItems(track) == 0:
            RPR_DeleteTrack(track)


def _add_video_markers():
    track_count = RPR_CountTracks(ACTIVE_PROJECT)
    tracks = [
        RPR_GetTrack(ACTIVE_PROJECT, idx) for idx in range(0, track_count)
    ]

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
        RPR_AddProjectMarker2(ACTIVE_PROJECT, True, start, end, name, False, 0)


def _clean_session():
    session_map = _get_session_map()
    _merge_tracks(session_map)
    _clean_empty_tracks()
    _add_video_markers()


if __name__ == "__main__":
    PATH = _get_folder_path()

    if PATH is not None:
        FILES_GLOB = PATH.glob("*{}".format(AAT_MATCH))
        FILES = []

        for filepath in FILES_GLOB:
            FILES.append(filepath)

        ALL_PROJECTS = _load_files(FILES)
        MAIN = all_projects["main"]

        for key, value in ALL_PROJECTS.items():
            if key == "main":
                continue
            seconds = _calculate_offset()
            RPR_SelectProjectInstance(value["pointer"])
            _move_all_items_by(seconds)
            RPR_SelectProjectInstance(value["pointer"])
            _move_all_tracks_to_main_project(value["pointer"])
            RPR_SelectProjectInstance(value["pointer"])

        RPR_SelectProjectInstance(MAIN["pointer"])
        _clean_session()
        RPR_UpdateArrange()
