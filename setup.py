#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
    'python-twitter',
    'numpy',
    'pytz',
    'python-dateutil',
    'tornado',
    'sqlalchemy'
]

test_requirements = [
    'pytest',
    'pytest-cov',
    'pytest-bdd',
    'pytest-xdist',
    'pytest-watch',
    'tox',
    'detox'
]

setup(
    name='quakeit',
    version='0.0.1',
    description='Loads data from twitter to show a live graph ' +
                'of earthquakes in Central Italy',
    long_description=readme + '\n\n' + history,
    author='Giuseppe Acito',
    author_email='giuseppe.acito@gmail.com',
    url='https://github.com/giupo/quakeit',
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    #package_dir={
    #    'quakeit': 'quakeit'
    #},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='quakeit',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
    ],
    cmdclass={'test': PyTest},
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
        'console_scripts': [
            'quakeit=quakeit.quakeit:main',
        ]
    },
)
