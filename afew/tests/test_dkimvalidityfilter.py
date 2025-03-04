"""Test suite for DKIMValidityFilter.
"""
import unittest
from email.utils import make_msgid
from unittest import mock

import dkim
import dns.exception

from afew.Database import Database
from afew.filters.DKIMValidityFilter import DKIMValidityFilter


class _AddTags:  # pylint: disable=too-few-public-methods
    """Mock for `add_tags` method of base filter. We need to easily collect
    tags added by filter for test assertion.
    """
    def __init__(self, tags):
        self._tags = tags

    def __call__(self, message, *tags):
        self._tags.update(tags)


def _make_dkim_validity_filter():
    """Make `DKIMValidityFilter` with mocked `DKIMValidityFilter.add_tags`
    method, so in tests we can easily check what tags were added by filter
    without fiddling with db.
    """
    tags = set()
    add_tags = _AddTags(tags)
    dkim_filter = DKIMValidityFilter(Database())
    dkim_filter.add_tags = add_tags
    return dkim_filter, tags


def _make_message():
    """Make mock email Message.

    Mocked methods:

    - `header()` returns non-empty string. When testing with mocked
      function for verifying DKIM signature, DKIM signature doesn't matter as
      long as it's non-empty string.

    - `filenames()` returns list of non-empty string. When testing with
    mocked file open, it must just be non-empty string.

    - `messageid` returns some generated message ID.
    """
    message = mock.Mock()
    message.header.return_value = 'sig'
    message.filenames.return_value = ['a']
    message.messageid = make_msgid()
    return message


class TestDKIMValidityFilter(unittest.TestCase):
    """Test suite for `DKIMValidityFilter`.
    """
    @mock.patch('afew.filters.DKIMValidityFilter.open',
                mock.mock_open(read_data=b''))
    def test_no_dkim_header(self):
        """Test message without DKIM-Signature header doesn't get any tags.
        """
        dkim_filter, tags = _make_dkim_validity_filter()
        message = _make_message()
        message.header.return_value = False

        with mock.patch('afew.filters.DKIMValidityFilter.dkim.verify') \
                as dkim_verify:
            dkim_verify.return_value = True
            dkim_filter.handle_message(message)

        self.assertSetEqual(tags, set())

    @mock.patch('afew.filters.DKIMValidityFilter.open',
                mock.mock_open(read_data=b''))
    def test_dkim_all_ok(self):
        """Test message, with multiple files all having good signature, gets
        only 'dkim-ok' tag.
        """
        dkim_filter, tags = _make_dkim_validity_filter()
        message = _make_message()
        message.filenames.return_value = ['a', 'b', 'c']

        with mock.patch('afew.filters.DKIMValidityFilter.dkim.verify') \
                as dkim_verify:
            dkim_verify.return_value = True
            dkim_filter.handle_message(message)

        self.assertSetEqual(tags, {'dkim-ok'})

    @mock.patch('afew.filters.DKIMValidityFilter.open',
                mock.mock_open(read_data=b''))
    def test_dkim_all_fail(self):
        """Test message, with multiple files all having bad signature, gets
        only 'dkim-fail' tag.
        """
        dkim_filter, tags = _make_dkim_validity_filter()
        message = _make_message()
        message.filenames.return_value = ['a', 'b', 'c']

        with mock.patch('afew.filters.DKIMValidityFilter.dkim.verify') \
                as dkim_verify:
            dkim_verify.return_value = False
            dkim_filter.handle_message(message)

        self.assertSetEqual(tags, {'dkim-fail'})

    @mock.patch('afew.filters.DKIMValidityFilter.open',
                mock.mock_open(read_data=b''))
    def test_dkim_some_fail(self):
        """Test message, with multiple files but only some having bad
        signature, still gets only 'dkim-fail' tag.
        """
        dkim_filter, tags = _make_dkim_validity_filter()
        message = _make_message()
        message.filenames.return_value = ['a', 'b', 'c']

        with mock.patch('afew.filters.DKIMValidityFilter.dkim.verify') \
                as dkim_verify:
            dkim_verify.side_effect = [True, False, True]
            dkim_filter.handle_message(message)

        self.assertSetEqual(tags, {'dkim-fail'})

    @mock.patch('afew.filters.DKIMValidityFilter.open',
                mock.mock_open(read_data=b''))
    def test_dkim_dns_resolve_failure(self):
        """Test message, on which DNS resolution failure happens when verifying
        DKIM signature, gets only 'dkim-fail' tag.
        """
        dkim_filter, tags = _make_dkim_validity_filter()
        message = _make_message()

        with mock.patch('afew.filters.DKIMValidityFilter.dkim.verify') \
                as dkim_verify:
            dkim_verify.side_effect = dns.resolver.NoNameservers()
            dkim_filter.handle_message(message)

        self.assertSetEqual(tags, {'dkim-fail'})

    @mock.patch('afew.filters.DKIMValidityFilter.open',
                mock.mock_open(read_data=b''))
    def test_dkim_verify_failed(self):
        """Test message, on which DKIM key parsing failure occurs, gets only
        'dkim-fail' tag.
        """
        dkim_filter, tags = _make_dkim_validity_filter()
        message = _make_message()

        with mock.patch('afew.filters.DKIMValidityFilter.dkim.verify') \
                as dkim_verify:
            dkim_verify.side_effect = dkim.KeyFormatError()
            dkim_filter.handle_message(message)

        self.assertSetEqual(tags, {'dkim-fail'})
