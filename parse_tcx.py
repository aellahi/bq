import bq
import pandas as pd
import numpy as np
import os
from datetime import datetime
from os.path import basename

# cd into /Users/aishaellahi/py2/bq/tcx
tcx_dir = "/Users/aishaellahi/py2/bq/tcx"
os.chdir(tcx_dir)
dir_contents = os.listdir(tcx_dir)

# initialize list of dfs
dfs = []

for f in dir_contents:
    extension = os.path.splitext(f)[-1]
    if extension == '.tcx':
        lap_df = bq.parse_lap_metrics(f)
        if isinstance(lap_df, pd.core.frame.DataFrame):
            # Calculate lap pace
            lap_df['miles'] = lap_df['meters'].apply(bq.meters_to_miles)
            lap_df['minutes'] = lap_df['seconds'].apply(bq.seconds_to_minutes)
            lap_df['pace min/mi'] = lap_df['minutes']/lap_df['miles']
            lap_df['pace min/mi'] = lap_df['pace min/mi'].round(decimals=2)
            dfs.append(lap_df)

            # get date of file for sorting
            file_date = datetime.date(lap_df.iloc[0]['run_start'])
            file_year = str(file_date.year)
            file_month = str(file_date.month).zfill(2)

            # move file into appropriate year-month directory
            path = ("/").join([os.getcwd(), file_year, file_month, f])
            move_message = "Moving {} to {}".format(f, path)
            print(move_message)
            os.rename(f, path)

            # print message
            message = "Parsed {}".format(f)
            print(message)
    else:
        pass

# concat all dfs  into one df
all_laps = pd.concat(dfs)
outcsv = '/Users/aishaellahi/py2/bq/runs/laps.csv'
all_laps.to_csv(outcsv, index=False)

# Aggregate based on run
