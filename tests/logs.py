# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: Apache 2.0, see LICENSE for more details.

import logging

from unittest.mock import Mock

from sxrumble.logs import (
    get_formatter, ColoredFormatter, prepare_process_error_message,
    maybe_decode, format_line,
)


def test_get_formatter():
    formatter = get_formatter(use_colors=False)
    assert type(formatter) == logging.Formatter


def test_get_colored_formatter():
    formatter = get_formatter(use_colors=True)
    assert type(formatter) == ColoredFormatter


def test_colored_formatter():
    formatter = ColoredFormatter(fmt='%(message)s')

    def color_format(level, msg):
        record = logging.LogRecord(
            level=level, msg=msg,
            name=None, pathname=None, lineno=None, args=None, exc_info=None,
        )
        return formatter.format(record)

    assert color_format(logging.DEBUG, 'foo') == 'foo'
    assert color_format(logging.INFO, 'foo') == '\033[34mfoo\033[0m'
    assert color_format(logging.WARNING, 'foo') == '\033[33mfoo\033[0m'
    assert color_format(logging.ERROR, 'foo') == '\033[35;1mfoo\033[0m'
    assert color_format(logging.CRITICAL, 'foo') == '\033[31;1mfoo\033[0m'


def test_prepare_process_error_message():
    proc = Mock(returncode=1, args=['ls'], stdout='', stderr='')
    assert prepare_process_error_message('test', proc) == \
        "test exited with 1:\n" + \
        " - args: ['ls']\n"

    proc = Mock(returncode=1, args=['ls', 'foo'], stdout='foo\n\n\n\n',
                stderr='foo\nbar\n')
    assert prepare_process_error_message('test', proc) == \
        "test exited with 1:\n" + \
        " - args: ['ls', 'foo']\n" + \
        " - stdout: foo\n" + \
        " - stderr:\n" + \
        "foo\n" + \
        "bar\n"


def test_maybe_decode():
    assert maybe_decode(b'foo') == 'foo'
    assert maybe_decode('foo') == 'foo'


def test_format_line():
    assert format_line('foo', 'bar') == ' - foo: bar\n'
    assert format_line('foo', 'bar') == ' - foo: bar\n'
    assert format_line('foo', 'bar\nbaz') == ' - foo:\nbar\nbaz\n'
