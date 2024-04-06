import argparse
import logging
from conf import Conf, LogLevel
from .apps import __all__ as app_lib
from lstpressure import __version__ as version

conf = Conf()


class CustomHelpFormatter(argparse.HelpFormatter):
    def _format_action(self, action):
        if isinstance(action, argparse._SubParsersAction):
            parts = []
            for subaction in action._choices_actions:
                parts.append(self._format_action(subaction))
            return "".join(parts)
        else:
            return super()._format_action(action)


def configure_logging(log_level):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    logging.basicConfig(level=numeric_level)


def cli():
    prog = "lstpressure"
    description = f"(NRF SARAO) LST Pressure v{version}"

    parser = argparse.ArgumentParser(
        prog=prog, description=description, formatter_class=CustomHelpFormatter
    )
    parser.add_argument("-v", "--version", action="version", version=version)
    parser.add_argument(
        "--debug", action="store_true", help='Show logs of "DEBUG" level or higher'
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help='Show logs of "INFO" level or higher (default)',
    )
    parser.add_argument(
        "--warn", action="store_true", help='Show logs of "WARN" level or higher'
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Output instructions for updating lstpressure",
    )

    module_parser = parser.add_subparsers(title="Modules", dest="command")

    # Build the CLI
    apps = {
        app.id[0:3]: app(
            module_parser.add_parser(
                app.id,
                usage=app.usage,
                description=app.description,
                help=app.description,
                aliases=[app.id[0:3]],
            )
        )
        for app in app_lib
    }
    args = parser.parse_args()

    if args.update:
        print(
            """(Docker) Please run the following command to pull the most recent Docker image:
    => docker pull ghcr.io/ska-sa/lst-pressure_dist:latest
"""
        )
        return

    # Override environment configuration
    if args.warn:
        conf.LOG_LEVEL = LogLevel.WARN
    if args.info:
        conf.LOG_LEVEL = LogLevel.INFO
    if args.debug:
        conf.LOG_LEVEL = LogLevel.DEBUG

    # Try get the application
    try:
        app = apps.get(args.command[0:3], None)
    except:
        app = None

    # If app not specified correctly then print help and exit
    if not app:
        parser.print_help()
        return

    # Otherwise execute the application
    app.parse(args).exe()

# Automatically added by katversion
__version__ = '1.5.0'
