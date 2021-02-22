"""
@description batch import of a folder with assets
@about 
  This is a single action that clear the envelopes of selected tracks or items.
  [More information](https://86thumbs.mooo.com/waldek/reapack_cosounders/src/branch/master/envelopes)
@version 0.1
@author Wouter Gordts
"""

from reaper_python import *
import pathlib

def _get_source_folder():
    filename = str()
    title = "Paste the path to the source directory"
    num_inputs = 1
    captions_csv = "paste path to asset directory:, extrawidth=400"
    retvals_csv = str()
    retvals_csv_sz = 4096
    retval, title, num_inputs, captions_csv, retvals_csv, retvals_csv_sz = RPR_GetUserInputs(title, num_inputs, captions_csv, retvals_csv, retvals_csv_sz)
    if retval:
        try:
            #retvals_csv = "/home/waldek/Downloads/demute_hirez/Fenrir (Dog Armor) - PICKED/Fenrir (Dog Armor)"
            path = pathlib.Path(retvals_csv)
            if path.exists():
                return path
            else:
                RPR_ShowConsoleMsg("Not a valid path!")
                return False
        except:
            return False
    else:
        return False

def _get_all_audio_files_from_folder(folderpath):
    all_audio_files = []
    for path in folderpath.glob('**/*.wav'):
        data = (path, path.relative_to(folderpath))
        all_audio_files.append(data)
    return all_audio_files

def _prepare_session():
    tracks = []
    for name in ("processed", "unprocessed"):
        RPR_InsertTrackAtIndex(0, True)
        track = RPR_GetTrack(0, 0)
        parmname = "P_NAME"
        value = name
        retval, tr, parmname, value, setNewValue = RPR_GetSetMediaTrackInfo_String(track, parmname, value, True)
        tracks.append(track)
    RPR_CreateTrackSend(tracks[1], tracks[0])
    RPR_Main_OnCommand(0, 40297)
    RPR_SetTrackSelected(track, True)

def _import_audiofile_into_session(filepath, regionname):
    RPR_InsertMedia(str(filepath), 0)
    cursor = RPR_GetCursorPosition()
    track = RPR_GetTrack(0, 0)
    count = RPR_CountTrackMediaItems(track)
    item = RPR_GetMediaItem(0, count - 1)
    position = RPR_GetMediaItemInfo_Value(item, "D_POSITION")
    length = RPR_GetMediaItemInfo_Value(item, "D_LENGTH")
    end = position + length
    RPR_AddProjectMarker2(0, True, position, end, str(regionname).strip(".wav"), 0, 0)
    RPR_MoveEditCursor(2, False)

def _normalize_and_lower_volume():
    RPR_Main_OnCommand(40289, 0) # unselect all items
    RPR_Main_OnCommand(40182, 0) # select all items
    RPR_Main_OnCommand(40108, 0) # normalize selected items
    for i in range(0, 3):
        RPR_Main_OnCommand(41924, 0) # nudge item volume -1db


if __name__ == "__main__":
    PATH = _get_source_folder()
    if PATH is not False:
        ALL_AUDIO_FILES = _get_all_audio_files_from_folder(PATH)
        RPR_Undo_BeginBlock()
        _prepare_session()
        for filepath, regionname in ALL_AUDIO_FILES:
            _import_audiofile_into_session(filepath, regionname)
        _normalize_and_lower_volume()
        RPR_Undo_EndBlock(0, 0)
        RPR_UpdateArrange()
