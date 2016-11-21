# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: Apache 2.0, see LICENSE for more details.

from random import choice
from typing import Tuple, Dict, Any, Optional

from sxrumble.config import ENTROPY_SEED_LENGTH, ENTROPY_SEED_CHARACTERS
from sxrumble.exceptions import ValidationError


Args = Dict[str, Any]


def validate_args(args: Args) -> Args:
    valid = {}  # type: Args
    valid['sx_url'] = validate_sx_url(args['sx_url'])
    valid['volumes'] = [
        validate_volume(v) for v in args['volumes']
    ]
    valid['threads'] = validate_threads(args['threads'])
    valid['min_size'], valid['max_size'] = validate_sizes(
        args['min_size'],
        args['max_size'],
    )
    valid['entropy_size'] = validate_entropy_size(
        args['entropy_size'],
        valid['max_size'],
    )
    valid['entropy_seed'] = validate_entropy_seed(args['entropy_seed'])
    return valid


def validate_sx_url(url: str) -> str:
    error = ValidationError(
        "SX_URL should have one of following formats:\n" +
        "  sx://user@cluster.example.com\n" +
        "  @user",
    )

    if ' ' in url:
        raise error
    if url.startswith('@'):
        return url
    if url.startswith('sx://') \
            and '@' in url:
        return url
    raise error


def validate_volume(volume: str) -> str:
    if '/' in volume or ' ' in volume:
        raise ValidationError("Invalid volume name: " + volume)
    return volume


def validate_threads(threads: int) -> int:
    if threads < 1:
        raise ValidationError("Invalid number of threads")
    return threads


def validate_sizes(size1: int, size2: int) -> Tuple[int, int]:
    if size1 <= 0 or size2 <= 0:
        raise ValidationError("Size must be greater than 0")
    if size1 < size2:
        return size1, size2
    return size2, size1


def validate_entropy_size(size: Optional[int], max_file_size: int) -> int:
    if size is None:
        return 100 * max_file_size
    if size <= 0:
        raise ValidationError("Size must be greater than 0")
    return max(size, max_file_size)


def validate_entropy_seed(seed: Optional[str]) -> str:
    if seed is None:
        return generate_entropy_seed()
    seed = seed.lower()

    if len(seed) > ENTROPY_SEED_LENGTH:
        raise ValidationError(
            "Entropy seed length should not exceed {} characters"
            .format(ENTROPY_SEED_LENGTH),
        )

    for c in seed:
        if c not in ENTROPY_SEED_CHARACTERS:
            raise ValidationError(
                "Entropy seed should be a hexadecimal string",
            )
    return seed


def generate_entropy_seed() -> str:
    return ''.join(
        choice(ENTROPY_SEED_CHARACTERS)
        for _ in range(ENTROPY_SEED_LENGTH)
    )
