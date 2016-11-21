# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: Apache 2.0, see LICENSE for more details.

import logging
import sys
from typing import Callable

from docopt import docopt

from sxrumble import get_name_and_version
from sxrumble import runner
from sxrumble.config import Session
from sxrumble.exceptions import ValidationError
from sxrumble.logs import configure_logging
from sxrumble.parsers import parse_args


logger = logging.getLogger(__name__)


__doc__ = """
Usage:
  sxrumble record SX_URL VOLUMES... [--] [options] [-c | -C]
  sxrumble replay SESSION_FILE [-c | -C]
  sxrumble (-h | --help)
  sxrumble (-v | --version)

Generate activity on cluster SX_URL in VOLUMES.

Options:
  -h, --help                Show help
  -v, --version             Show version
  -c, --color               Enable colors [default if printing to terminal]
  -C, --no-color            Disable colors
  -t, --threads NUM         Number of threads to use [default: 8]
  --min-size SIZE           Minimum file size [default: 1K]
  --max-size SIZE           Maximum file size [default: 1M]
  --entropy-size SIZE       Size of an entropy for generating files. If not
                            specified, will equal to `100 * max-size`
  --entropy-seed SEED       Seed for the entropy file. This should be a
                            12-character hexadecimal string. If not specified,
                            a random seed will be used.
"""


def entry_point() -> None:
    main(sys.argv)


def main(argv: list) -> None:
    raw_args = parse_argv(argv[1:])

    use_colors = should_use_colors(
        raw_args['color'],
        raw_args['no_color'],
    )
    configure_logging(use_colors=use_colors)

    try:
        args = parse_args(raw_args)
        handle_cli(args)
    except ValidationError as e:
        message = "sxrumble: " + str(e)
        raise SystemExit(message)


def should_use_colors(enable: bool, disable: bool) -> bool:
    if enable is False and disable is False:
        return sys.stdout.isatty()
    return enable


def handle_cli(args: dict) -> None:
    if args['record'] is True:
        return handle_record_command(args)
    if args['replay'] is True:
        return handle_replay_command(args)
    raise NotImplementedError()


def handle_record_command(args: dict) -> None:
    session = Session.from_cli(args)
    runner.record_session(session)


def handle_replay_command(args: dict) -> None:
    session = Session.from_file(args['session_file'])
    runner.replay_session(session)


def parse_argv(argv: list) -> dict:
    parsed_args = docopt(
        __doc__,
        argv=argv,
        version=get_name_and_version(),
    )
    return rename_args(parsed_args)


def rename_args(args: dict) -> dict:
    return map_keys(rename_key, args)


def map_keys(f: Callable, d: dict) -> dict:
    return {f(k): v for k, v in d.items()}


def rename_key(key: str) -> str:
    return key \
        .lower() \
        .lstrip('-') \
        .replace('-', '_')
