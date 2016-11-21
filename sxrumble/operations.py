# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: Apache 2.0, see LICENSE for more details.

import logging
import os
import random
import subprocess
import time
from functools import partial
from subprocess import CompletedProcess
from typing import List, Union, Tuple, Type, Any  # noqa
from uuid import uuid4

from sxrumble.config import Config, ENTROPY_FILE_PATH
from sxrumble.logs import prepare_process_error_message


CommandArgs = List[str]
CommandInput = Union[str, bytes, None]
RunCommandArgs = Tuple[CommandArgs, CommandInput]


logger = logging.getLogger(__name__)


class Operation:

    def __init__(self, config: Config, **kwargs: Any) -> None:
        self.config = config

    @classmethod
    def randomize(cls, config: Config) -> 'Operation':
        return cls(config)

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    def serialize(self) -> dict:
        return {}

    def run(self) -> None:
        args, stdin = self.prepare_command()
        duration, proc = measure_command(args, stdin)
        if proc.returncode == 0:
            self.report_success(duration)
        else:
            self.report_error(proc)

    def prepare_command(self) -> RunCommandArgs:
        raise NotImplementedError()

    def report_success(self, duration: float) -> None:
        logger.debug(
            "%s finished in %.3fs",
            self.get_name(),
            duration,
        )

    def report_error(self, proc: CompletedProcess) -> None:
        message = prepare_process_error_message(
            self.get_name(),
            proc,
        )
        logger.error(message)


class ListUsers(Operation):

    def prepare_command(self) -> RunCommandArgs:
        args = ['sxacl', 'userlist', self.config.sx_url]
        return args, None


class ListVolumes(Operation):

    def prepare_command(self) -> RunCommandArgs:
        args = ['sxls', self.config.sx_url]
        return args, None


class ListFiles(Operation):

    def __init__(self, config: Config, *, volume: str) -> None:
        super().__init__(config)
        self.volume = volume

    @classmethod
    def randomize(cls, config: Config) -> 'ListFiles':
        return cls(
            config,
            volume=pick_volume(config),
        )

    def serialize(self) -> dict:
        return {'volume': self.volume}

    def prepare_command(self) -> RunCommandArgs:
        path = os.path.join(self.config.sx_url, self.volume)
        args = ['sxls', path]
        return args, None


class ShowVolumeAcl(Operation):

    def __init__(self, config: Config, *, volume: str) -> None:
        super().__init__(config)
        self.volume = volume

    @classmethod
    def randomize(cls, config: Config) -> 'ShowVolumeAcl':
        return cls(
            config,
            volume=pick_volume(config),
        )

    def serialize(self) -> dict:
        return {'volume': self.volume}

    def prepare_command(self) -> RunCommandArgs:
        path = os.path.join(self.config.sx_url, self.volume)
        args = ['sxacl', 'volshow', path]
        return args, None


class UploadNewFile(Operation):

    def __init__(
            self, config: Config, *, volume: str, filename: str, size: int,
            offset: int) -> None:
        super().__init__(config)
        self.volume = volume
        self.filename = filename
        self.size = size
        self.offset = offset

    @classmethod
    def randomize(cls, config: Config) -> 'UploadNewFile':
        size, offset = pick_size_and_offset(config)
        return cls(
            config,
            volume=pick_volume(config),
            filename=pick_filename(config),
            size=size,
            offset=offset,
        )

    def serialize(self) -> dict:
        return {
            'volume': self.volume,
            'filename': self.filename,
            'size': self.size,
            'offset': self.offset,
        }

    def prepare_command(self) -> RunCommandArgs:
        stdin = get_file_content(self.size, self.offset)
        sx_path = os.path.join(
            self.config.sx_url,
            self.volume,
            self.filename,
        )
        args = ['sxcp', '--no-progress', '-', sx_path]
        return args, stdin


def measure_command(args: CommandArgs, stdin: CommandInput) \
        -> Tuple[float, CompletedProcess]:
    start = time.monotonic()
    proc = run_command(args, stdin)
    duration = time.monotonic() - start
    return duration, proc


def run_command(args: CommandArgs, input: CommandInput = '') \
        -> CompletedProcess:
    return subprocess.run(
        args,
        input=input or '',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setpgrp,
    )


ALL_OPERATIONS = [
    ListUsers,
    ListVolumes,
    ListFiles,
    ShowVolumeAcl,
    UploadNewFile,
]  # type: List[Type[Operation]]
OPERATIONS_BY_NAME = {o.get_name(): o for o in ALL_OPERATIONS}


def pick_operation(config: Config) -> Operation:
    cls = random.choice(ALL_OPERATIONS)
    return cls.randomize(config)


def pick_volume(config: Config) -> str:
    return random.choice(config.volumes)


def pick_size_and_offset(config: Config) -> Tuple[int, int]:
    size = random.randint(
        config.min_size,
        config.max_size,
    )
    offset = random.randint(
        0,
        config.entropy_size - size,
    )
    return size, offset


def read_slice(filename: str, size: int, offset: int) -> bytes:
    with open(filename, 'rb') as f:
        f.seek(offset)
        return f.read(size)


get_file_content = partial(read_slice, ENTROPY_FILE_PATH)


def pick_filename(config: Config) -> str:
    return 'sxrumble-' + str(uuid4())


def get_random_bytes(size: int, seed: str) -> bytes:
    old_seed = random.getstate()
    random.seed(seed)
    try:
        return bytearray(random.getrandbits(8) for _ in range(size))
    finally:
        random.setstate(old_seed)
