# Package containing functions to calculate run metrics
# Author Aisha Ellahi

import tcxparser
import xmltodict as xml
import collections
from pint import UnitRegistry
import datetime
import pandas as pd
ureg = UnitRegistry()

# To structure with classes
# Create a "lap" object
# Attributes:
    # * distance
    # * pace in minutes/mile
    # * start altitude
    # * end altitude
    # * altitude change

# class lap:
#     """A lap object."""
#
#     # Default distance = 1 mile
#     distance = ureg.mile
#
#     def meters_to_miles(meters):
#         """Convert meters to miles."""
#
#         dist_m = meters * ureg.meter
#         miles = dist_m.to(ureg.mile)
#         return miles.magnitude
#
#     def __init__(self, seconds, start_altitude, end_altitude):
#         self.seconds = seconds
#         self.minutes =
#         self.pace =
#         self.start_altitude =
#         self.end_altitude =
#         self.altitude_change =

def run_metrics(tcx_file, run_type=None):
    """Parses a Fitbit tcx_file.
    Returns dictionary:
        *start time of run
        *total distance in meters
        *total time in seconds
        *total miles
        *total minutes
        *average pace in minutes per mile
        dictionary of lap, distance, and time."""

    def parse_run_type(run_type):
        if run_type:
            return run_type
        else:
            return tcx_file.split('_')[1]

    with open(tcx_file) as tcx:
        try:
            tcx_obj = xml.parse(tcx.read())
            total_dist_m = 0
            total_time_sec = 0
            start_time = str(tcx_obj['TrainingCenterDatabase']['Activities']['Activity']['Lap'][0]['@StartTime'])
            lap_dict = collections.OrderedDict()
            laps = tcx_obj['TrainingCenterDatabase']['Activities']['Activity']['Lap']
            if laps:
                for n, lap in enumerate(laps):
                    lap_dict[n] = float(total_dist_m), float(total_time_sec)
                    total_dist_m += float(lap['DistanceMeters'])
                    total_time_sec += float(lap['TotalTimeSeconds'])

                dist_m = total_dist_m * ureg.meter
                miles = dist_m.to(ureg.mile)
                secs = total_time_sec * ureg.seconds
                minutes = secs.to(ureg.minute)
                min_per_mile = (minutes / miles).magnitude
                metrics = (start_time, total_dist_m, total_time_sec, miles.magnitude, minutes.magnitude, min_per_mile)
                columns = ['start', 'distance (m)', 'time (s)', 'miles', 'minutes', 'min_per_mile']
                metrics_dict = dict(list(zip(columns, metrics)))
                metrics_dict['run_type'] = parse_run_type(run_type)
                return metrics_dict
            else:
                return None
        except:
            print "Error! Unable to read file: ", tcx_file
            return None


def track_lap_time(distance_in_meters, lap_type='speed', speed_1600m=(417, 427), tempo_1600m=(447, 457)):

    '''Returns target time to finish distance_in_meters in minutes:seconds units.
    Default lap_type is speed. Specify "tempo" to return target tempo speed.'''

    distance_multiplier = float(distance_in_meters) / float(1600)

    def calc_target_time(seconds, dist_multiplier):
        target_time = (seconds * dist_multiplier)
        minutes = str(datetime.timedelta(seconds=target_time))
        return minutes

    if lap_type == 'speed':
        target = calc_target_time(417, distance_multiplier)
    elif lap_type == 'tempo':
        target = calc_target_time(447, distance_multiplier)
    return target


