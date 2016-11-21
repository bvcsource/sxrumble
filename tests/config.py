# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: Apache 2.0, see LICENSE for more details.

from unittest.mock import patch, mock_open

import pytest
import yaml

from sxrumble.config import Session, Config


@pytest.fixture
def args():
    return {
        'sx_url': '@indian',
        'volumes': ['v1', 'v2'],
        'threads': 4,
        'min_size': 1,
        'max_size': 2,
        'entropy_size': 200,
        'entropy_seed': 'abcdef',
    }


def test_session_from_args(args):
    session = Session.from_cli(args)
    for key in args:
        assert getattr(session.config, key) == args[key]
    assert session.operations is None


def test_session_from_file(args):
    contents = yaml.safe_dump({'config': args, 'operations': []})
    open = mock_open(read_data=contents)
    with patch('sxrumble.config.open', open):
        session = Session.from_file('filename')
    for key in args:
        if key == 'threads':
            # Replay session needs more threads than record session to be
            # accurate.
            assert session.config.threads == args['threads'] * 2
        else:
            assert getattr(session.config, key) == args[key]
    assert session.operations == []


def test_session_serialize(args):
    config = Config(**args)
    session = Session(config, [])
    assert session.serialize() == {
        'config': args,
        'operations': [],
    }
