# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

import re
from datetime import datetime


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
