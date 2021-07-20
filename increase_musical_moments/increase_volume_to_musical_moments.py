"""
@description increase musical moments
@version 0.1.2
@author Wouter Gordts
@provides
	[nomain] ./lib_move_to_bus.py > lib_move_to_bus.py
	[nomain] ./lib_increase_volume_to_musical_moments.py > lib_increase_volume_to_musical_moments.py
"""

from reaper_python import *
from lib_increase_volume_to_musical_moments import main 
import logging

LOGGER = logging.root

if __name__ == "__main__":
    RPR_Undo_BeginBlock()
    LOGGER.debug("musical moment script")
    main()
    RPR_Undo_EndBlock("musical moment script", 0)
