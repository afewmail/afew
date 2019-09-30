# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

from afew.filters.HeaderMatchingFilter import HeaderMatchingFilter


class ListMailsFilter(HeaderMatchingFilter):
    message = 'Tagging mailing list posts'
    query = 'NOT tag:lists'
    pattern = r"<(?P<list_id>[a-z0-9!#$%&'*+/=?^_`{|}~-]+)\."
    header = 'List-Id'
    tags = ['+lists', '+lists/{list_id}']
