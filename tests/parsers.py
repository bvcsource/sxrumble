# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: Apache 2.0, see LICENSE for more details.

import pytest

from sxrumble.exceptions import ValidationError
from sxrumble.parsers import (
    parse_args, parse_threads, parse_entropy_size, parse_size,
)


def test_parse_args():
    raw_args = {
        'sx_url': '@indian',
        'volumes': ['jungle'],
        'threads': '4',
        'min_size': '1KB',
        'max_size': '1MB',
        'entropy_size': None,
        'entropy_seed': 'c0ffee',
    }
    args = parse_args(raw_args)
    assert args == {
        'sx_url': raw_args['sx_url'],
        'volumes': raw_args['volumes'],
        'threads': 4,
        'min_size': 2 ** 10,
        'max_size': 2 ** 20,
        'entropy_size': None,
        'entropy_seed': raw_args['entropy_seed'],
    }


def test_parse_threads():
    assert parse_threads('1') == 1
    assert parse_threads(-1) == -1
    with pytest.raises(ValidationError):
        parse_threads('garbage')


def test_parse_entropy_size():
    assert parse_entropy_size(None) is None
    assert parse_entropy_size('1k') == 2 ** 10


def test_parse_size():
    kb = 1024
    assert parse_size('1K') == kb
    assert parse_size('1k') == kb
    assert parse_size('1KB') == kb
    assert parse_size('1kb') == kb

    assert parse_size('42K') == 42 * kb
    assert parse_size('1,5K') == 1.5 * kb
    assert parse_size('1.5K') == 1.5 * kb
    assert parse_size('1.5M') == 1.5 * 1024 * kb

    with pytest.raises(ValidationError):
        parse_size('garbage')
