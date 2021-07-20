"""
@noindex true
"""

from reaper_python import *
from logging import root, Formatter, FileHandler, DEBUG, ERROR
from lib_move_to_bus import *

ACTIVE_PROJ = 0
UNITY_VOL = 716.2178503126559
MINIMUM_LENGHT_OF_BLANK = 10
NORMAL_VOLUME = 0
INCREASED_VOLUME = UNITY_VOL
FADE_TIME = 0.5
TIME_FOR_MAXIMUM_GAIN = 3
REFERENCE_TRACK_NAME = "AUTOMATIONS REFERENCES"
MUSIC_BUS_NAME = "MUSIC DRY"


def set_automation_value_references():
    global INCREASED_VOLUME, NORMAL_VOLUME

    reference_track = ReaperTrack.get_track_by_name(REFERENCE_TRACK_NAME)
    envelope = _get_track_volume_envelope(reference_track.track)
    envelope_points_values = []
    for index in range(2):
        point = RPR_GetEnvelopePointEx(envelope, -1, index, 0, 0, 0, 0, 0)
        value = point[5]
        envelope_points_values.append(value)
        LOGGER.debug("VALUE" + str(value))

    INCREASED_VOLUME = envelope_points_values[0]
    NORMAL_VOLUME = envelope_points_values[1]


def get_all_items_in_track(track):
    LOGGER.debug("      GETTING ALL ITEMS ON TRACK")
    number_of_items = RPR_CountTrackMediaItems(track)
    items = []
    LOGGER.debug("NUMBER_OF_ITEMS " + str(number_of_items))
    for item_index in range(number_of_items):
        item = RPR_GetTrackMediaItem(track, item_index)
        items.append(item)

    return items


def get_region_around_point(point, delta):
    return (point - delta / 2, point + delta / 2)


def increase_volume_to_region(regions):
    music_track = ReaperTrack.get_track_by_name(MUSIC_BUS_NAME)
    volume_envelope = _get_track_volume_envelope(music_track.track)

    clear_envelope(volume_envelope)

    for region in regions:
        LOGGER.debug("      REGION: " + str(region))
        LOGGER.debug("VALUE" + str(NORMAL_VOLUME) + "   " + str(INCREASED_VOLUME))
        starting_point = region[0]
        ending_point = region[1]
        duration = ending_point - starting_point

        musical_moment_gain = get_gain_of_musical_moment(duration, TIME_FOR_MAXIMUM_GAIN, NORMAL_VOLUME,
                                                         INCREASED_VOLUME)
        climb_region = get_region_around_point(starting_point, FADE_TIME)
        descent_region = get_region_around_point(ending_point, FADE_TIME)

        _insert_automation_item_beetween_points(volume_envelope, climb_region, NORMAL_VOLUME, musical_moment_gain)
        _insert_automation_item_beetween_points(volume_envelope, descent_region, musical_moment_gain, NORMAL_VOLUME)


def get_gain_of_musical_moment(duration, time_for_maximum_delta_gain, low_value, high_value):
    if duration >= time_for_maximum_delta_gain:
        return high_value

    else:
        return interpolate(duration, time_for_maximum_delta_gain, low_value, high_value)


def interpolate(x, x_max, y_low, y_high):
    LOGGER.debug(str(x))
    LOGGER.debug(str(x_max))
    LOGGER.debug(str(y_low))
    LOGGER.debug(str(y_high))
    delta_y = y_high - y_low
    delta_x = x_max

    slope = delta_y / delta_x

    y = y_low + x * slope

    return y


def get_all_items_in_selected_tracks():
    number_of_selected_tracks = RPR_CountSelectedTracks(ACTIVE_PROJ)
    items = []
    for selected_track_index in range(number_of_selected_tracks):
        track = RPR_GetSelectedTrack(ACTIVE_PROJ, selected_track_index)
        items.extend(get_all_items_in_track(track))

    return items


def get_blanks_points(limits, minimum_lenght_of_blank):
    previous_time = 0
    points = []
    for time in limits:
        if (time - previous_time) >= minimum_lenght_of_blank:
            points.append((previous_time / 100, time / 100))
        previous_time = time

    return points


def get_items_limits(items):
    limits = []
    for item in items:
        limit = get_item_range(item)
        limits.extend(limit)
    return sorted(limits)


def get_item_range(item):
    position = int(RPR_GetMediaItemInfo_Value(item, "D_POSITION") * 100)
    length = int(RPR_GetMediaItemInfo_Value(item, "D_LENGTH") * 100)
    limit = set(range(position, position + length))
    return limit


def _insert_automation_item_beetween_points(env, points, starting_value, ending_value):
    region_start = points[0]
    region_end = points[1]

    _insert_automation_ramp(env, region_start, region_end, starting_value, ending_value)


def _insert_automation_item_in_region(env, region, starting_value, ending_value):
    region_start = region[4]
    region_end = region[5]
    _insert_automation_ramp(env, region_start, region_end, starting_value, ending_value)


def _get_track_volume_envelope(track):
    vol_env = RPR_GetTrackEnvelopeByName(track, "Volume")
    return vol_env


def _insert_automation_ramp(env, starting_point, ending_point, starting_value, ending_value):
    RPR_InsertEnvelopePoint(env, starting_point, starting_value, 0, 0, False, True)
    RPR_InsertEnvelopePoint(env, ending_point, ending_value, 0, 0.0, False, True)
    RPR_Envelope_SortPoints(env)


def clear_envelope(envelope):
    LOGGER.debug("  CLEARING ENVELOPE")
    RPR_DeleteEnvelopePointRange(envelope, 0, RPR_GetProjectLength(ACTIVE_PROJ))

def main():
    set_automation_value_references()
    items = get_all_items_in_selected_tracks()
    limits = get_items_limits(items)
    musical_regions = get_blanks_points(limits, MINIMUM_LENGHT_OF_BLANK)
    increase_volume_to_region(musical_regions)

if __name__ == "__main__":
    pass
