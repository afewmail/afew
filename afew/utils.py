# -*- coding: utf-8 -*-
# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

from __future__ import print_function, absolute_import, unicode_literals

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
