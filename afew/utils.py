# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals

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

import codecs
import re
import sys
import email
from datetime import datetime

signature_line_re = re.compile(r'^((--)|(__)|(==)|(\*\*)|(##))')
def strip_signatures(lines, max_signature_size = 10):
    r'''
    Strip signatures from a mail. Used to filter mails before
    classifying mails.

    :param lines: a mail split at newlines
    :type  lines: :class:`list` of :class:`str`
    :param max_signature_size: consider message parts up to this size as signatures
    :type  max_signature_size: int
    :returns: the mail with signatures stripped off
    :rtype:   :class:`list` of :class:`str`

    >>> strip_signatures([
    ...     'Huhu',
    ...     '--',
    ...     'Ikke',
    ... ])
    ['Huhu']
    >>> strip_signatures([
    ...     'Huhu',
    ...     '--',
    ...     'Ikke',
    ...     '**',
    ...     "Sponsored by PowerDoh\'",
    ...     "Sponsored by PowerDoh\'",
    ...     "Sponsored by PowerDoh\'",
    ...     "Sponsored by PowerDoh\'",
    ...     "Sponsored by PowerDoh\'",
    ... ], 5)
    ['Huhu']
    '''

    siglines = 0
    sigline_count = 0

    for n, line in enumerate(reversed(lines)):
        if signature_line_re.match(line):
            # set the last line to include
            siglines = n + 1

            # reset the line code
            sigline_count = 0

        if sigline_count >= max_signature_size:
            break

        sigline_count += 1

    return lines[:-siglines]


def extract_mail_body(message):
    r'''
    Extract the plain text body of the message with signatures
    stripped off.

    :param message: the message to extract the body from
    :type  message: :class:`notmuch.Message`
    :returns: the extracted text body
    :rtype:   :class:`list` of :class:`str`
    '''
    if hasattr(email, 'message_from_binary_file'):
        mail = email.message_from_binary_file(open(message.get_filename(), 'br'))
    else:
        if (3, 1) <= sys.version_info < (3, 2):
            fp = codecs.open(message.get_filename(), 'r', 'utf-8', errors='replace')
        else:
            fp = open(message.get_filename())
        mail = email.message_from_file(fp)

    content = []
    for part in mail.walk():
        if part.get_content_type() == 'text/plain':
            raw_payload = part.get_payload(decode=True)
            encoding = part.get_content_charset()
            if encoding:
                try:
                    raw_payload = raw_payload.decode(encoding, 'replace')
                except LookupError:
                    raw_payload = raw_payload.decode(sys.getdefaultencoding(), 'replace')
            else:
                raw_payload = raw_payload.decode(sys.getdefaultencoding(), 'replace')

            lines = raw_payload.split('\n')
            lines = strip_signatures(lines)

            content.append('\n'.join(lines))
    return '\n'.join(content)

def filter_compat(*args):
    r'''
    Compatibility wrapper for filter builtin.

    The semantic of the filter builtin has been changed in
    python3.x. This is a temporary workaround to support both python
    versions in one code base.
    '''
    return list(filter(*args))

def get_message_summary(message):
    when = datetime.fromtimestamp(float(message.get_date()))
    sender = get_sender(message)
    subject = message.get_header('Subject')
    return '[{date}] {sender} | {subject}'.format(date=when, sender=sender,
                                                  subject=subject)

def get_sender(message):
    sender = message.get_header('From')
    name_match = re.search('(.+) <.+@.+\..+>', sender)
    if name_match:
        sender = name_match.group(1)
    return sender
