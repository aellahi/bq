# Creates a .csv file of runs for a 16-week marathon training cycle
# following the 3+2 system of training

import pandas as pd
from datetime import datetime
from datetime import timedelta
import numpy as np

def date_range(start_date, num_periods, frequency):

    """Returns a list object of datetime objects of length
    num_periods separated by frequency.
    Arguments:
    -start_date: datetime object of date to start range
    -num_periods: int object of length of range
    -frequency: int object in days to separate dates between start
    and stop; fed to timedelta as an argument
    """

    total_days = num_periods*(frequency)
    steps = np.arange(0, total_days, frequency)
    dates = [start_date+timedelta(step) for step in steps]
    return dates

def create_training_plan(speed_start, tempo_start, long_start,
    num_weeks = 16):

    """Returns a pandas dataframe of runs based on a 16-week marathon
    training plan from the 3+2 system of training. Book reference: Run Less
    Run Faster by Bill Pierce, Scott Murr, and Ray Moss.

    Arguments:
    -num_weeks: int object specifying the number of total weeks in plan.
    default = 16.
    -speed_start = datetime object specifying start date of speed interval
    workouts.
    -tempo_start = datetime object specifying start date of tempo runs.
    -long_start = datetime object specifying start date of long runs.

    Returns: pandas df with the following columns:
        * week: week number in training plan
        * date: date of run
        * run: run type; one of 3: speed, tempo, or long
        * run_details: short string describing number of miles and pace at
            which to complete run
        * completed: boolean column specifying whether or not the run was
            completed as outlined in the plan; starts out as False
        * effort: int column denoting how effortful/difficult the run was;
            rating of 1 to 5, with 1 = easy, 5 = very hard
        * pre_run_calories: int column of number of calories consumed before
            the run
        * pre_run_food: string column; short descriptor of what was eaten
            before the run
        * post_run_calories: int column of number of calories consumed after
        * post_run_food: analogous to pre_run_food column
        * run_calories: number of calories consumed *during* the run
        * run_food: analogous to pre_run_food column except food consumed
            during the run.
        * notes: string description of any other relevant notes on the run
        * tcx_file: Garmin tcx file name containing run data
        * garmin_run_name: name of the logged run in Garmin; metadata of the
            tcx file
        """

    columns = ['week',
         'date',
         'run',
         'completed',
         'effort',
         'pre_run_calories',
         'pre_run_food',
         'post_run_calories',
         'post_run_food',
         'run_food',
         'run_calories',
         'notes',
         'tcx_file',
         'garmin_run_name']

    workouts = num_weeks * 3
    rows = range(workouts)
    week_column = pd.Series(np.repeat([1, 2, 3], num_weeks), index=rows,
        dtype=int)
    run_column = pd.Series(['speed', 'tempo', 'long']*num_weeks, index=rows,
        dtype=str)
    completed_column = pd.Series([False]*workouts, index=rows, dtype=bool)
    speed_ind = np.arange(0, workouts, 3)
    tempo_ind = speed_ind+1
    long_ind = speed_ind+2
    for date in [speed_start, tempo_start, long_start]:
        speed_dates = pd.Series(date_range(speed_start, num_weeks, 7),
            index=speed_ind)
        tempo_dates = pd.Series(date_range(tempo_start, num_weeks, 7),
            index=tempo_ind)
        long_dates = pd.Series(date_range(long_start, num_weeks, 7),
            index=long_ind)

    # create empty dataframe
    empty_array = np.zeros((workouts, len(columns)))
    df = pd.DataFrame(empty_array, columns=columns)

    # Fill in df and specify datatypes
    df['week'] = week_column
    df['run'] = run_column
    df['completed'] = completed_column
    for n, row in df.iterrows():
        if row['run'] == 'speed':
            df['date'][n] = speed_dates[n]
        elif row['run'] == 'tempo':
            df['date'][n] = tempo_dates[n]
        elif row['run'] == 'long':
            df['date'][n] = long_dates[n]
    df = df.astype({'effort': int, 'pre_run_calories': int,
    'post_run_calories': int, 'run_calories': int
    }, inplace=True)
    str_cols = ['pre_run_food', 'post_run_food', 'run_food',
    'notes', 'garmin_run_name', 'tcx_file']

    for col in str_cols:
        df[col] = ' '

    return df


test_plan = create_training_plan(speed_start, tempo_start, long_start, num_weeks=18)

