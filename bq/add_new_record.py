# Author: Aisha Ellahi

import pandas as pd
import yaml
import sys

FILENAME = sys.argv[1]
NEW_RECORD = sys.argv[2]

# Read run records
records_df = pd.read_csv(FILENAME)
records_df.set_index(['date', 'run'], inplace=True)
records = dict(records_df)

# read yaml
with open(NEW_RECORD) as f:
    new_record = yaml.load(f, Loader=yaml.FullLoader)

# Lookup new entry index
RECORD_IDX = new_record['date'], new_record['run']

# mark run as completed
records['completed'][RECORD_IDX] = True

# Add new fields
for col, field in new_record.items():

    if (col == 'date') or (col == 'run'):
        pass
    else:
        # TODO: Fix AssertionError (mismatch in types)
        try:
            records[col][RECORD_IDX] = field
        except AssertionError:
            print(col)
            print(field)
            print(" ")

# re-create records df
modified_records_df = pd.DataFrame(records)
modified_records_df.reset_index(inplace=True)

# save
modified_records_df.to_csv(FILENAME, index=False)
