"""
@noindex true
"""

import pathlib
import time
from timecode import Timecode
import logging

LOGGER = logging.root

class EDLItem(object):
   def __init__(self, row):
        self._row = row


class EDLCut(EDLItem):
    def __init__(self, *args, **kwargs):
        EDLItem.__init__(self, *args, **kwargs)
        
    def get_master_region(self):
        region = (self._row["master_in"], self._row["master_out"])
        return region


class EDL(object):
    COLUMN_MAP = [
            "event_id",
            "source_name", 
            "event_kind", 
            "event_type", 
            "source_in", 
            "source_out", 
            "master_in", 
            "master_out" 
            ]
    TYPE_MAP = {
            "C": EDLCut,
            "D": NotImplemented,
            "W": NotImplemented,
            }

    def __init__(self):
        self.logger = LOGGER.getChild(self.__class__.__name__)
        self._data = {"C": []}
        pass

    @property
    def fps(self):
        print("fps", str(self._data["fps"]))
        return str(self._data["fps"])
    
    @fps.setter
    def fps(self, fps):
        self._data["fps"] = str(fps)

    @property
    def title(self):
        return self._data["TITLE:"]

    def _add_title(self, title):
        self._data["TITLE:"] = title
    
    def _add_fcm(self, fcm):
        self.logger.debug("line is fcm: {}".format(fcm))
 
    def _add_comment(self, comment):
        self.logger.debug("line is comment: {}".format(comment))

    @property
    def cuts(self):
        return self._data["C"]
    
    def load_from_edl_file(self, filepath):
        with open(filepath, "r") as fp:
            lines = [line.rstrip().split() for line in fp]
        for d in lines:
            try:
                identifier = d[0]
            except Exception as e:
                self.logger.error(e)
                continue
            if identifier in METADATA_MAP.keys():
                line = " ".join(d)
                func = METADATA_MAP[identifier](self, line)
                continue
            if len(d) == len(EDL.COLUMN_MAP):
                data = {}
                for i in range(0, len(d)):
                    data[EDL.COLUMN_MAP[i]] = d[i]
                func = EDL.TYPE_MAP[data["event_type"]](data)
                self.cuts.append(func)

    def _convert_tc_to_seconds(self, tc):
        hours, minutes, seconds, frames = [int(x) for x in tc.split(":")]
        seconds = seconds + (minutes * 60) + (hours * 60 *60) + (frames / float(self.fps))
        seconds = round(seconds, 3)
        print(seconds)
        return seconds

    def get_start_and_end_times(self):
        items = []
        for cut in self.cuts:
            if "." in self.fps:
                force = True
            else:
                force = False
            start, end = cut.get_master_region()
            # start = self._convert_tc_to_seconds(start)
            # end = self._convert_tc_to_seconds(end)
            start = Timecode(self.fps, start, force_non_drop_frame=force).total_seconds
            end = Timecode(self.fps, end, force_non_drop_frame=force).total_seconds
            items.append((round(start, 3), round(end, 3)))
        items = sorted(set(items))
        return items


METADATA_MAP = {
        "TITLE:": EDL._add_title,
        "FCM:": EDL._add_fcm,
        "*": EDL._add_comment,
        }


if __name__ == "__main__":
    LOGGER = logging.root
    LOGGER.setLevel(logging.DEBUG)
    ST_HANDLER = logging.StreamHandler()
    LOGGER.addHandler(ST_HANDLER)
    LOGGER.info("hello world")
    edl = EDL()
    edl.load_from_edl_file("/home/waldek/Downloads/EXPORT_EDL_1.edl")
    edl.fps = 29.97
    print(edl.title)
    print(edl.get_start_and_end_times())
