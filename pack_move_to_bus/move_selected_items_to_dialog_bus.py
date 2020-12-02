"""
@description Move selected items to dialog bus package
@author Wouter Gordts
@version 0.2
@metapackage true
@provides [nomain] ../lib/lib_move_to_bus.py > lib_move_to_bus.py
"""

from os import urandom
from reaper_python import *
from sys import stdout
from logging import root, Formatter, StreamHandler, INFO, DEBUG, ERROR, CRITICAL
from lib_move_to_bus import ReaperTrack

LOGGER = root
FMT_STR = '%(asctime)s - %(levelname)s - %(name)s.%(funcName)s %(message)s'
DATE_STR = '%Y-%m-%d %H:%M:%S'
FMT = Formatter(FMT_STR, DATE_STR)
ST_HANDLER = StreamHandler(stdout)
ST_HANDLER.setFormatter(FMT)
LOGGER.addHandler(ST_HANDLER)
LOGGER.setLevel(DEBUG)
#LOGGER.setLevel(ERROR)

ReaperTrack.NAME = "#DIALOG"

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
