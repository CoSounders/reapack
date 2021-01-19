"""
@noindex true
"""

from sys import stdout
from logging import root, Formatter, StreamHandler, INFO, DEBUG, ERROR, CRITICAL
from lib_move_to_bus import ReaperTrack, main

LOGGER = root
FMT_STR = '%(asctime)s - %(levelname)s - %(name)s.%(funcName)s %(message)s'
DATE_STR = '%Y-%m-%d %H:%M:%S'
FMT = Formatter(FMT_STR, DATE_STR)
ST_HANDLER = StreamHandler(stdout)
ST_HANDLER.setFormatter(FMT)
LOGGER.addHandler(ST_HANDLER)
LOGGER.setLevel(DEBUG)
#LOGGER.setLevel(ERROR)

ReaperTrack.NAME = "#!FX"
main()
