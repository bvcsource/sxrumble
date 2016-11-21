# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: Apache 2.0, see LICENSE for more details.

import sys
from unittest.mock import patch

import pytest
from docopt import DocoptExit

from sxrumble.cli import (
    entry_point, parse_argv, should_use_colors, rename_args, rename_key,
)
from sxrumble.exceptions import ValidationError


def test_entry_point():
    with patch('sxrumble.cli.main') as main:
        entry_point()
    assert main.call_args == ((sys.argv,), {})


@pytest.mark.parametrize('arg', ['-h', '--help'])
def test_parse_argv_help(capsys, arg):
    with pytest.raises(SystemExit):
        parse_argv([arg])
    out, err = capsys.readouterr()
    assert 'Show help' in out
    assert err == ''


@pytest.mark.parametrize('arg', ['-v', '--version'])
def test_parse_argv_version(capsys, arg):
    with pytest.raises(SystemExit):
        parse_argv([arg])
    out, err = capsys.readouterr()
    assert 'SXRumble v' in out
    assert err == ''


def test_parse_argv_record_defaults():
    actual = parse_argv('record @indian v')
    expected = {
        'record': True,
        'sx_url': '@indian',
        'volumes': ['v'],
        '': False,
        'help': False,
        'version': False,
        'color': False,
        'no_color': False,
        'threads': '8',
        'min_size': '1K',
        'max_size': '1M',
        'entropy_size': None,
        'entropy_seed': None,
        'replay': False,
        'session_file': None,
    }
    assert actual == expected


@pytest.mark.parametrize('argv', [
    '',
    'record',
    'record @indian',
    'record @indian v -color --no-color',
    'record @indian v --threads',
    'record @indian v --min-size',
    'record @indian v --max-size',
    'record @indian v --entropy-size',
    'record @indian v --entropy-seed',
    'replay',
])
def test_parse_argv_invalid(argv):
    with pytest.raises(DocoptExit):
        parse_argv(argv)


@pytest.mark.parametrize('argv, expected', [
    (
        # Multiple volumes
        '@indian v1 v2',
        {'volumes': ['v1', 'v2']},
    ), (
        # Colors
        '@indian v --color',
        {
            'color': True,
            'no_color': False,
        },
    ), (
        # No colors
        '@indian v --no-color',
        {
            'no_color': True,
            'color': False,
        },
    ), (
        # Number of threads
        '@indian v --threads 32',
        {'threads': '32'},
    ), (
        # Number of threads
        '@indian v -t 32',
        {'threads': '32'},
    ), (
        # Can put options anywhere
        '@indian --threads 1 v',
        {'threads': '1'},
    ), (
        '@indian v --min-size 1K --max-size 1M',
        {
            'min_size': '1K',
            'max_size': '1M',
        },
    ), (
        '@indian v --entropy-size 10M',
        {'entropy_size': '10M'},
    ), (
        '@indian v --entropy-seed abcdefabcdef',
        {'entropy_seed': 'abcdefabcdef'},
    ),
])
def test_parse_argv_record(argv, expected):
    args = parse_argv('record ' + argv)
    for name in expected:
        assert args[name] == expected[name]


@pytest.mark.parametrize('argv, expected', [
    (
        'config.yaml',
        {'session_file': 'config.yaml'},
    ),
])
def test_parse_argv_replay(argv, expected):
    args = parse_argv('replay ' + argv)
    for name in expected:
        assert args[name] == expected[name]


def test_should_use_colors():
    isatty = object()
    with patch('sys.stdout.isatty', return_value=isatty) as isatty_spy:
        assert should_use_colors(False, True) is False
        assert should_use_colors(True, False) is True
        assert should_use_colors(False, False) is isatty
    assert isatty_spy.call_count == 1


def test_rename_args():
    args = {
        'FOO': 'a',
        '--foo-bar': 'b',
    }
    assert rename_args(args) == {
        'foo': 'a',
        'foo_bar': 'b',
    }


@pytest.mark.parametrize('key,expected', [
    ('SX_URL', 'sx_url'),
    ('--max-size', 'max_size'),
    ('--config', 'config'),
])
def test_rename_key(key, expected):
    assert rename_key(key) == expected
