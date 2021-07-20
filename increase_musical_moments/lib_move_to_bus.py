"""
@noindex true
"""

from reaper_python import *

from logging import root, Formatter, FileHandler, StreamHandler, INFO, DEBUG, ERROR, CRITICAL

LOGGER = root


def set_logging():
    FMT_STR = '%(asctime)s - %(levelname)s - %(name)s.%(funcName)s %(message)s'
    DATE_STR = '%Y-%m-%d %H:%M:%S'
    FMT = Formatter(FMT_STR, DATE_STR)
    # ST_HANDLER = StreamHandler(stdout)
    F_HANDLER = FileHandler('D:\\musical_moment.log')
    F_HANDLER.setFormatter(FMT)
    LOGGER.addHandler(F_HANDLER)
    LOGGER.setLevel(DEBUG)
    # LOGGER.setLevel(ERROR)



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
        self._make_track_a_parent()
        idx = self.idx + 1
        RPR_InsertTrackAtIndex(idx, True)
        track = RPR_GetTrack(0, idx)
        self._make_track_last_in_folder_hierarchy(track)
        name = "{} {}".format(self.name, len(self.get_children()))
        RPR_GetSetMediaTrackInfo_String(track, "P_NAME", name, True)
        self._move_inside_folder(track)

    def _make_track_last_in_folder_hierarchy(self,
                                             track):  # TODO: Change Implementation: apply to self and not the parameter
        RPR_SetMediaTrackInfo_Value(track, "I_FOLDERDEPTH", -1)

    def _make_track_a_parent(self):
        RPR_SetMediaTrackInfo_Value(self.track, "I_FOLDERDEPTH", 1)

    def _move_inside_folder(self, track):
        self.logger.debug("moving items to folder")
        count = RPR_CountTrackMediaItems(self.track)
        for item in range(0, count):
            item = RPR_GetTrackMediaItem(self.track, item)
            RPR_MoveMediaItemToTrack(track, item)

    def _add_child(self):
        children = self.get_children()
        child_index = len(children) + 1
        name = "{} {}".format(self.name, child_index)
        idx = self.idx + 1

        RPR_InsertTrackAtIndex(idx, True)
        track = RPR_GetTrack(0, idx)
        RPR_GetSetMediaTrackInfo_String(track, "P_NAME", name, True)
        child = ReaperTrack(idx, RPR_GetTrack(0, idx))
        return child

    def add_multipe_children(self, amount_of_children):
        if not self.is_parent():
            self._make_folder()
            amount_of_children -= 1

        for i in range(amount_of_children):
            self._add_child()

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

        if self._is_free(item):
            self.do_copy(item, self)
            return True

        if not self.is_parent():
            self._make_folder()

        children = self.get_children()
        for child in children:
            if child._is_free(item):
                self.do_copy(item, child)
                return True

        child = self._add_child()
        self.do_copy(item, child)
        return True

    def do_copy(self, item, track):
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

    def do_move(self, item, track):
        self.logger.debug("moving {} {}".format(item, track))
        RPR_MoveMediaItemToTrack(item, track.track)
        color = RPR_ColorToNative(0, 255, 0) | 0x01000000
        RPR_SetMediaItemInfo_Value(item, "I_CUSTOMCOLOR", color)
        return

    def add_to_child(self, child_index, item):
        children = self.get_children()
        track = children[child_index]
        self.do_copy(item, track)


def get_all_tracks_from_media_items(items_):
    tracks_ = []
    for item_ in items_:
        new_track = RPR_GetMediaItem_Track(item_)
        if new_track not in tracks_:
            tracks_.append(new_track)
    return tracks_


def move_items_on_new_tracks_without_overlaping():
    count = RPR_CountSelectedMediaItems(0)
    if count != 0:
        bus = ReaperTrack.get_track_by_name(ReaperTrack.NAME)
        items = []
        for i in range(0, count):
            item = RPR_GetSelectedMediaItem(0, i)
            items.append(item)
        for item in items:
            bus.tester(item)
    RPR_UpdateArrange()


def move_items_on_new_tracks():
    count = RPR_CountSelectedMediaItems(0)
    if count != 0:
        bus = ReaperTrack.get_track_by_name(ReaperTrack.NAME)
        items = []
        for i in range(0, count):
            item = RPR_GetSelectedMediaItem(0, i)
            items.append(item)
        tracks = get_all_tracks_from_media_items(items)
        bus.add_multipe_children(len(tracks))
        for item in items:
            track_id = RPR_GetMediaItemTrack(item)
            track_index = tracks.index(track_id)
            bus.add_to_child(track_index, item)
    RPR_UpdateArrange()
