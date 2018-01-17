import bq
import pandas as pd
import numpy as np
import os
from datetime import datetime
from os.path import basename

# get lap metrics
test_file = "tcx/2052870182_track.tcx"
filename = basename(test_file)
lap_df = bq.parse_lap_metrics(test_file)

# get date of file for sorting
file_date = datetime.date(lap_df.iloc[0]['run_start'])
file_year = str(file_date.year)
file_month = str(file_date.month)


# move file into appropriate year-month directory
path = ("/").join(["tcx", file_year, file_month, filename])
os.rename(test_file, path)
