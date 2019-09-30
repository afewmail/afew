# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

from afew.filters.HeaderMatchingFilter import HeaderMatchingFilter


class SpamFilter(HeaderMatchingFilter):
    message = 'Tagging spam messages'
    header = 'X-Spam-Flag'
    pattern = 'YES'

    def __init__(self, database, tags='+spam', spam_tag=None, **kwargs):
        if spam_tag is not None:
            # this is for backward-compatibility
            tags = '+' + spam_tag
        kwargs['tags'] = [tags]
        super().__init__(database, **kwargs)
