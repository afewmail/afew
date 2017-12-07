# -*- coding: utf-8 -*-
# SPDX-License-Identifier: ISC
# Copyright (c) Amadeusz Zolnowski <aidecoe@aidecoe.name>

from __future__ import print_function, absolute_import, unicode_literals

import re
import tempfile
import xml.etree.ElementTree as ET
import zipfile

from .BaseFilter import Filter


class ReportFilesIterator(object):
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


class ReportParseError(Exception):
    '''
    The report is malformed.
    '''
    pass


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


def read_dmarc_results(document):
    '''
    Parse DMARC document.

    Look for results for DKIM and SPF. If there's more than one record, return
    `True` only and only if all of the records of particular type (DKIM or SPF)
    are "pass".

    :returns: Results as a dictionary where keys are: `dkim` and `spf` and
    values are boolean values.
    '''
    results = {'dkim': True, 'spf': True}

    try:
        root = ET.fromstring(document)
    except ET.ParseError:
        raise ReportParseError()

    try:
        for record in root.findall('record'):
            policy_evaluated = record.find('row').find('policy_evaluated')
            dkim = policy_evaluated.find('dkim')
            spf = policy_evaluated.find('spf')

            results['dkim'] &= dkim.text.strip() == 'pass'
            results['spf'] &= spf.text.strip() == 'pass'
    except AttributeError:
        raise ReportParseError()

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
        super(DMARCReportInspectionFilter, self).__init__(database)
        self.dkim_tag = {True: dkim_ok_tag, False: dkim_fail_tag}
        self.spf_tag = {True: spf_ok_tag, False: spf_fail_tag}
        self.dmarc_subject = re.compile(r'^report domain:',
                                        flags=re.IGNORECASE)

    def handle_message(self, message):
        if not self.dmarc_subject.match(message.get_header('Subject')):
            return

        dmarc_results = {'dkim': True, 'spf': True}

        try:
            for file_content in ReportFilesIterator(message):
                document = file_content.decode('UTF-8')
                dmarc_results = and_dict(dmarc_results,
                                         read_dmarc_results(document))

            self.add_tags(message,
                          'dmarc',
                          self.dkim_tag[dmarc_results['dkim']],
                          self.spf_tag[dmarc_results['spf']])
        except ReportParseError:
            self.add_tags(message, 'dmarc', 'dmarc/malformed')
