import csv
from datetime import datetime
import spiceypy as spice
import tempfile

def reorder_csv_columns(input_file, output_file, column_order):
    with open(input_file, 'r', newline='') as file:
        csv_reader = csv.reader(filter(lambda row: row[0]!='#', file))
        rows = list(csv_reader)

    reordered_rows = []

    for row in rows:
        reordered_row = [row[i] for i in column_order]
        reordered_rows.append(reordered_row)

    with open(output_file, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(reordered_rows)


def replace_csv_column(input_file, output_file, column_index, new_value_function):
    with open(input_file, 'r') as file_in, open(output_file, 'w', newline='') as file_out:
        reader = csv.reader(file_in)
        writer = csv.writer(file_out)

        for row in reader:
            # Replace the value of the specified column with the new value
            value = row[column_index]
            new_value = new_value_function(value)
            # The Row is added only if there os a default FOV for the instrument.
            if new_value:
                row[column_index] = new_value
                writer.writerow(row)

def instrument_default_active_fov(name):
    ins_dict = {'GALA': 'JUICE_GALA_RXT',
                'JANUS': 'JUICE_JANUS',
                'MAJIS': 'JUICE_MAJIS_ENVELOPE',
                'NAVCAM': 'JUICE_NAVCAM-1',
                'RIME': 'JUICE_RIME_BASE',
                'SWI': 'JUICE_SWI_CH1',
                'UVS': 'JUICE_UVS'}
    try:
        active_fov = ins_dict[name]
    except:
        active_fov = None

    return active_fov

def instrument_default_cadence(cadence):
    return '0'


def observation_timeline():
    return 'OBSERVATION_TEST'

def instrument_mode_active_fovs_dict():

    fov_active_modes = spice.gnpool("*FOV_ACTIVE_MODE*", 0, 100, 100)
    modes_dict = {}

    for fov_active_mode in fov_active_modes:
        fov_id = fov_active_mode.split('INS')[-1]
        fov_id = int(fov_id.split('_FOV_ACTIVE_MODES')[0])
        try:
            fov_nm = spice.bodc2n(fov_id)
        except:
            print(f'FOV ID: {fov_id} NOT FOUND.')
            continue
        ins_nm = fov_nm.split('_')[1]

        modes = spice.gcpool(fov_active_mode, 0, 80, 80)

        # Add the instrument dictionary if not present
        if ins_nm not in modes_dict.keys():
            modes_dict[ins_nm] = {}

        for mode in modes:

            if mode not in modes_dict[ins_nm].keys():
                modes_dict[ins_nm][mode] = []
                modes_dict[ins_nm][mode].append(fov_nm)
            else:
                modes_dict[ins_nm][mode].append(fov_nm)

    return modes_dict


def eps_modes_to_obs_cov(eps_modes_input, cadence=0, instrument=False, lines_to_skip=23, output_dir='.'):

    modes_fovs_dict = instrument_mode_active_fovs_dict()

    # Read the input CSV file
    with open(eps_modes_input, 'r') as modes_file:
        # Skip the specified number of lines
        for _ in range(lines_to_skip):
            next(modes_file)

        # Initialize csv.DictReader after skipping lines
        reader = csv.DictReader(modes_file)
        data = list(reader)

    # Initialize variables
    prev_time = None
    prev_row = None
    output_files = []

    # Iterate through columns (excluding the first one, which is the timestamp)
    columns = reader.fieldnames[1:]
    for ins in columns:
        if instrument:
            if instrument.lower() != ins.lower():
                continue

        output_file = f"otc_{ins.lower()}.csv"
        # Define a dictionary to keep track of whether changes were recorded for each column
        column_changes = {column: False for column in columns}

        # Iterate through the data
        for row in data:
            current_time = datetime.strptime(row['dd-mmm-yyyy_hh:mm:ss'], '%d-%b-%Y_%H:%M:%S')
            column_value = row[ins]

            if prev_row is not None and column_value != prev_row[ins]:
                # Write the change to the output CSV
                mode = prev_row[ins]
                try:
                    observation = observation_timeline()
                    active_fovs = modes_fovs_dict[ins][mode]

                    # Check if changes were recorded for this column
                    if not column_changes[ins]:
                        output_file = f"otc_{ins.lower()}.csv"
                        output_files.append(output_file)
                        # create an empty file called output_file
                        with open(f'{output_dir}/{output_file}', 'w'):
                            pass
                        column_changes[ins] = True  # Mark changes recorded for this column

                    # Write the change to the output CSV
                    with open(f'{output_dir}/{output_file}', 'a', newline='') as output_csv:
                        writer = csv.writer(output_csv)
                        for fov in active_fovs:
                            writer.writerow([observation,
                                             prev_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                             current_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                             cadence,
                                             fov])
                except:
                    pass

            prev_time = current_time
            prev_row = row

    return output_files


def obs_plan_to_obs_cov(csvfile, cesium_file):
    # original columns = ['DEFINITION', 'START_TIME', 'STOP_TIME', 'NAME',    'SOURCE']
    # target columns  =  ['NAME',       'START_TIME', 'STOP_TIME', 'CADENCE', 'FOV']

    temp_file = tempfile.NamedTemporaryFile(delete=True)
    temp_file_path = temp_file.name
    temp_file_bis = tempfile.NamedTemporaryFile(delete=True)
    temp_file_bis_path = temp_file_bis.name

    column_order = [3, 1, 2, 0, 4]  # Specify the desired order of columns
    reorder_csv_columns(csvfile, temp_file_path, column_order)
    replace_csv_column(temp_file_path, temp_file_bis_path, 3, instrument_default_cadence)
    replace_csv_column(temp_file_bis_path, cesium_file, 4, instrument_default_active_fov)

    temp_file.close()
    temp_file_bis.close()

def repair_obs_cov(input, output):
    replace_csv_column(input, output, 4, instrument_default_active_fov)

