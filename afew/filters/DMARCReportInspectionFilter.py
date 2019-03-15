# -*- coding: utf-8 -*-
# SPDX-License-Identifier: ISC
# Copyright (c) Amadeusz Zolnowski <aidecoe@aidecoe.name>

from __future__ import print_function, absolute_import, unicode_literals

import re
import tempfile
import xml.etree.ElementTree as ET
import zipfile

from .BaseFilter import Filter


class ReportFilesIterator:
    '''
    Iterator over DMARC reports files attached to the e-mail either directly or
    in ZIP files.

    Returns content of each document file (as bytes, not as string) which needs
    to be decoded from charset encoding.
    '''
    def __init__(self, message):
        self.message = message

    def __iter__(self):
        for part in self.message.get_message_parts():
            if part.get_content_type() == 'application/zip':
                with tempfile.TemporaryFile(suffix='.zip') as file:
                    file.write(part.get_payload(decode=True))
                    with zipfile.ZipFile(file) as zip_file:
                        for member_file in zip_file.infolist():
                            if member_file.filename.endswith('.xml'):
                                yield zip_file.read(member_file)
            elif part.get_content_type() == 'application/xml':
                yield part.get_payload(decode=True)


def and_dict(dict1, dict2):
    '''
    Apply logical conjunction between values of dictionaries of the same keys.

    Keys set must be identical in both dictionaries. Otherwise KeyError
    exception is raised.

    :param dict1: Dictionary of bool values.
    :param dict2: Dictionary of bool values.
    :returns: A dictionary with the same set of keys but with modified values.
    '''
    dict3 = {}
    for key in dict1.keys():
        dict3[key] = dict1[key] & dict2.get(key, False)
    return dict3


def has_failed(node):
    '''
    Check whether status is "failed".

    To avoid false positives check whether status is one of "pass" or "none".

    :param node: XML node holding status as text.
    :returns: Whether the status is reported as "failed".
    '''
    return (node.text.strip() not in ['pass', 'none'])


def read_auth_results(document):
    '''
    Parse DMARC document.

    Look for results for DKIM and SPF. If there's more than one record, return
    `True` only and only if all of the records of particular type (DKIM or SPF)
    are "pass".

    :returns: Results as a dictionary where keys are: `dkim` and `spf` and
    values are boolean values.
    '''
    results = {'dkim': True, 'spf': True}
    root = ET.fromstring(document)
    for record in root.findall('record'):
        auth_results = record.find('auth_results')
        if auth_results:
            dkim = auth_results.find('dkim')
            if dkim:
                dkim = dkim.find('result')
                results['dkim'] &= not has_failed(dkim)
            spf = auth_results.find('spf')
            if spf:
                spf = spf.find('result')
                results['spf'] &= not has_failed(spf)

    return results


class DMARCReportInspectionFilter(Filter):
    '''
    Inspect DMARC reports for DKIM and SPF status.
    '''
    def __init__(self,                     # pylint: disable=too-many-arguments
                 database,
                 dkim_ok_tag='dmarc/dkim-ok',
                 dkim_fail_tag='dmarc/dkim-fail',
                 spf_ok_tag='dmarc/spf-ok',
                 spf_fail_tag='dmarc/spf-fail'):
        super().__init__(database)
        self.dkim_tag = {True: dkim_ok_tag, False: dkim_fail_tag}
        self.spf_tag = {True: spf_ok_tag, False: spf_fail_tag}
        self.dmarc_subject = re.compile(r'^report domain:',
                                        flags=re.IGNORECASE)

    def handle_message(self, message):
        if not self.dmarc_subject.match(message.get_header('Subject')):
            return

        auth_results = {'dkim': True, 'spf': True}

        for file_content in ReportFilesIterator(message):
            document = file_content.decode('UTF-8')
            auth_results = and_dict(auth_results, read_auth_results(document))

        self.add_tags(message,
                      'dmarc',
                      self.dkim_tag[auth_results['dkim']],
                      self.spf_tag[auth_results['spf']])
