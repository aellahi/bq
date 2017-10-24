# Package containing functions to calculate run metrics
# Author Aisha Ellahi

import tcxparser
import xmltodict as xml
import collections
from pint import UnitRegistry
import datetime

ureg = UnitRegistry()


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

    """Parses tcx_file and returns lap-by-lap metrics.
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
            run_type = tcx_file.split('_')[1]
            laps = tcx_obj['TrainingCenterDatabase']['Activities']['Activity']['Lap']
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
                    d['meters'] = float(lap['DistanceMeters'])
                    d['start_meters'] = float(lap['Track']['Trackpoint'][0]['DistanceMeters'])
                    d['end_meters'] = float(lap['Track']['Trackpoint'][-1]['DistanceMeters'])
                    d['average_cadence'] = float(lap['Extensions']['ns3:LX']['ns3:AvgRunCadence'])
                    d['start_altitude'] = float(lap['Track']['Trackpoint'][0]['AltitudeMeters'])
                    d['end_altitude'] = float(lap['Track']['Trackpoint'][-1]['AltitudeMeters'])
                    d['average_cadence'] = float(lap['Extensions']['ns3:LX']['ns3:AvgRunCadence'])
                    lap_list.append(d)
                except KeyError:
                    lap_list.append(d)
            return lap_list
        except:
            return None

def seconds_to_minutes(seconds):

    '''Convert seconds as float to minutes.'''

    secs = seconds * ureg.seconds
    minutes = secs.to(ureg.minute)
    return minutes.magnitude

def meters_to_miles(meters):

    '''Convert meters as float to meters.'''

    dist_m = meters * ureg.meter
    miles = dist_m.to(ureg.mile)
    return miles.magnitude