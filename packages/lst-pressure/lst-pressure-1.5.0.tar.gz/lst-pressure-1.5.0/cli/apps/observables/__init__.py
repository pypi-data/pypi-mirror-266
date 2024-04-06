from typing import Self
from datetime import datetime, timedelta
import re
from conf import Conf, LocationProviderType
from lstpressure import LSTIntervalType as I, Observation, LST
from ..AppInterface import AppInterface
from ..aggregate import (
    parse_sql_query,
    execute_csvsql,
    execute_csvlook,
    quoted_existing_reports,
)
from logger import error
import sys
import pandas as pd
from io import StringIO

conf = Conf()

filter_mapping = {
    I.NIGHT.name: I.NIGHT,
    I.SUNRISE_SUNSET.name: I.SUNRISE_SUNSET,
    I.ALL_DAY.name: I.ALL_DAY,
    I.SUNSET_SUNRISE.name: I.SUNSET_SUNRISE,
    I.OBSERVATION_WINDOW.name: I.OBSERVATION_WINDOW,
}


def kebab_to_snake(input_string):
    return re.sub(r"-", "_", input_string)


def parseDateInput(input: str, current_date=None) -> str:
    """
    Handle relative date inputs
    """

    # Check if the input is a direct date
    if re.match(r"^\d{8}$", input):
        return input

    # Convert provided current_date from yyyymmdd format to datetime
    if current_date is not None:
        try:
            current_date = datetime.strptime(current_date, "%Y%m%d")
        except ValueError:
            raise ValueError("current_date must be in yyyymmdd format")
    else:
        current_date = datetime.now()
    input = input.upper()
    match = re.match(r"^([-+])(\d+)([DMY])$", input)
    if match:
        sign, value, unit = match.groups()
        value = int(value)

        if unit == "D":
            # Add or subtract days
            if sign == "+":
                new_date = current_date + timedelta(days=value)
            else:
                new_date = current_date - timedelta(days=value)
        elif unit == "M":
            # Add or subtract months
            if sign == "+":
                new_month = current_date.month - 1 + value
            else:
                new_month = current_date.month - 1 - value

            year = current_date.year + new_month // 12
            month = new_month % 12 + 1
            day = min(
                current_date.day,
                [
                    31,
                    (
                        29
                        if year % 4 == 0 and not year % 100 == 0 or year % 400 == 0
                        else 28
                    ),
                    31,
                    30,
                    31,
                    30,
                    31,
                    31,
                    30,
                    31,
                    30,
                    31,
                ][new_month % 12],
            )
            new_date = datetime(year, month, day)
        elif unit == "Y":
            # Add or subtract years
            if sign == "+":
                new_date = current_date.replace(year=current_date.year + value)
            else:
                new_date = current_date.replace(year=current_date.year - value)

        return new_date.strftime("%Y%m%d")

    # If the input format is unrecognized
    raise ValueError("Invalid input format")


