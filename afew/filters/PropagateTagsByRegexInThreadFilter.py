# Copyright (c) Jens Neuhalfen <jens@neuhalfen.name>

import re
from itertools import chain

from afew.filters.BaseFilter import Filter


def _flatten(listOfLists):
    "Flatten one level of nesting"
    return chain.from_iterable(listOfLists)


class PropagateTagsByRegexInThreadFilter(Filter):
    """
    This filter enables a very easy workflow where entire threads can be tagged automatically.

    Assuming the following workflow: all messages for projects or releases should be tagged
    as "project/A", "project/B" respectively "release/1.0.1" or "release/1.2.0".

    In most cases replies to messages retain their context: the project, the release(s), ..

    The following config will propagate all project/... or release/... tags from a thread
    to all new messages.

        [PropagateTagsByRegexInThreadFilter.1]
        propagate_tags = project/.*
        # do not tag spam
        filter = not is:spam

        [PropagateTagsByRegexInThreadFilter.2]
        propagate_tags = release/.*

    Implementation spec: This filter will search through all (new) messages matched by ``filter``.
    For each message ``m`` found it goes through the messages thread an collects all assigned
    tags that match the regexp ``propagate_tags`` (``t``).

    All matching tags ``t`` are then assigned to the new message.
    """

    def handle_message(self, message):
        thread_query = 'thread:"%s"' % (message.get_thread_id(),)
        if self._filter:
            query = self.database.get_messages("(%s) AND (%s)" % (thread_query, self._filter))
        else:
            query = self.database.get_messages(thread_query)

        # the query can only be iterated once, then it is exhausted
        # https://git.notmuchmail.org/git?p=notmuch;a=blob;f=bindings/python/notmuch/messages.py;h=cae5da508f353f12cca585cb056c0b9ed92e29b3;hb=HEAD
        messages = list(query)

        # flatten  tags
        tags_in_thread_t = {m.get_tags() for m in messages}  # a set of Tags instances
        tags_in_thread = set(_flatten(tags_in_thread_t))

        # filter tags
        propagatable_tags_in_thread = {tag for tag in tags_in_thread if self._propagate_tags.fullmatch(tag)}

        if len(propagatable_tags_in_thread):
            self.add_tags(message, *propagatable_tags_in_thread)

    def __init__(self, database, propagate_tags, filter=None, **kwargs):
        if filter:
            self.message = "Propagating tag(s) matching regexp /%s/ from threads to (new) messages matching '%s'" % (
                propagate_tags, filter)
        else:
            self.message = "Propagating tag(s) matching regexp /%s/ from threads to (new) messages'" % (
                propagate_tags,)

        self._filter = filter
        self._propagate_tags = re.compile(propagate_tags)

        super(PropagateTagsByRegexInThreadFilter, self).__init__(database, **kwargs)
