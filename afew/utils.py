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
    name_match = re.search(r'(.+) <.+@.+\..+>', sender)
    if name_match:
        sender = name_match.group(1)
    return sender
