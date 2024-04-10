"""CSV Command Line Interface module."""
import os
import sys
from argparse import ArgumentParser
from pathlib import Path

import spiceypy as spice

from .timeline.itl import obs_plan_to_obs_timeline
from .timeline.ptr import check_obs_metadata, set_obs_id
from .timeline.coverage import obs_plan_to_obs_cov
from .modelling import rpwi

from .utils.setup import get_version_from_setup_cfg
VERSION = get_version_from_setup_cfg()

def obs_plan_to_timeline(argv=None):
    """CLI to convert a OPL to an OTL structure."""
    parser = ArgumentParser(description=f'juice-phs-{VERSION} CLI - Convert Observation Plan (OPL) to Observation Timeline (OTL)')
    parser.add_argument('csv', help='Observation Plan (OPL) CSV input file.')
    parser.add_argument('-o', '--output', metavar='OUTPUT', default=os.getcwd(),
                        help='Output directory (default: Current).')
    parser.add_argument('-s', '--scenario', metavar='SCENARIO',
                        help='Scenario Identifier (default: E001).', default='E001_01')
    parser.add_argument('-i', '--iteration', metavar='ITERATION',
                        help='Iteration reference (default: S01P00).', default='S01P00')
    parser.add_argument('-u', '--utc', action='store_true',
                        help='File times as UTC (default: Relative to events).')

    args, _ = parser.parse_known_args(argv)

    # Check if the file exists
    if not (csv := Path(args.csv)).exists():
        sys.stderr.write(f'OPL not found: {csv}\n')
        sys.exit(1)

    if args.utc:
        relative = 'utc'
    else:
        relative = 'events'

    # Export CSV to OTL structure
    obs_plan_to_obs_timeline(csv, args.output, relative=relative, scenario_id=args.scenario, iteration=args.iteration)

    sys.stdout.write(f'OTL structure saved in: {args.output}\n')


def obs_plan_to_coverage(argv=None):
    """CLI to convert a OPL to an OTC structure."""
    parser = ArgumentParser(description=f'juice-phs-{VERSION} CLI - Convert Observation Plan (OPL) to Observation Timeline Coverage (OTC)')
    parser.add_argument('csv', help='Quick-Look Coverage input CSV input file')
    parser.add_argument('-o', '--output', metavar='OUTPUT', default=f'{os.getcwd()}{os.sep}qlc_output.csv',
                        help='Output file (default: otc_output.csv at current directory)')

    args, _ = parser.parse_known_args(argv)

    # Check if the file exists
    if not (csv := Path(args.csv)).exists():
        sys.stderr.write(f'OPL not found: {csv}\n')
        sys.exit(1)


    # Export CSV to QLC file
    obs_plan_to_obs_cov(csv, args.output)

    sys.stdout.write(f'OTC file saved as: {args.output}\n')


def rpwi_langmuir_probe_illumination(argv=None):
    """CLI to convert a OPL to an OTC structure."""
    parser = ArgumentParser(description=f'juice-phs-{VERSION} CLI - RPWI Langmuir Probe Illumination')
    parser.add_argument('meta_kernel', help='SPICE meta-kernel')
    parser.add_argument('utc_start', help='Start Time in UTC')
    parser.add_argument('utc_end', help='End Time in UTC')
    parser.add_argument('-p', '--plot', action='store_true',
                        help='Plot the LP Illumination time series')

    args, _ = parser.parse_known_args(argv)

    spice.furnsh(args.meta_kernel)

    output = f'rpwi_langmuir_probe_illumination_' \
             f'{"".join(filter(str.isdigit, args.utc_start))}_' \
             f'{"".join(filter(str.isdigit, args.utc_end))}.csv'

    rpwi.langmuir_probe_illumination(args.utc_start, args.utc_end, plot=args.plot, output=output)


def ptr_check(argv=None):
    """CLI to perform PTR checks."""
    parser = ArgumentParser(description=f'juice-phs-{VERSION} CLI - PTR Syntax Check')
    parser.add_argument('input', help='Input PTR')
    parser.add_argument('output', help='Output PTR')

    args, _ = parser.parse_known_args(argv)

    check_obs_metadata(args.input,'temp.ptx')
    set_obs_id('temp.ptx',args.output)
    os.remove('temp.ptx')



