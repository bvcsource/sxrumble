# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: Apache 2.0, see LICENSE for more details.

import os
import subprocess
from unittest.mock import Mock, patch, mock_open

import pytest

from sxrumble import operations
from sxrumble.config import ENTROPY_FILE_PATH
from sxrumble.operations import (
    Operation, ListUsers, ListVolumes, ListFiles, ShowVolumeAcl, UploadNewFile,
)


@pytest.fixture
def config():
    return Mock(
        sx_url='@sx',
        volumes=['v1'],
        min_size=1,
        max_size=1,
        entropy_size=10,
    )


class CustomOperation(Operation):
    def prepare_command(self):
        return [], None


def test_operation_get_name():
    assert CustomOperation.get_name() == 'CustomOperation'


@pytest.mark.parametrize('rc,report_func_name', [
    (0, 'report_success'),
    (1, 'report_error'),
])
def test_operation_run(config, rc, report_func_name):
    operation = CustomOperation(config)
    ret = (0, Mock(returncode=rc))
    with patch('sxrumble.operations.measure_command', return_value=ret):
        with patch.object(operation, report_func_name) as report_func:
            operation.run()
    assert report_func.called is True


def test_list_users(config):
    args, stdin = ListUsers.randomize(config).prepare_command()
    assert args == ['sxacl', 'userlist', '@sx']
    assert stdin is None


def test_list_users_serialize(config):
    assert ListUsers(config).serialize() == {}


def test_list_volumes(config):
    args, stdin = ListVolumes.randomize(config).prepare_command()
    assert args == ['sxls', '@sx']
    assert stdin is None


def test_list_volumes_serialize(config):
    assert ListVolumes(config).serialize() == {}


def test_list_files(config):
    args, stdin = ListFiles.randomize(config).prepare_command()
    assert args == ['sxls', '@sx/v1']
    assert stdin is None


def test_list_files_serialize(config):
    assert ListFiles(config, volume='v').serialize() == {'volume': 'v'}


def test_show_volume_acl(config):
    args, stdin = ShowVolumeAcl.randomize(config).prepare_command()
    assert args == ['sxacl', 'volshow', '@sx/v1']
    assert stdin is None


def test_show_volume_acl_serialize(config):
    assert ShowVolumeAcl(config, volume='v').serialize() == {'volume': 'v'}


def test_upload_new_file(config):
    operation = UploadNewFile.randomize(config)
    file_content = '42'
    with patch('sxrumble.operations.get_file_content',
               return_value=file_content) as get_file_content:
        args, stdin = operation.prepare_command()
    assert get_file_content.call_args[0] == (operation.size, operation.offset)
    assert args == \
        ['sxcp', '--no-progress', '-', '@sx/v1/' + operation.filename]
    assert stdin == file_content


def test_upload_new_file_serialize(config):
    operation = UploadNewFile(
        config, volume='v', filename='f', size=1, offset=2)
    assert operation.serialize() == {
        'volume': 'v',
        'filename': 'f',
        'size': 1,
        'offset': 2,
    }


def test_measure_command():
    duration = 1.5
    proc = Mock()
    with patch('time.monotonic', side_effect=[0, duration]):
        with patch('sxrumble.operations.run_command', return_value=proc):
            result = operations.measure_command([], None)
    assert result == (duration, proc)


def test_run_command():
    result = Mock()
    args = ['ls', '-l', '.']
    with patch('subprocess.run', return_value=result) as subprocess_run:
        assert operations.run_command(args, input) is result
    assert subprocess_run.call_args[0] == (args,)
    assert subprocess_run.call_args[1] == {
        'input': input,
        'stdout': subprocess.PIPE,
        'stderr': subprocess.PIPE,
        'preexec_fn': os.setpgrp,
    }


def test_pick_operation():
    config = Mock()
    operation = Mock()
    with patch('random.choice', return_value=operation) as choice:
        operations.pick_operation(config)
    assert choice.call_args == ((operations.ALL_OPERATIONS,), {})
    assert operation.randomize.call_args == ((config,), {})


def test_pick_volume():
    volumes = ['v1', 'v2', 'v3']
    config = Mock(volumes=volumes)
    with patch('random.choice') as choice:
        operations.pick_volume(config)
    assert choice.call_args == ((volumes,), {})


def test_get_file_content():
    # It's just a parital
    assert operations.get_file_content.args == (ENTROPY_FILE_PATH,)
    assert operations.get_file_content.func is operations.read_slice


def test_pick_size_and_offset():
    size, offset = 30, 50
    config = Mock(
        min_size=10,
        max_size=100,
        entropy_size=1000,
    )

    with patch('random.randint', side_effect=[size, offset]) as randint:
        assert operations.pick_size_and_offset(config) == (size, offset)
    assert randint.call_args_list == [
        ((config.min_size, config.max_size), {}),
        ((0, config.entropy_size - size), {}),
    ]


def test_read_slice():
    filename = 'file'
    size = 10
    offset = 1
    open = mock_open(read_data='foo')
    with patch('sxrumble.operations.open', open):
        operations.read_slice(filename, size, offset)
    assert open.call_args == ((filename, 'rb'), {})
    f = open()
    assert f.seek.call_args == ((offset,), {})
    assert f.read.call_args == ((size,), {})


def test_pick_filename():
    config = Mock()
    with patch('sxrumble.operations.uuid4') as uuid4:
        name = operations.pick_filename(config)
    assert uuid4.call_args == ((), {})
    assert name.startswith('sxrumble-')
