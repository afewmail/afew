#!/usr/bin/env python
# coding = utf-8

#
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

import os
from setuptools import setup, find_packages
from sys import version_info

def get_requires():
    if os.environ.get('TRAVIS') != 'true':
        yield 'notmuch'
    yield 'chardet'
    if version_info < (3, 0):
        yield 'subprocess32'

setup(
    name='afew',
    use_scm_version={'write_to': 'afew/version.py'},
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
            'FolderNameFilter = afew.filters.FolderNameFilter:FolderNameFilter',
            'HeaderMatchingFilter = afew.filters.HeaderMatchingFilter:HeaderMatchingFilter',
            'InboxFilter = afew.filters.InboxFilter:InboxFilter',
            'KillThreadsFilter = afew.filters.KillThreadsFilter:KillThreadsFilter',
            'ListMailsFilter = afew.filters.ListMailsFilter:ListMailsFilter',
            'SentMailsFilter = afew.filters.SentMailsFilter:SentMailsFilter',
            'SpamFilter = afew.filters.SpamFilter:SpamFilter',
        ],
    },
    install_requires=list(get_requires()),
    provides=['afew'],
    classifiers=[
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
