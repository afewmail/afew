#
# Copyright (c) 2013 Patrick Gerken <do3cc@patrick-gerken.de>
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

import unittest


class TestFilterRegistry(unittest.TestCase):

    def test_all_filters_exist(self):
        from afew import FilterRegistry
        self.assertTrue(hasattr(FilterRegistry.all_filters, 'get'))

    def test_entry_point_registration(self):
        from afew import FilterRegistry

        class FakeRegistry(object):
            name = 'test'

            def load(self):
                return 'class'
        registry = FilterRegistry.FilterRegistry([FakeRegistry()])

        self.assertEqual('class', registry['test'])

    def test_all_builtin_FilterRegistrys_exist(self):
        from afew import FilterRegistry
        self.assertEqual(sorted(['FolderNameFilter',
                           'ArchiveSentMailsFilter',
                           'InboxFilter',
                           'SpamFilter',
                           'Filter',
                           'KillThreadsFilter',
                           'SentMailsFilter',
                           'HeaderMatchingFilter',
                           'ListMailsFilter']),
                          sorted(list(FilterRegistry.all_filters.keys())))

    def test_add_FilterRegistry(self):
        from afew import FilterRegistry
        try:
            FilterRegistry.all_filters['test'] = 'class'
            self.assertEqual('class', FilterRegistry.all_filters['test'])
        finally:
            del FilterRegistry.all_filters['test']
