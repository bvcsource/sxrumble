# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: Apache 2.0, see LICENSE for more details.

VERSION = (0, 5, 0, 'dev')


def get_version() -> str:
    return 'v' + '.'.join(map(str, VERSION))


def get_name_and_version() -> str:
    return "SXRumble " + get_version()