def parse_lap_metrics(tcx_file):

    """Parses tcx_file and returns pandas dataframe with lap-by-lap metrics.
    Returns a list of dictionaries for each lap with the following metrics:
        * lap start time
        * total lap time in seconds
        * total lap distance in meters
        * starting altitude of lap
        * ending altitude of lap
        """

    with open(tcx_file) as tcx:
        try:
            tcx_obj = xml.parse(tcx.read())
            run_type = tcx_file.split('_')[-1].split('/')[0]
            laps = tcx_obj['TrainingCenterDatabase']['Activities']['Activity']['Lap']
            #print(type(laps))
            if isinstance(laps, list):
                keys = ['lap_start', 'seconds', 'meters', 'start_meters', 'end_meters',
                        'start_altitude', 'end_altitude', 'average_cadence']
                lap_list = []
                for n, lap in enumerate(laps):
                    d = {k:None for k in keys}
                    if n==0:
                        run_start = lap['@StartTime']
                    try:
                        d['run_type'] = run_type
                        d['run_start'] = run_start
                        d['lap_start'] = lap['@StartTime']
                        d['seconds'] = float(lap['TotalTimeSeconds'])
                        d['distance (m)'] = float(lap['DistanceMeters'])
                        d['start (m)'] = float(lap['Track']['Trackpoint'][0]['DistanceMeters'])
                        d['end (m)'] = float(lap['Track']['Trackpoint'][-1]['DistanceMeters'])
                        d['start_altitude (m)'] = float(lap['Track']['Trackpoint'][0]['AltitudeMeters'])
                        d['end_altitude (m)'] = float(lap['Track']['Trackpoint'][-1]['AltitudeMeters'])
                        d['average_cadence'] = float(lap['Extensions']['ns3:LX']['ns3:AvgRunCadence'])
                        lap_list.append(d)
                    except KeyError:
                        lap_list.append(d)
                df = pd.DataFrame(lap_list)
                df.sort_values(by='lap_start', inplace=True)
                df['run_start'] = pd.to_datetime(df['run_start'])
                df['lap_start'] = pd.to_datetime(df['lap_start'])
                return df
            elif isinstance(laps, dict):
                try:
                    track_list = tcx_obj['TrainingCenterDatabase']['Activities']['Activity']['Lap']['Track']['Trackpoint']
                    trackpoints = []
                    keys = ['time', 'position', 'altitude_meters', 'distance_meters']
                    for n, trackpoint in enumerate(track_list):
                        d = {k:None for k in keys}
                        try:
                            d['time'] = trackpoint['Time']
                            d['latitude'] = trackpoint['Position']['LatitudeDegrees']
                            d['longitude'] = trackpoint['Position']['LongitudeDegrees']
                            d['altitude (m)'] = trackpoint['AltitudeMeters']
                            d['distance (m)'] = trackpoint['DistanceMeters']
                        except KeyError:
                            pass
                        trackpoints.append(d)
                    df = pd.DataFrame(trackpoints, columns=['time', 'distance (m)',
                    'altitude (m)', 'latitude', 'longitude'])
                    # enforce types
                    float_types = ['distance (m)', 'altitude (m)']
                    for col in float_types:
                        df[col] = df[col].astype(float)
                    return df
                except:
                    return None
        except:
            return None

def seconds_to_minutes(seconds, format='float'):

    '''Convert seconds to minutes.

    Parameters
    ----------
    seconds: number of seconds
    format: 'float' or 'hh:mm:ss'; default 'float'
    '''

    if format=='float':
        secs = seconds * ureg.seconds
        minutes = secs.to(ureg.minute)
        return minutes.magnitude
    elif format=='hh:mm:ss':
        return str(datetime.timedelta(seconds=seconds))
    else:
        # Raise exception
        print('Unrecognized format!')
        raise Exception

def meters_to_miles(meters):

    '''Convert meters to miles.'''

    dist_m = meters * ureg.meter
    miles = dist_m.to(ureg.mile)
    return miles.magnitude

def total_course_time(distance, pace, miles=True):

    '''Calculates the total time to complete the input distance
    for a given pace.
    Arguments:
    * distance: distance to run. Default units is miles. To change to meters,
    set miles=False.
    * pace: pace in mm:ss format. E.g., enter the string "8:35" for 08:35.

    Returns the total time to complete the distance in hh:mm:ss format.
    '''

    # convert the pace string to total seconds
    min, sec = tuple(map(int, pace.split(':')))
    pace_in_seconds = (60*min) + sec
    total_course_seconds = distance * pace_in_seconds
    total_course_time = seconds_to_minutes(total_course_seconds,
    format='hh:mm:ss')

    return total_course_time

def target_pace(distance, total_time, miles=True):

    '''Calculates the target pace to hit to complete the input distance
    in the total input time.
    -Arguments:
    * distance: distance to run. Default units is miles. To change to meters,
    set miles=False.
    * total_time: total time in 'hh:mm:ss' format.

    Returns target_pace in 'hh:ss' format.
    '''

    # convert total_time to seconds
    hour, min, sec = tuple(map(int, total_time.split(':')))
    total_seconds = (hour*60*60) + (min*60) + sec

    # divide by distance
    pace = float(total_seconds)/float(distance)
    return seconds_to_minutes(pace, format='hh:mm:ss')
