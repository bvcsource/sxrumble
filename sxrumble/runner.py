# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: Apache 2.0, see LICENSE for more details.

import logging
import os.path
import subprocess
from functools import wraps
from typing import Callable

from sxrumble import get_name_and_version
from sxrumble import record, replay
from sxrumble.operations import get_random_bytes
from sxrumble.config import (
    ENTROPY_FILE_PATH, Session,
)


logger = logging.getLogger(__name__)


def make_runner(func: Callable) -> Callable:
    @wraps(func)
    def run(session: Session) -> None:
        setup(session)
        try:
            func(session)
        except SystemExit:
            raise
        except:
            logger.critical("Internal error!", exc_info=True)
        finally:
            cleanup(session)
    return run


record_session = make_runner(record.record)
replay_session = make_runner(replay.replay)


def setup(session: Session) -> None:
    logger.info(
        '%s, using %s threads',
        get_name_and_version(),
        session.config.threads,
    )
    logging.info("Emptying the volumes...")
    cleanup_volumes(session)

    logger.info('Preparing the entropy file...')
    prepare_entropy_file(session)


def cleanup(session: Session) -> None:
    os.remove(ENTROPY_FILE_PATH)


def prepare_entropy_file(session: Session) -> None:
    contents = get_random_bytes(
        session.config.entropy_size,
        session.config.entropy_seed,
    )
    with open(ENTROPY_FILE_PATH, 'wb') as f:
        f.write(contents)


def cleanup_volumes(session: Session) -> None:
    for volume in session.config.volumes:
        path = os.path.join(session.config.sx_url, volume, '*')
        output = subprocess.check_output(['sxls', path])
        if output:
            subprocess.check_call(['sxrm', path])
