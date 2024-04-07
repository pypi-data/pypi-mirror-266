#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright by: P.J. Grochowski

import itertools
import shutil
import sys
from pathlib import Path
from typing import List, Tuple

from setuptools import Command, find_packages, setup

NAME_PACKAGE_ROOT = 'pkg'

DIR_ROOT = Path(__file__).resolve().parent
DIR_PACKAGE_ROOT = DIR_ROOT / NAME_PACKAGE_ROOT

sys.path.append(str(DIR_PACKAGE_ROOT))

from tunit import __package__, __version__


def assert_working_dir() -> None:
    currDir = Path().resolve()
    if currDir != DIR_ROOT:
        print(f"[ERROR]: Please change working directory: '{currDir}' -> '{DIR_ROOT}'")
        sys.exit(1)


def read_file(filePath: Path) -> str:
    with open(filePath) as fInput:
        return fInput.read()


def get_requirements() -> List[str]:
    fileRequirements = DIR_ROOT / 'requirements' / 'release.txt'
    return read_file(fileRequirements).splitlines()


def get_extra_requirements(tag: str) -> Tuple[str, List[str]]:
    fileRequirements = DIR_ROOT / 'requirements' / 'extra' / f'{tag}.txt'
    return tag, read_file(fileRequirements).splitlines()


class CmdDistClean(Command):
    description = "removes 'build', 'dist' and '<package>.egg-info' dirs with all of their contents"
    user_options = []

    def initialize_options(self) -> None:
        pass

    def finalize_options(self) -> None:
        pass

    def run(self) -> None:
        self._removeIfExists(DIR_ROOT / 'dist')
        self._removeIfExists(DIR_ROOT / 'build')
        self._removeIfExists(DIR_PACKAGE_ROOT / f'{__package__}.egg-info')

    def _removeIfExists(self, path: Path) -> None:
        if path.exists():
            print(f"Removing: {path}")
            shutil.rmtree(path)


def main():
    assert_working_dir()

    extra_requirements = dict([
        get_extra_requirements('json'),
        get_extra_requirements('yaml'),
    ])
    extra_requirements['all'] = list(itertools.chain.from_iterable(extra_requirements.values()))

    setup(
        name=__package__,
        version=__version__,
        license='MIT',
        url='https://bitbucket.org/massultidev/tunit/',
        author='P.J. Grochowski',
        author_email='pawel.grochowski.dev@gmail.com',
        description='Time unit types. For transparency safety and readability.',
        long_description=read_file(DIR_ROOT / 'README.md'),
        long_description_content_type='text/markdown',
        package_dir={'': NAME_PACKAGE_ROOT},
        packages=find_packages(NAME_PACKAGE_ROOT),
        include_package_data=True,
        zip_safe=False,
        install_requires=get_requirements(),
        extras_require=extra_requirements,
        python_requires='>=3.7',
        classifiers=[
            "Programming Language :: Python :: 3.7",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        cmdclass={
            'distclean': CmdDistClean,
        },
    )


if __name__ == '__main__':
    main()
