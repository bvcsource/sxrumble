# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: Apache 2.0, see LICENSE for more details.

import logging
from concurrent.futures import (
    Executor, ThreadPoolExecutor, Future, CancelledError, wait,
    FIRST_COMPLETED,
)
from time import monotonic
from typing import Tuple, Set, Iterable  # noqa

from sxrumble.config import Session, Config, save_session_to_file
from sxrumble.operations import Operation, pick_operation


OperationInfo = Tuple[float, str, dict]


logger = logging.getLogger(__name__)


def record(session: Session) -> None:
    logger.info('Recording operations...')
    # Run and record operations
    start_time = monotonic()
    futures = start_threads_and_yield_futures(session.config)
    operation_infos = list(pick_results(futures, start_time))
    logger.info(
        "Ran %s operations in %.3fs",
        len(operation_infos),
        monotonic() - start_time,
    )

    # Save the session
    serialized_operations = [
        serialize_operation_info(start_time, info)
        for info in operation_infos
    ]
    session.set_operations(serialized_operations)
    filename = save_session_to_file(session)
    logger.info('Saved the session to %s', filename)


def start_threads_and_yield_futures(config: Config) -> Iterable[Future]:
    running = set()  # type: Set[Future]
    e = ThreadPoolExecutor(config.threads)
    try:
        while True:
            add_jobs_to_queue(config, e, running)
            done, running = wait(  # type: ignore
                running, return_when=FIRST_COMPLETED,
            )
            yield from done
    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt!")
        logger.warning("Waiting for jobs to finish...")
        e.shutdown()
        yield from running


def add_jobs_to_queue(
        config: Config, e: Executor, running: Set[Future]) -> None:
    while len(running) < config.threads:
        operation = pick_operation(config)
        future = e.submit(record_operation, operation)
        running.add(future)


def record_operation(operation: Operation) -> OperationInfo:
    started_at = monotonic()
    operation.run()
    return started_at, operation.get_name(), operation.serialize()


def pick_results(futures: Iterable[Future], start_time: float) \
        -> Iterable[OperationInfo]:
    for f in futures:
        try:
            yield f.result()
        except CancelledError:
            pass
        except:
            logger.error('Internal error!', exc_info=True)


def serialize_operation_info(time_offset: float, info: OperationInfo) -> dict:
    return {
        'time': info[0] - time_offset,
        'type': info[1],
        'params': info[2],
    }
