from reaper_python import *
from lib_clean_session import main
import pathlib

AAT_MATCH = "-AAT.rpp"
VIDEO_SRC_EXT = "mp4"
VIDEO_TRACK_NAME = "#!VIDEO"
SOURCE_TRACK_NAME = "#!SOURCE"
ACTIVE_PROJECT = 0

path = pathlib.Path("/home/waldek/bin/python/demute_auto_session/tests/playground")
path = pathlib.Path("/home/waldek/bin/python/demute_auto_session/tests/")
files_glob = path.glob("*{}".format(AAT_MATCH))
files = []
for file in files_glob:
    files.append(file)


def _find_video_file(rpp_file):
    videofile = pathlib.Path(
            rpp_file.parent,
            rpp_file.name.replace(AAT_MATCH, ".") + VIDEO_SRC_EXT
            )
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
    pointer, rel_id, path, length = RPR_EnumProjects(-1, "", 4000)
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
    RPR_Main_OnCommandEx(40886, 0, 0) # close all projects
    proj_data = _create_main_session(path)
    all_projects["main"] = proj_data
    for rpp_file in files:
        RPR_Main_OnCommandEx(40859, 0, 0) # new project tab
        RPR_Main_openProject(str(rpp_file))
        proj_data = _get_data_struct_of_project()
        # _put_tracks_in_bus(SOURCE_TRACK_NAME)
        videofile = _find_video_file(rpp_file)
        _add_video(videofile)
        proj_data["videofile"] = videofile
        all_projects[rpp_file] = proj_data
        # RPR_Main_SaveProject(pointer, False)
    return all_projects


def _test(files):
    all_projects = {}
    counter = 0
    for idx in range(-1, len(files)):
        pointer, rel_id, path, length = RPR_EnumProjects(idx, "", 4000)
        path = pathlib.Path(path)
        videofile = pathlib.Path(path.parent, path.name.replace(
            AAT_MATCH, ".") + VIDEO_SRC_EXT)
        project = {
            "pointer": pointer,
            "rel_id": counter,
            "path": str(path),
            "length": length,
            "videofile": videofile,
        }
        all_projects[path] = project
        counter += 1
    return all_projects

def _get_main_length():
    seconds = RPR_GetProjectLength(MAIN["pointer"])
    return seconds

def get_track_by_name_from_main(trackname):
    """unused"""
    RPR_SelectProjectInstance(main)
    track_count = RPR_CountTracks(0)
    for idx in range(ACTIVE_PROJECT, track_count):
        track = RPR_GetTrack(ACTIVE_PROJECT, idx)
        track_name = RPR_GetTrackName(track, "", 1000)
        if track_name == trackname:
            return track
    RPR_InsertTrackAtIndex(track_count, False)
    track = RPR_GetTrack(ACTIVE_PROJECT, track_count)
    RPR_GetSetMediaTrackInfo_String(track, "P_NAME", trackname, True)
    return track


def _move_all_items_by(seconds):
    item_count = RPR_CountMediaItems(ACTIVE_PROJECT)
    items = []
    for idx in range(0, item_count): # extra loop because pointers change!
        item = RPR_GetMediaItem(ACTIVE_PROJECT, idx)
        items.append(item)
    for item in items:
        position = RPR_GetMediaItemInfo_Value(item, "D_POSITION")
        position_with_offset = position + seconds
        RPR_SetMediaItemInfo_Value(item, "D_POSITION", position_with_offset)
        #print(from_project, position, position + seconds)
        #RPR_SetMediaItemPosition(item, position + seconds, False)

def _move_all_tracks_to_main_project(project):
    RPR_Main_OnCommand(40296, 0) # select all tracks
    RPR_Main_OnCommand(40210, 0) # copy all tracks
    RPR_SelectProjectInstance(MAIN["pointer"])
    RPR_Main_OnCommand(42398, 0) # paste all tracks

def _calculate_offset():
    offset = 60
    seconds = _get_main_length()
    if seconds == 0:
        return seconds
    seconds = int((seconds / offset) + 1) * offset
    return seconds


all_projects = _load_files(files)
print("hello world")
MAIN = all_projects["main"]
for key, value in all_projects.items():
    if key == "main":
        continue
    seconds = _calculate_offset()
    RPR_SelectProjectInstance(value["pointer"])
    _move_all_items_by(seconds)
    RPR_SelectProjectInstance(value["pointer"])
    _move_all_tracks_to_main_project(value["pointer"])
    RPR_SelectProjectInstance(value["pointer"])


RPR_SelectProjectInstance(MAIN["pointer"])
main()
RPR_UpdateArrange()



def unused():
    proj1 = RPR_EnumProjects(0, "", 100)
    proj2 = RPR_EnumProjects(1, "", 100)
    print(proj1)
    print(proj2)
    seconds1 = RPR_GetProjectLength(proj1[0])
    seconds2 = RPR_GetProjectLength(proj2[0])
    RPR_SelectProjectInstance(proj2[0])
    print(seconds1, seconds2)
    _move_all_items_by(seconds2, proj2[0])
    for key, value in all_projects.items():
        if key.name == "consolidate.RPP":
            continue
        proj_pointer = value["pointer"]
        track_count = RPR_CountTracks(proj_pointer)
        RPR_SelectProjectInstance(proj_pointer)
        for idx in range(0, track_count):
            track = RPR_GetTrack(0, idx)
            status = RPR_GetTrackStateChunk(track, "", 400000, False)
            print(status)
    
            track_name = RPR_GetTrackName(track, "", 99)[2]
            print(track_name)
            print(get_track_by_name_from_main(track_name))
        # print(track_count)
        # RPR_MoveMediaItemToTrack(MediaItem item, MediaTrack desttr)
