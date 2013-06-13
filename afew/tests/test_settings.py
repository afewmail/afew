import unittest


class TestFilterSettings(unittest.TestCase):

    def test_all_filters_exist(self):
        from afew import Filter
        self.assertTrue(hasattr(Filter.all_filters, 'get'))

    def test_entry_point_registration(self):
        from afew import Filter

        class FakeRegistry(object):
            name = 'test'

            def load(self):
                return 'class'
        registry = Filter.FilterRegistry([FakeRegistry()])

        self.assertEquals('class', registry['test'])

    def test_all_builtin_filters_exist(self):
        from afew import Filter
        self.assertEquals(['FolderNameFilter',
                           'ArchiveSentMailsFilter',
                           'ClassifyingFilter',
                           'InboxFilter',
                           'SpamFilter',
                           'Filter',
                           'KillThreadsFilter',
                           'SentMailsFilter',
                           'HeaderMatchingFilter',
                           'ListMailsFilter'], Filter.all_filters.keys())
