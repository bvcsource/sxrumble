# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: Apache 2.0, see LICENSE for more details.

import os.path
from time import localtime, strftime
from typing import Any

import yaml


ENTROPY_FILE_PATH = os.path.expanduser('~/.sxrumble-entropy')
ENTROPY_SEED_LENGTH = 12
ENTROPY_SEED_CHARACTERS = '0123456789abcdef'


CONFIG_FIELDS = (
    'sx_url', 'volumes', 'threads', 'min_size', 'max_size', 'entropy_size',
    'entropy_seed',
)


class Session:

    def __init__(self, config: 'Config', operations: list = None) -> None:
        self._creation_time = localtime()
        self.config = config
        self.operations = operations

    @classmethod
    def from_cli(cls, args: dict) -> 'Session':
        config = Config(**args)
        return cls(config, None)

    @classmethod
    def from_file(cls, filename: str) -> 'Session':
        with open(filename) as f:
            payload = yaml.safe_load(f)

        config = Config(**payload['config'])
        # Replay session needs more threads than record session to be accurate.
        config.threads *= 2
        operations = payload['operations']
        return cls(config, operations)

    def serialize(self) -> dict:
        return {
            'config': self.config.serialize(),
            'operations': self.operations,
        }

    def set_operations(self, operations: list) -> None:
        assert self.operations is None
        operations.sort(key=lambda i: i['time'])
        self.operations = operations


class Config:

    def __init__(self, **kwargs: Any) -> None:
        from sxrumble.validators import validate_args
        kwargs = validate_args(kwargs)
        self.sx_url = kwargs['sx_url']
        self.volumes = kwargs['volumes']
        self.threads = kwargs['threads']
        self.min_size = kwargs['min_size']
        self.max_size = kwargs['max_size']
        self.entropy_size = kwargs['entropy_size']
        self.entropy_seed = kwargs['entropy_seed']

    def serialize(self) -> dict:
        return {name: getattr(self, name) for name in CONFIG_FIELDS}


def save_session_to_file(session: Session) -> str:
    payload = session.serialize()
    filename = 'sxrumble-{}.yaml'.format(
        strftime('%Y-%m-%d-%H:%M:%S', session._creation_time),
    )
    with open(filename, 'w') as f:
        yaml.safe_dump(payload, f, default_flow_style=False)
    return filename
