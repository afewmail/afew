"""Test suite for DKIMValidityFilter.
"""
import unittest
from email.utils import make_msgid
from unittest import mock

from afew.Database import Database
from afew.filters.HeaderMatchingFilter import HeaderMatchingFilter

from notmuch.errors import NullPointerError


class _AddTags:  # pylint: disable=too-few-public-methods
    """Mock for `add_tags` method of base filter. We need to easily collect
    tags added by filter for test assertion.
    """
    def __init__(self, tags):
        self._tags = tags

    def __call__(self, message, *tags):
        self._tags.update(tags)


def _make_header_matching_filter():
    """Make `HeaderMatchingFilter` with mocked `HeaderMatchingFilter.add_tags`
    method, so in tests we can easily check what tags were added by filter
    without fiddling with db.
    """
    tags = set()
    add_tags = _AddTags(tags)
    header_filter = HeaderMatchingFilter(Database(), header="X-test", pattern="")
    header_filter.add_tags = add_tags
    return header_filter, tags


def _make_message(should_fail):
    """Make mock email Message.

    Mocked methods:

    - `get_header()` returns non-empty string. When testing with mocked
      function for verifying DKIM signature, DKIM signature doesn't matter as
      long as it's non-empty string.

    - `get_filenames()` returns list of non-empty string. When testing with
    mocked file open, it must just be non-empty string.

    - `get_message_id()` returns some generated message ID.
    """
    message = mock.Mock()
    if should_fail:
        message.get_header.side_effect = NullPointerError
    else:
        message.get_header.return_value = 'header'
    message.get_filenames.return_value = ['a']
    message.get_tags.return_value = ['a']
    message.get_message_id.return_value = make_msgid()
    return message


class TestHeaderMatchingFilter(unittest.TestCase):
    """Test suite for `HeaderMatchingFilter`.
    """
    @mock.patch('afew.filters.HeaderMatchingFilter.open',
                mock.mock_open(read_data=b''))
    def test_header_exists(self):
        """Test message with header that exists.
        """
        header_filter, tags = _make_header_matching_filter()
        message = _make_message(False)
        header_filter.handle_message(message)

        self.assertSetEqual(tags, set())

    @mock.patch('afew.filters.HeaderMatchingFilter.open',
                mock.mock_open(read_data=b''))
    def test_header_doesnt_exist(self):
        """Test message with header that exists.
        """
        header_filter, tags = _make_header_matching_filter()
        message = _make_message(True)
        header_filter.handle_message(message)

        self.assertSetEqual(tags, set())
