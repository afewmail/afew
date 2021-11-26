# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

import re
from datetime import datetime


def get_message_summary(message):
    when = datetime.fromtimestamp(float(message.date))
    sender = get_sender(message)
    try:
        subject = message.header('Subject')
    except LookupError:
        subject = ''
    return '[{date}] {sender} | {subject}'.format(date=when, sender=sender,
                                                  subject=subject)


def get_sender(message):
    try:
        sender = message.header('From')
    except LookupError:
        sender = ''
    name_match = re.search(r'(.+) <.+@.+\..+>', sender)
    if name_match:
        sender = name_match.group(1)
    return sender
