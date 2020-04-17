# SPDX-License-Identifier: ISC
# Copyright (c) Amadeusz Zolnowski <aidecoe@aidecoe.name>

"""
DKIM validator filter.

Verifies DKIM signature of an e-mail which has DKIM header.
"""

import logging

import dkim
import dns.exception

from afew.filters.BaseFilter import Filter


class DKIMVerifyError(Exception):
    """Failed to verify DKIM signature.
    """


def verify_dkim(path):
    """
    Verify DKIM signature of an e-mail file.

    :param path: Path to the e-mail file.
    :returns: Whether DKIM signature is valid or not.
    """
    with open(path, 'rb') as message_file:
        message_bytes = message_file.read()

    try:
        return dkim.verify(message_bytes)
    except (dns.exception.DNSException, dkim.DKIMException) as exception:
        raise DKIMVerifyError(str(exception)) from exception


class DKIMValidityFilter(Filter):
    """
    Verifies DKIM signature of an e-mail which has DKIM header.
    """
    message = 'Verify DKIM signature'
    header = 'DKIM-Signature'

    def __init__(self, database, ok_tag='dkim-ok', fail_tag='dkim-fail'):
        super().__init__(database)
        self.dkim_tag = {True: ok_tag, False: fail_tag}
        self.log = logging.getLogger('{}.{}'.format(
            self.__module__, self.__class__.__name__))

    def handle_message(self, message):
        if message.get_header(self.header):
            try:
                dkim_ok = all(map(verify_dkim, message.get_filenames()))
            except DKIMVerifyError as verify_error:
                self.log.warning(
                    "Failed to verify DKIM of '%s': %s "
                    "(marked as 'dkim-fail')",
                    message.get_message_id(),
                    verify_error
                )
                dkim_ok = False
            self.add_tags(message, self.dkim_tag[dkim_ok])