class Observables(AppInterface):
    id = "observables"
    usage = "lstpressure observables -h"
    description = (
        "Generate a list of observables (slots where OPT observations can be observed)"
    )

    def __init__(self, parser) -> None:
        super().__init__(parser)

    def build(self) -> Self:
        self.parser.add_argument(
            "--start",
            type=str,
            required=False,
            default=datetime.today().strftime("%Y%m%d"),
            help="The start date in the format 'YYYYMMDD', or as a relative date (from today) in the form +|-iD|M|Y (example: \"+3D\"). Defaults to today",
            metavar="",
        )

        self.parser.add_argument(
            "--end",
            type=str,
            required=False,
            default=None,
            help="The end date in the format 'YYYYMMDD', or as a relative date (from --start) in the form +|-iD|M|Y (example: \"+1Y\"). Defaults to --start",
            metavar="",
        )

        self.parser.add_argument(
            "--input",
            required=False,
            type=str,
            help="Path to an OPT csv download. If this is omitted, provide the CSV file contents via stdin",
            metavar="",
        )

        self.parser.add_argument(
            "--output",
            type=str,
            help="Path to the output csv file",
            metavar="",
        )

        self.parser.add_argument(
            "--loc-provider",
            type=lambda s: s.upper(),
            choices=list(LocationProviderType.__members__),
            default="MEERKAT",
            help="Specify the location provider for calculating sun statistics and for calculating intervals. Choose between: ASTRAL or MEERKAT (default). MeerKAT: intervals calculated using sunrise/sunset values (including NIGHT), ASTRAL: intervals calculated using dawn, sunrise, sunset, dusk",
            metavar="",
        )

        filter_choices = [
            choice
            for choice in list(I.__members__)
            if choice.upper() != I.OBSERVATION_WINDOW.name.upper()
        ]
        self.parser.add_argument(
            "--filter",
            type=lambda s: kebab_to_snake(s.upper()),
            choices=filter_choices,
            default=None,
            required=False,
            metavar="",
            help=f"Select from: {', '.join(filter_choices)}. If multiple filters are passed, only the last filter value is used (multiple filters not supported)",
        )

        self.parser.add_argument(
            "--lat",
            metavar="D:M:S",
            default=None,
            nargs="?",
            type=str,
            help="The latitude for the observation in the format 'D:M:S'. Default is '-30:42:39.8' (for ASTRAL provider). Value must be quoted --lat=\"location\"",
        )

        self.parser.add_argument(
            "--long",
            metavar="D:M:S",
            default=None,
            nargs="?",
            type=str,
            help="The longitude for the observation in the format 'D:M:S'. Default is '21:26:38.0' (for ASTRAL provider). Value must be quoted --long=\"location\"",
        )

        self.parser.add_argument(
            "--aggregate",
            required=False,
            type=str,
            metavar="",
            help=f'Apply a SQL aggregation to the CSV before printing to a file/stdout, or apply a built-in aggregation: {quoted_existing_reports}. The CSV is provided as a relation called "stdin". SQLite and DuckDB engines are supported, include ".duckdb" in the filename or as a comment in the SQL to enable DuckDB engine. Functionality is provided by the excellent csvsql library',
        )

        self.parser.add_argument(
            "--pretty",
            required=False,
            default=False,
            action="store_true",
            help=f"Format CSV output using the csvlook tool (included in this CLI)",
        )

        return self

    def parse(self, args) -> Self:
        if args.lat or args.long:
            if LocationProviderType[args.loc_provider] == LocationProviderType.MEERKAT:
                error(
                    "The MEERKAT provider has set lat/long coordinates that can't be overriden. Either use a different loc-provider or don't specify --lat and --long"
                )
                exit(1)
        if args.loc_provider == "MEERKAT":
            conf.LATITUDE = None
            conf.LONGITUDE = None
        else:
            if args.lat and args.lat != "":
                conf.LATITUDE = args.lat
            if args.long and args.long != "":
                conf.LONGITUDE = args.long
        self.input = args.input
        self.start = parseDateInput(args.start)
        self.end = parseDateInput(args.end, self.start) if args.end else self.start
        conf.LOC_PROVIDER = LocationProviderType[args.loc_provider]

        filter_name = args.filter
        if filter_name and not filter_mapping.get(filter_name.upper()):
            error(
                f"Invalid filter name, valid options: {', '.join(list(filter_mapping.keys()))}"
            )
            exit(1)
        self.filter_value = (
            None if not filter_name else filter_mapping.get(filter_name.upper(), None)
        )

        self.output = args.output if args.output else None
        self.aggregate = args.aggregate if args.aggregate else None
        self.pretty = args.pretty if args.pretty else None
        return self

    def exe(self) -> None:
        sql = parse_sql_query(self.aggregate) if self.aggregate else None

        def observation_filter(observation: Observation):
            if self.filter_value in observation.utc_constraints:
                return True
            return False

        if not self.input:
            if not sys.stdin.isatty():
                input_data = sys.stdin.read()
                input = pd.read_csv(StringIO(input_data))
            else:
                error(
                    "No input provided. Please either provide a filepath (--input), or pipe a CSV-formatted string from stdin"
                )
                exit(1)
        else:
            input = self.input

        output_csv_string = LST(
            input,
            calendar_start=self.start,
            calendar_end=self.end,
            observation_filter=observation_filter if self.filter_value else None,
            latitude=conf.LATITUDE,
            longitude=conf.LONGITUDE,
        ).to_csv_string()

        output_string = (
            execute_csvsql(output_csv_string, sql, self.aggregate)
            if sql
            else output_csv_string
        )

        output_string = execute_csvlook(output_string) if self.pretty else output_string

        if self.output:
            with open(self.output, "w") as f:
                f.write(output_string)
        else:
            print(output_string)

# Automatically added by katversion
__version__ = '1.5.0'
