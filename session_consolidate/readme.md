# Consolidate OMF to RPP via AATranslator

This is a highly specific script.
The workflow is as follows:

* **outside Reaper**
	1. create a new folder
	1. convert your individual OMF files to individual RPP sessions
	1. move the individual RPP sessions and the corresponding video files inside your folder
	1. copy the */path/to/your/folder* to the clipboard
* **inside Reaper**
	1. launch the script
	1. paste */path/to/your/folder* in the dialog 
	1. reaper will now close all your open sessions (will ask to save or not)
	1. reaper creates a *consolidate.RPP* session
	1. reaper opens every individual RPP session as a tab
		* imports the video to this session
		* copy and pastes all tracks from each session to the *consolidate.RPP* session with a time offset
	1. reaper merges all **same named tracks** in the *consolidate.RPP* session 
	1. reaper deletes all tracks without items on it
	1. reaper creates named regions for each **videofile**

# TODO

* prompt for ffmpeg video convert
* prompt for automation removal
