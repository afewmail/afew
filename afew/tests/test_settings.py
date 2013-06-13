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

        self.assertEquals('class', registry['test'])

    def test_all_builtin_FilterRegistrys_exist(self):
        from afew import FilterRegistry
        self.assertEquals(['FolderNameFilter',
                           'ArchiveSentMailsFilter',
                           'ClassifyingFilter',
                           'InboxFilter',
                           'SpamFilter',
                           'Filter',
                           'KillThreadsFilter',
                           'SentMailsFilter',
                           'HeaderMatchingFilter',
                           'ListMailsFilter'],
                          FilterRegistry.all_filters.keys())

    def test_add_FilterRegistry(self):
        from afew import FilterRegistry
        try:
            FilterRegistry.all_filters['test'] = 'class'
            self.assertEquals('class', FilterRegistry.all_filters['test'])
        finally:
            del FilterRegistry.all_filters['test']
