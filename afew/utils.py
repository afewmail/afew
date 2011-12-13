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

import re
import email

signature_line_re = re.compile(r'^((--)|(__)|(==)|(\*\*)|(##))')
def strip_signatures(lines, max_signature_size = 10):
    r'''
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
    for n, line in enumerate(reversed(lines)):
        if signature_line_re.match(line):
            return strip_signatures(lines[:-n - 1], max_signature_size)
        if n >= max_signature_size:
            break
    return lines

def extract_mail_body(message):
    mail = email.message_from_file(open(message.get_filename()))

    content = []
    for part in mail.walk():
        if part.get_content_type() == 'text/plain':
            raw_payload = part.get_payload(decode=True)
            encoding = part.get_content_charset()
            if encoding:
                try:
                    raw_payload = unicode(raw_payload, encoding, errors = 'replace')
                except LookupError:
                    raw_payload = unicode(raw_payload, errors = 'replace')
            else:
                raw_payload = unicode(raw_payload, errors = 'replace')

            lines = raw_payload.split('\n')
            lines = strip_signatures(lines)

            content.append('\n'.join(lines))
    return '\n'.join(content)

def filter_compat(*args):
    r'''
    Compatibility wrapper for filter builtin
    '''
    return list(filter(*args))
