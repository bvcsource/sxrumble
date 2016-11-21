# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: Apache 2.0, see LICENSE for more details.

from setuptools import find_packages, setup

from sxrumble import get_version


def get_requirements(path):
    with open(path, 'r') as f:
        content = f.read()
    return content.split()


if __name__ == '__main__':
    setup(
        name='sxrumble',
        author='Skylable Ltd.',
        version=get_version(),

        packages=find_packages(),
        install_requires=get_requirements('requirements.txt'),
        entry_points={
            'console_scripts': [
                'sxrumble=sxrumble.cli:entry_point',
            ],
        },
        include_package_data=True,
        license='Apache 2.0',
        classifiers=(
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.5',
        ),
    )
