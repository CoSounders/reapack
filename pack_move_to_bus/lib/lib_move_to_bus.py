from reaper_python import *
from logging import root

LOGGER = root

def get_item_range_alt(item):
    position = float(RPR_GetMediaItemInfo_Value(item, "D_POSITION"))
    length = float(RPR_GetMediaItemInfo_Value(item, "D_LENGTH"))
    limit = (position, position + length)
    return limit


def get_item_range(item):
    position = int(RPR_GetMediaItemInfo_Value(item, "D_POSITION") * 100)
    length = int(RPR_GetMediaItemInfo_Value(item, "D_LENGTH") * 100)
    limit = set(range(position, position + length))
    return limit

class ReaperTrack(object):
    NAME = "TEST"

    @staticmethod
    def get_track_by_name(name):
        count = RPR_GetNumTracks()
        bus = None
        for idx in range(0, count):
            track = RPR_GetTrack(0, idx)
            status, mediatrack, trackname, size = RPR_GetTrackName(
                track, "", 100)
            if trackname == name:
                bus = ReaperTrack(idx, track, trackname)
                return bus
        if bus is None:
            RPR_InsertTrackAtIndex(0, True)
            track = RPR_GetTrack(0, 0)
            RPR_GetSetMediaTrackInfo_String(track, "P_NAME", ReaperTrack.NAME, True)
            bus = ReaperTrack.get_track_by_name(ReaperTrack.NAME)
            return bus

    def __init__(self, idx, track, name="_tmp"):
        self.logger = LOGGER.getChild(self.__class__.__name__)
        self.idx = idx
        self.track = track
        self.name = self._get_name_by_index(idx)

    @property
    def children(self):
        return self.get_children()

    def _get_name_by_index(self, idx):
        track = RPR_GetTrack(0, idx)
        status, mediatrack, trackname, size = RPR_GetTrackName(track, "", 100)
        return trackname

    def __str__(self):
        return "{}".format(self.name)

    def is_parent(self):
        value = int(RPR_GetMediaTrackInfo_Value(self.track, "I_FOLDERDEPTH"))
        self.logger.debug(value)
        if value == 1:
            return True
        elif value <= 0:
            return False

    def get_children(self):
        idx = self.idx + 1
        children = []
        while True:
            track = RPR_GetTrack(0, idx)
            value = int(RPR_GetMediaTrackInfo_Value(track, "I_FOLDERDEPTH"))
            child = ReaperTrack(idx, RPR_GetTrack(0, idx))
            children.append(child)
            if value < 0:
                break
            idx += 1
        return children

    def _make_folder(self):
        RPR_SetMediaTrackInfo_Value(self.track, "I_FOLDERDEPTH", 1)
        idx = self.idx + 1
        RPR_InsertTrackAtIndex(idx, True)
        track = RPR_GetTrack(0, idx)
        RPR_SetMediaTrackInfo_Value(track, "I_FOLDERDEPTH", -1)
        name = "{} {}".format(self.name, len(self.get_children()))
        RPR_GetSetMediaTrackInfo_String(track, "P_NAME", name, True)
        self._move_inside_folder(track)

    def _move_inside_folder(self, track):
        self.logger.debug("moving items to folder")
        count = RPR_CountTrackMediaItems(self.track)
        for item in range(0, count):
            item = RPR_GetTrackMediaItem(self.track, item)
            RPR_MoveMediaItemToTrack(track, item)

    def _add_child(self):
        children = self.get_children()
        name = "{} {}".format(self.name, len(children) + 1)
        idx = self.idx + 1 #len(children) 
        RPR_InsertTrackAtIndex(idx, True)
        track = RPR_GetTrack(0, idx)
        RPR_GetSetMediaTrackInfo_String(track, "P_NAME", name, True)
        child = ReaperTrack(idx, RPR_GetTrack(0, idx))
        return child

    def _get_track_limits(self):
        track_limits = []
        count = RPR_CountTrackMediaItems(self.track)
        for item in range(0, count):
            item = RPR_GetTrackMediaItem(self.track, item)
            limit = get_item_range(item)
            track_limits.append(limit)
        return track_limits

    def _is_free(self, item):
        limits = self._get_track_limits()
        item_limit = get_item_range(item)
        intersections = []
        for limit in limits:
            intersection = limit.intersection(item_limit)
            if len(intersection) != 0:
                intersections.append(intersection)
                break
        if len(intersections) == 0:
            status = True
        else:
            status = False
        self.logger.debug("{} {}".format(self, status))
        return status

    def tester(self, item):
        self.logger.debug("testing...")
        status = self._is_free(item)
        if status:
            self.do_move(item, self)
            return True
        status = self.is_parent()
        if not status:
            self._make_folder()
        children = self.get_children()
        for child in children:
            status = child._is_free(item)
            if status:
                self.do_move(item, child)
                return True
        child = self._add_child()
        self.do_move(item, child)
        return True

    def do_move(self, item, track, move=False):
        if move:
            self.logger.debug("moving {} {}".format(item, track))
            RPR_MoveMediaItemToTrack(item, track.track)
            color = RPR_ColorToNative(0, 255, 0) | 0x01000000
            RPR_SetMediaItemInfo_Value(item, "I_CUSTOMCOLOR", color)
            return
        new_item = RPR_AddMediaItemToTrack(track.track)
        status, original_item, chunk, size, undo = RPR_GetItemStateChunk(item, "", 1000, True)
        position = RPR_GetMediaItemInfo_Value(item, "D_POSITION")

        status = RPR_SetMediaItemInfo_Value(new_item, "D_POSITION", position)
        status = RPR_GetSetMediaItemInfo_String(new_item, "GUID", "", False)
        guid = status[3]

        RPR_SetItemStateChunk(new_item, chunk, True)
        status = RPR_GetSetMediaItemInfo_String(new_item, "GUID", guid, True)
        color = RPR_ColorToNative(0, 255, 0) | 0x01000000
        RPR_SetMediaItemInfo_Value(item, "I_CUSTOMCOLOR", color)
        RPR_SetMediaItemInfo_Value(item, "B_MUTE", True)
        status, original_item, chunk, size, undo = RPR_GetItemStateChunk(new_item, "", 1000, True)
        self.logger.debug("moving {} {}".format(item, track))
