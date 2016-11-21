# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: Apache 2.0, see LICENSE for more details.

import logging
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import Future  # noqa
from time import monotonic, sleep
from typing import List, Tuple

from sxrumble.config import Session, Config
from sxrumble.operations import OPERATIONS_BY_NAME, Operation


logger = logging.getLogger(__name__)
OperationAndDelay = Tuple[Operation, float]
OperationsAndDelays = List[OperationAndDelay]


def replay(session: Session) -> None:
    if not session.operations:
        raise SystemExit("No operations found!")

    logging.info("Preparing operations")
    operations_and_delays = get_operations_and_delays(session)

    logging.info("Replaying saved operations")
    start_time = monotonic()
    replay_operations(
        session.config,
        operations_and_delays,
        start_time,
    )
    logger.info(
        "Ran %s operations in %.3fs",
        len(session.operations),
        monotonic() - start_time,
    )


def replay_operations(
        config: Config,
        operations_and_delays: OperationsAndDelays,
        start_time: float,
) -> None:
    futures = []  # type: List[Future]
    with ThreadPoolExecutor(config.threads) as e:
        for operation, delay in operations_and_delays:
            future = e.submit(
                replay_operation,
                config,
                operation,
                start_time + delay,
            )  # type: Future
            futures.append(future)
    for f in futures:
        f.result()  # Raise errors, if any.


def replay_operation(config: Config, operation: Operation, start_at: float) \
        -> None:
    time_left = start_at - monotonic()
    if time_left < 0:
        logger.warning('%s starts %.3fs late', operation.get_name(), time_left)
    else:
        sleep(time_left)
    operation.run()


def get_operations_and_delays(session: Session) -> OperationsAndDelays:
    results = []  # type: OperationsAndDelays
    for info in session.operations or []:
        operation = deserialize_operation(session.config, info)
        results.append((operation, info['time']))
    return results


def deserialize_operation(config: Config, info: dict) -> Operation:
    operation_cls = OPERATIONS_BY_NAME[info['type']]
    return operation_cls(config, **info['params'])
