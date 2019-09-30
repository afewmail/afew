# Copyright (c) Jens Neuhalfen <jens@neuhalfen.name>

from afew.filters.BaseFilter import Filter


class PropagateTagsInThreadFilter(Filter):
    """
    Propagate tags in threads. For each new message the mail thread is examined. If one of the
    configured tags is found, it is automatically attached to the new message.

    This enables a very easy workflow where entire threads can be tagged automatically.

    Config:

    [PropagateTagsInThreadFilter]
    propagate_tags = "project_A;billing;private"
    filter = not is:spam

    """

    def handle_message(self, message):
        for tag in self._propagate_tags:
            tag_query = 'thread:"%s" AND is:"%s"' % (message.get_thread_id(), tag)
            if self._filter:
                query = self.database.get_messages("(%s) AND (%s)" % (tag_query, self._filter))
            else:
                query = self.database.get_messages(tag_query)

            if len(list(query)):
                self.add_tags(message, tag)

    def __init__(self, database, propagate_tags="", filter=None, **kwargs):
        if filter:
            self.message = "Propagating tag(s) '%s' for messages matching '%s' to whole threads" % (
                propagate_tags, filter)
        else:
            self.message = "Propagating tag(s) '%s' to whole threads" % (propagate_tags,)

        self._filter = filter
        self._propagate_tags = [t for t in propagate_tags.split(";") if len(t) > 0]

        super(PropagateTagsInThreadFilter, self).__init__(database, **kwargs)
