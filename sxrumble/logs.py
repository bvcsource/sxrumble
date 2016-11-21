# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: Apache 2.0, see LICENSE for more details.

import logging
import sys
from subprocess import CompletedProcess
from typing import Union


def configure_logging(*, use_colors: bool) -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = get_handler(use_colors=use_colors)
    logger.addHandler(handler)


def get_handler(*, use_colors: bool) -> logging.Handler:
    handler = logging.StreamHandler(sys.stdout)
    formatter = get_formatter(use_colors=use_colors)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    return handler


def get_formatter(*, use_colors: bool) -> logging.Formatter:
    if use_colors:
        return ColoredFormatter(
            fmt='[%(levelname)s %(asctime)s] %(message)s',
            datefmt='%H:%M:%S',
        )
    return logging.Formatter(
        fmt='[%(asctime)s %(levelname)s] %(message)s',
    )


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'INFO': '\033[34m',
        'WARNING': '\033[33m',
        'ERROR': '\033[35;1m',
        'CRITICAL': '\033[31;1m',
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        message = super(ColoredFormatter, self).format(record)
        level = record.levelname
        if level in self.COLORS:
            return self.COLORS[level] + message + self.RESET
        return message


def prepare_process_error_message(name: str, proc: CompletedProcess) -> str:
    message = "{} exited with {}:\n".format(
        name,
        proc.returncode,
    )

    message += format_line('args', str(proc.args))
    stdout = maybe_decode(proc.stdout).strip()
    if stdout != '':
        message += format_line('stdout', stdout)
    stderr = maybe_decode(proc.stderr).strip()
    if stderr != '':
        message += format_line('stderr', stderr)
    return message


def maybe_decode(s: Union[str, bytes]) -> str:
    return s.decode() if isinstance(s, bytes) else s


def format_line(name: str, message: str) -> str:
    connector = '\n' if '\n' in message else ' '
    return " - {name}:{connector}{message}\n".format(
        name=name,
        connector=connector,
        message=message.strip(),
    )
