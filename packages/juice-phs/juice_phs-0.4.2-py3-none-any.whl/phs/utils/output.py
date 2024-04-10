import csv
from itertools import zip_longest
from datetime import datetime

from phs.setup import get_version_from_setup_cfg
VERSION = get_version_from_setup_cfg()


def write_csv(header_list, data_columns, file_name, title, resolution, precision=6, mk=False):
    # Check if the length of header_list matches the number of data columns
    if len(header_list) != len(data_columns):
        raise ValueError("Number of columns in header doesn't match number of data columns")

    # Zip the columns into rows using zip_longest
    data_rows = list(zip_longest(*data_columns))

    # Round only numeric values in the rows to the specified precision
    rounded_data = [
        [
            round(float(item), precision) if isinstance(item, (int, float)) else item
            for item in row
        ]
        for row in data_rows
    ]

    # Get the current date and time
    current_datetime = datetime.now()
    # Format the datetime object as a string in the specified format
    formatted_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M:%S")

    with open(file_name, 'w+', newline='') as csvfile:

        writer = csv.writer(csvfile)

        # Write the header
        csvfile.write(f'# {title}\n')
        csvfile.write(f'# JUICE SPICE MK: : {mk}\n')
        csvfile.write(f'# JUICE-SHT version: {VERSION}\n')
        csvfile.write(f'# Resolution [s]: {resolution:.0f}\n')
        csvfile.write(f'# Generation date: {formatted_datetime}\n')
        csvfile.write(f'{",".join(map(str, header_list))}\n')
        # Write the data rows
        writer.writerows(rounded_data)

    return