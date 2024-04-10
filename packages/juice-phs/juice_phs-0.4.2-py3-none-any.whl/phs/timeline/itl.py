import csv
import tempfile

from pathlib import Path
from datetime import datetime, timedelta


def instrument_acronym(name):

    ins_dict = {'SOC' : 'SOC',
                'GALA' : 'GAL',
                'JANUS' : 'JAN',
                'JMAG' : 'MAG',
                'JMC' : 'JMC',
                'MAJIS' : 'MAJ',
                'NAVCAM' : 'NAV',
                'RADEM' : 'RAD',
                'PEP' : 'PEP',
                'PRIDE' : 'PRI',
                'RIME' : 'RIM',
                'RPWI' : 'RPW',
                'SWI' : 'SWI',
                'UVS' : 'UVS',
                '3GM': '3GM'
                }

    return ins_dict[name]


def parse_utc_datetime(utc_str):
    try:
        return datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        pass

    try:
        return datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        pass

    try:
        return datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        pass

    try:
        return datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        pass

    raise ValueError("Invalid UTC datetime format")


def convert_date(input_date, fmt=None):

    if fmt == 'eps':
        dt = parse_utc_datetime(input_date)
        output_date = dt.strftime("%d-%b-%Y_%H:%M:%S")
    else:
        dt = parse_utc_datetime(input_date)
        output_date = dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    return output_date


def format_timedelta(delta):

    total_seconds = delta.total_seconds()
    sign = '-' if total_seconds < 0 else ''
    total_seconds = abs(total_seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_time = f"{sign}{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    return formatted_time


def match_utc_time(utc_time, reference_times):
    closest_reference = None
    min_delta = timedelta.max

    for reference in reference_times:
        delta = utc_time - reference

        if abs(delta) < min_delta:
            min_delta = delta
            closest_reference = reference

    return closest_reference, min_delta


def ptr_times(instrument_timelines):
    '''Obtain the primes of the timeline.
    '''
    ptr_times = []
    for timeline in instrument_timelines.values():
        for obs in timeline:
            if "PRIME" in obs['DEFINITION'].upper():
                utc_str = obs['START_TIME']
                utc_end = obs['STOP_TIME']
                ptr_times.append(parse_utc_datetime(utc_str))
                ptr_times.append(parse_utc_datetime(utc_end))

    return sorted(ptr_times)


def generate_evf(instrument_timelines):

    evf_lines = str()
    evf_dict = {}
    times = ptr_times(instrument_timelines)
    count = 0

    for i in range(0, len(times), 2):
        count += 1

        utc_str = times[i].strftime("%d-%b-%Y_%H:%M:%S")
        utc_end = times[i+1].strftime("%d-%b-%Y_%H:%M:%S")

        evf_lines += f"{utc_str}    PTR_OBS_START              (COUNT =  {count})\n"
        evf_lines += f"{utc_end}    PTR_OBS_END                (COUNT =  {count})\n\n"

        evf_dict[times[i]] = ('PTR_OBS_START', count)
        evf_dict[times[i+1]] = ('PTR_OBS_END', count)

    return evf_lines, evf_dict


def parse_csv(filename, entity_column='SOURCE'):
    entities = {}
    columns = ['DEFINITION','START_TIME', 'STOP_TIME', 'NAME', 'SOURCE']
    with open(filename, 'r') as file:
        reader = csv.DictReader(filter(lambda row: row[0]!='#', file), fieldnames=columns)

        for row in reader:
            entity_value = row[entity_column]

            if entity_value not in entities:
                entities[entity_value] = []

            entities[entity_value].append(row)

    return entities


def obs_plan_to_obs_timeline(csvfile, output_dir, relative='events', scenario_id='E001_01', iteration='S01P01',
                             target='JUPITER'):

    instrument_timelines = parse_csv(csvfile)
    evf_lines, evf_dict = generate_evf(instrument_timelines)

    for timeline in instrument_timelines.values():

        otl_lines = str()
        sorted_timeline = sorted(timeline, key=lambda x: x['START_TIME'])

        for obs in sorted_timeline:
            source = obs['SOURCE']
            name = obs['NAME']
            if "PRIME" in obs['DEFINITION'].upper():
                prime = "(PRIME=TRUE)"
            else:
                prime = ""

            obs_header = f'#OBS_NAME={name} TARGET={target} SCENARIO={scenario_id}\n'
            otl_lines += obs_header

            if relative == 'events':

                utc_str = parse_utc_datetime(obs['START_TIME'])
                utc_end = parse_utc_datetime(obs['STOP_TIME'])
                reference_times = evf_dict.keys()

                str_closest, str_delta = match_utc_time(utc_str, reference_times)
                end_closest, end_delta = match_utc_time(utc_end, reference_times)

                str_ptr_count = evf_dict[str_closest]
                end_ptr_count = evf_dict[end_closest]

                str_delta = format_timedelta(str_delta)
                end_delta = format_timedelta(end_delta)

                otl_lines += f"{str_ptr_count[0]:13}  (COUNT = {str_ptr_count[1]:3})  {str_delta:>9}  " \
                             f"{source}   OBS_START  {name} {prime}\n"
                otl_lines += f"{end_ptr_count[0]:13}  (COUNT = {end_ptr_count[1]:3})  {end_delta:>9}  " \
                             f"{source}   OBS_END    {name}\n\n"

            else:

                utc_str = convert_date(obs['START_TIME'])
                utc_end = convert_date(obs['STOP_TIME'])

                otl_lines += f"{utc_str} {source}   OBS_START  {name} {prime}\n"
                otl_lines += f"{utc_end} {source}   OBS_END    {name}\n\n"

        try:
            ins_acr = instrument_acronym(source.strip())
        except:
            print(f'{obs["SOURCE"]} not processed.')
            continue

        # Export in a output file
        otl_name = f"OTL_{ins_acr}_{scenario_id}_{iteration}.itl"
        fname = Path(f"{output_dir}/{ins_acr}/{otl_name}")

        # Create parents folder if needed
        fname.parent.mkdir(parents=True, exist_ok=True)

        # Save the segments content
        fname.write_text(otl_lines, encoding='utf-8')

        fname = Path(f"{output_dir}/{ins_acr}/{otl_name.replace(iteration, 'SXXPYY')}")
        fname.write_text(otl_lines, encoding='utf-8')

    # Export in a output file
    evf_name = f"EVF_SOC_{scenario_id}_{iteration}.evf"
    fname = Path(f"{output_dir}/{evf_name}")

    # Create parents folder if needed
    fname.parent.mkdir(parents=True, exist_ok=True)

    # Save the segments content
    fname.write_text(evf_lines, encoding='utf-8')

    fname = Path(f"{output_dir}/{evf_name.replace(iteration, 'SXXPYY')}")
    fname.write_text(evf_lines, encoding='utf-8')

    # Create parents folder if needed
    # fname.parent.mkdir(parents=True, exist_ok=True)

    return
