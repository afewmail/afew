"""Test suite for DKIMValidityFilter.
"""
from email.utils import make_msgid
from unittest import mock

import pytest
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

    - `get_header()` returns non-empty string. When testing with mocked
      function for verifying DKIM signature, DKIM signature doesn't matter as
      long as it's non-empty string.

    - `get_filenames()` returns list of non-empty string. When testing with
    mocked file open, it must just be non-empty string.

    - `get_message_id()` returns some generated message ID.
    """
    message = mock.Mock()
    message.get_header.return_value = 'sig'
    message.get_filenames.return_value = ['a']
    message.get_message_id.return_value = make_msgid()
    return message


@pytest.mark.asyncio
async def test_no_dkim_header():
    """Test message without DKIM-Signature header doesn't get any tags."""
    dkim_filter, tags = _make_dkim_validity_filter()
    message = _make_message()
    message.get_header.return_value = False

    with mock.patch("builtins.open", mock.mock_open(read_data=b"")):
        with mock.patch("afew.filters.DKIMValidityFilter.dkim.verify") as dkim_verify:
            dkim_verify.return_value = True
            await dkim_filter.handle_message(message)

    assert tags == set()


@pytest.mark.asyncio
async def test_dkim_all_ok():
    """Test message, with multiple files all having good signature, gets
    only 'dkim-ok' tag.
    """
    dkim_filter, tags = _make_dkim_validity_filter()
    message = _make_message()
    message.get_filenames.return_value = ["a", "b", "c"]

    with mock.patch("builtins.open", mock.mock_open(read_data=b"")):
        with mock.patch("afew.filters.DKIMValidityFilter.dkim.verify") as dkim_verify:
            dkim_verify.return_value = True
            await dkim_filter.handle_message(message)

    assert tags == {"dkim-ok"}


@pytest.mark.asyncio
async def test_dkim_all_fail():
    """Test message, with multiple files all having bad signature, gets
    only 'dkim-fail' tag.
    """
    dkim_filter, tags = _make_dkim_validity_filter()
    message = _make_message()
    message.get_filenames.return_value = ["a", "b", "c"]

    with mock.patch("builtins.open", mock.mock_open(read_data=b"")):
        with mock.patch("afew.filters.DKIMValidityFilter.dkim.verify") as dkim_verify:
            dkim_verify.return_value = False
            await dkim_filter.handle_message(message)

    assert tags == {"dkim-fail"}


@pytest.mark.asyncio
async def test_dkim_some_fail():
    """Test message, with multiple files but only some having bad
    signature, still gets only 'dkim-fail' tag.
    """
    dkim_filter, tags = _make_dkim_validity_filter()
    message = _make_message()
    message.get_filenames.return_value = ["a", "b", "c"]

    with mock.patch("builtins.open", mock.mock_open(read_data=b"")):
        with mock.patch("afew.filters.DKIMValidityFilter.dkim.verify") as dkim_verify:
            dkim_verify.side_effect = [True, False, True]
            await dkim_filter.handle_message(message)

    assert tags == {"dkim-fail"}


@pytest.mark.asyncio
async def test_dkim_dns_resolve_failure():
    """Test message, on which DNS resolution failure happens when verifying
    DKIM signature, gets only 'dkim-fail' tag.
    """
    dkim_filter, tags = _make_dkim_validity_filter()
    message = _make_message()

    with mock.patch("builtins.open", mock.mock_open(read_data=b"")):
        with mock.patch("afew.filters.DKIMValidityFilter.dkim.verify") as dkim_verify:
            dkim_verify.side_effect = dns.resolver.NoNameservers()
            await dkim_filter.handle_message(message)

    assert tags == {"dkim-fail"}


@pytest.mark.asyncio
async def test_dkim_verify_failed():
    """Test message, on which DKIM key parsing failure occurs, gets only
    'dkim-fail' tag.
    """
    dkim_filter, tags = _make_dkim_validity_filter()
    message = _make_message()

    with mock.patch("builtins.open", mock.mock_open(read_data=b"")):
        with mock.patch("afew.filters.DKIMValidityFilter.dkim.verify") as dkim_verify:
            dkim_verify.side_effect = dkim.KeyFormatError()
            await dkim_filter.handle_message(message)

    assert tags == {"dkim-fail"}


@mock.patch("afew.Database.Database.get_messages",
            return_value=[
                _make_message(),
                _make_message(),
                _make_message()
            ])
@pytest.mark.asyncio
async def test_dkim_validity_filter_run(get_messages):
    """Test filter run, on which runs a N coroutines for N messages
    """
    dkim_filter, tags = _make_dkim_validity_filter()
    message = _make_message()
    message.get_filenames.return_value = ["a", "b", "c"]

    with mock.patch("builtins.open", mock.mock_open(read_data=b"")):
        with mock.patch("afew.filters.DKIMValidityFilter.dkim.verify") as dkim_verify:
            dkim_verify.return_value = True
            await dkim_filter.run("")

    assert get_messages.called


@mock.patch("afew.Database.Database.get_messages", return_value=set())
@pytest.mark.asyncio
async def test_dkim_validity_filter_run_sets_query(get_messages):
    """Test filter run with a query attribute set
    """
    dkim_filter, tags = _make_dkim_validity_filter()

    # without the query attribute
    await dkim_filter.run("folder:archived")
    assert get_messages.call_args.args == ('folder:archived',)

    # with query attribute
    dkim_filter.query = "folder:inbox"
    await dkim_filter.run("folder:archived")
    assert get_messages.call_args.args == ('(folder:archived) AND (folder:inbox)',)

    # with query attribute and no query
    await dkim_filter.run("")
    assert get_messages.call_args.args == ('folder:inbox',)
