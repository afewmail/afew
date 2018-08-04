#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

import os
from setuptools import setup, find_packages
from sys import version_info

def get_requires():
    if os.environ.get('TRAVIS') != 'true' and os.environ.get('READTHEDOCS') != 'True':
        yield 'notmuch'
    yield 'chardet'
    yield 'dkimpy'

setup(
    name='afew',
    use_scm_version={'write_to': 'afew/version.py'},
    description="An initial tagging script for notmuch mail",
    url="https://github.com/afewmail/afew",
    license="ISC",
    setup_requires=['setuptools_scm'],
    packages=find_packages(),
    test_suite='afew.tests',
    package_data={
        'afew': ['defaults/afew.config']
    },
    entry_points={
        'console_scripts': [
            'afew = afew.commands:main'],
        'afew.filter': [
            'Filter = afew.filters.BaseFilter:Filter',
            'ArchiveSentMailsFilter = afew.filters.ArchiveSentMailsFilter:ArchiveSentMailsFilter',
            'DKIMValidityFilter = afew.filters.DKIMValidityFilter:DKIMValidityFilter',
            'DMARCReportInspectionFilter = afew.filters.DMARCReportInspectionFilter:DMARCReportInspectionFilter',
            'FolderNameFilter = afew.filters.FolderNameFilter:FolderNameFilter',
            'HeaderMatchingFilter = afew.filters.HeaderMatchingFilter:HeaderMatchingFilter',
            'InboxFilter = afew.filters.InboxFilter:InboxFilter',
            'KillThreadsFilter = afew.filters.KillThreadsFilter:KillThreadsFilter',
            'ListMailsFilter = afew.filters.ListMailsFilter:ListMailsFilter',
            'MeFilter = afew.filters.MeFilter:MeFilter',
            'SentMailsFilter = afew.filters.SentMailsFilter:SentMailsFilter',
            'SpamFilter = afew.filters.SpamFilter:SpamFilter',
        ],
    },
    install_requires=list(get_requires()),
    provides=['afew'],
    classifiers=[
        'License :: OSI Approved :: ISC License (ISCL)',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python',
        'Topic :: Communications :: Email',
        'Topic :: Communications :: Email :: Filters',
        'Topic :: Utilities',
        'Topic :: Database',
        ],
)
