# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: Apache 2.0, see LICENSE for more details.

import pytest

from sxrumble.config import ENTROPY_SEED_LENGTH, ENTROPY_SEED_CHARACTERS
from sxrumble.exceptions import ValidationError
from sxrumble.validators import (
    validate_args, validate_sx_url, validate_volume, validate_threads,
    validate_sizes, validate_entropy_size, validate_entropy_seed,
    generate_entropy_seed,
)


ONE_KB = 2 ** 10
ONE_MB = 2 ** 20


def test_validate_args():
    raw_args = {
        'sx_url': '@indian',
        'volumes': ['jungle'],
        'threads': 4,
        'min_size': ONE_KB,
        'max_size': ONE_MB,
        'entropy_size': None,
        'entropy_seed': 'c0ffee',
    }
    args = validate_args(raw_args)
    assert args == {
        'sx_url': raw_args['sx_url'],
        'volumes': raw_args['volumes'],
        'threads': raw_args['threads'],
        'min_size': raw_args['min_size'],
        'max_size': raw_args['max_size'],
        'entropy_size': 100 * ONE_MB,
        'entropy_seed': raw_args['entropy_seed'],
    }


def test_validate_sx_url():
    assert validate_sx_url('@indian') == '@indian'
    with pytest.raises(ValidationError):
        validate_sx_url('indian')

    url = 'sx://user@indian.skylable.com'
    assert validate_sx_url(url) == url
    with pytest.raises(ValidationError):
        validate_sx_url('sx://indian.skylable.com')

    with pytest.raises(ValidationError):
        validate_sx_url('sx://user@indian skylable com')


def test_validate_volume():
    assert validate_volume('jungle') == 'jungle'
    with pytest.raises(ValidationError):
        validate_volume('indian/jungle')

    assert validate_volume('pl.jungle') == 'pl.jungle'
    with pytest.raises(ValidationError):
        validate_volume('pl jungle')


def test_validate_threads():
    assert validate_threads(1) == 1
    with pytest.raises(ValidationError):
        validate_threads(0)


def test_validate_sizes():
    assert validate_sizes(ONE_KB, ONE_MB) == (ONE_KB, ONE_MB)
    assert validate_sizes(ONE_MB, ONE_KB) == (ONE_KB, ONE_MB)


def test_validate_sizes_invalid():
    with pytest.raises(ValidationError):
        validate_sizes(0, 1)
    with pytest.raises(ValidationError):
        validate_sizes(1, -1)


def test_validate_entropy_size_default():
    entropy_size = validate_entropy_size(None, ONE_MB)
    assert entropy_size == ONE_MB * 100


def test_validate_entropy_size():
    entropy_size = validate_entropy_size(ONE_KB, ONE_MB)
    assert entropy_size == ONE_MB

    entropy_size = validate_entropy_size(ONE_MB, ONE_KB)
    assert entropy_size == ONE_MB


def test_validate_entropy_size_invalid():
    with pytest.raises(ValidationError):
        validate_entropy_size(0, 1)
    with pytest.raises(ValidationError):
        validate_entropy_size(-1, 1)


@pytest.mark.parametrize('seed', (
    '0', '01', '9001', 'c0ffee', 'abcdefabcdef',
))
def test_validate_entropy_seed_valid(seed):
    assert validate_entropy_seed(seed) == seed


@pytest.mark.parametrize('seed', (
    'hello world', 'foo', 'abcdefabcdefa',
))
def test_validate_entropy_seed_invalid(seed):
    with pytest.raises(ValidationError):
        validate_entropy_seed(seed)


def test_validate_entropy_seed_lower():
    assert validate_entropy_seed('ABCDEF') == 'abcdef'


def test_validate_entropy_seed():
    seed = validate_entropy_seed(None)
    assert seed is not None
    assert validate_entropy_seed(seed) == seed


def test_generate_entropy_seed():
    seed = generate_entropy_seed()
    assert generate_entropy_seed() != seed
    assert len(seed) == ENTROPY_SEED_LENGTH
    for c in seed:
        assert c in ENTROPY_SEED_CHARACTERS
