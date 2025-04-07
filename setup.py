# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

import os

from setuptools import setup, find_packages


def get_requires():
    if os.environ.get('TRAVIS') != 'true' and os.environ.get('READTHEDOCS') != 'True':
        yield 'notmuch2'
    yield 'chardet'
    yield 'dkimpy'

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='afew',
    use_scm_version={'write_to': 'afew/version.py'},
    description="An initial tagging script for notmuch mail",
    url="https://github.com/afewmail/afew",
    license="ISC",
    long_description=long_description,
    long_description_content_type="text/x-rst",
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
            'PropagateTagsByRegexInThreadFilter = afew.filters.PropagateTagsByRegexInThreadFilter:PropagateTagsByRegexInThreadFilter',
            'PropagateTagsInThreadFilter = afew.filters.PropagateTagsInThreadFilter:PropagateTagsInThreadFilter',
        ],
    },
    install_requires=list(get_requires()),
    tests_require=['freezegun'],
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
