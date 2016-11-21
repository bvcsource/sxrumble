# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: Apache 2.0, see LICENSE for more details.

from typing import Dict, Any, Optional

import humanfriendly

from sxrumble.exceptions import ValidationError


def parse_args(args: Dict[str, str]) -> Dict[str, Any]:
    parsed_args = {}  # type: Dict[str, Any]
    parsed_args.update(args)
    parsed_args['threads'] = parse_threads(args['threads'])
    parsed_args['min_size'] = parse_size(args['min_size'])
    parsed_args['max_size'] = parse_size(args['max_size'])
    parsed_args['entropy_size'] = parse_entropy_size(args['entropy_size'])
    return parsed_args


def parse_threads(threads: str) -> int:
    try:
        return int(threads)
    except ValueError:
        raise ValidationError("Invalid number of threads")


def parse_entropy_size(size: Optional[str]) -> Optional[int]:
    if size is not None:
        return parse_size(size)


def parse_size(size: str) -> int:
    size = size.replace(',', '.')
    try:
        return humanfriendly.parse_size(size, binary=True)
    except humanfriendly.InvalidSize:
        raise ValidationError("Invalid size: " + size)
