Filters
=======

The default filter set (if you don't specify anything in the config) is:

.. code-block:: ini

    [SpamFilter]
    [ClassifyingFilter]
    [KillThreadsFilter]
    [ListMailsFilter]
    [ArchiveSentMailsFilter]
    [InboxFilter]

These can be customised by specifying settings beneath them.  The standard settings are:

* `message` - text that will be displayed while running this filter if the verbosity is high enough.
* `query` - the query to use against the messages, specified in standard notmuch format
* `tags` - the tags to add to messages that match the query
* `tag_blacklist` - if the message has one of these tags, don't add `tags` to it

Note that most of the filters below set their own value for message, query
and/or tags, and some ignore some of the above settings.

SpamFilter
----------

This looks for the header `X-Spam-Flag` - if it finds it, the **spam** tag is set.
You can override the tag used for spam if you want.

The settings you can use are:

* `spam_tag` is the tag used to identify spam. It defaults to **spam**

ClassifyingFilter
-----------------

This filter will tag messages based on what it has learnt from seeing how you've
tagged messages in the past.  See :doc:`classification` for more details.

KillThreadsFilter
-----------------

If the new message has been added to a thread that has already been tagged
**killed** then add the **killed** tag to this message.  This allows for ignoring
all replies to a particular thread.

ListMailsFilter
---------------

This filter looks for the `List-Id` header, and if it finds it, adds the list
name as a tag, together with the tag **lists**.

ArchiveSentMailsFilter
----------------------

Basically does what says it on the tin.  Though more accurately, it looks for
emails that are from one of your addresses *and not* to any of your addresses.
It then adds the **sent** tag and removes the **inbox** tag.

InboxFilter
-----------

This removes the **new** tag, and adds the **inbox** tag, to any message that isn't
killed or spam.  (The new tags are set in your notmuch config, and default to
just **new**.)

FolderNameFilter
----------------

This looks at which folder each email is in and uses that name as a tag for the
email.  So if you have a procmail or sieve set up that puts emails in folders
for you, this might be useful.
