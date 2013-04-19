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

The standard filter :doc:`configuration` can be applied to these filters as
well. Though note that most of the filters below set their own value for
message, query and/or tags, and some ignore some of the standard settings.

SpamFilter
----------

The settings you can use are:

* spam_tag = <tag>

 * Add <tag> to all mails recognized as spam.
 * The default is 'spam'.
 * You may use it to tag your spam as 'junk', 'scum' or whatever suits your mood.
   Note that only a single tag is supported here.

Email will be considered spam if the header `X-Spam-Flag` is present.

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

The settings you can use are:

* sent_tag = <tag>

 * Add <tag> to all mails sent from one of your configured mail addresses.
 * The default is to add no tag.
 * Emails filtered by this filter have the **new** tag removed, so will not have
   the **inbox** tag added by the InboxFilter.
 * You may e.g. use it to tag all mails sent by you as 'sent'. This may make
   special sense in conjunction with a mail client that is able to not only search
   for threads but individual mails as well.

More accurately, it looks for emails that are from one of your addresses
*and not* to any of your addresses.

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

* folder_explicit_list = <folder list>

 * Tag mails with tag in <folder list> only. <folder list> is a space separated
   list, not enclosed in quotes or any other way.
 * Empty list means all folders (of course blacklist still applies).
 * The default is empty list.
 * You may use it e.g. to set tags only for specific folders like 'Sent'.

* folder_blacklist = <folder list>

 * Never tag mails with tag in <folder list>. <folder list> is a space separated
   list, not enclosed in quotes or any other way.
 * The default is to blacklist no folders.
 * You may use it e.g. to avoid mails being tagged as 'INBOX' when there is the more
   standard 'inbox' tag.

* folder_transforms = <transformation rules>

 * Transform folder names according to the specified rules before tagging mails.
   <transformation rules> is a space separated list consisting of
   'folder:tag' style pairs. The colon separates the name of the folder to be
   transformed from the tag it is to be transformed into.
 * The default is to transform to folder names.
 * You may use the rules e.g. to transform the name of your 'Junk' folder into your
   'spam' tag or fix capitalization of your draft and sent folder:

.. code-block:: ini

    folder transforms = Junk:spam Drafts:draft Sent:sent

* maildir_separator = <sep>

 * Use <sep> to split your maildir hierarchy into individual tags.
 * The default is to split on '.'
 * If your maildir hierarchy is represented in the filesystem as collapsed dirs,
   <sep> is used to split it again before applying tags. If your maildir looks
   like this:

.. code-block:: ini

   [...]
   /path/to/maildir/devel.afew/[cur|new|tmp]/...
   /path/to/maildir/devel.alot/[cur|new|tmp]/...
   /path/to/maildir/devel.notmuch/[cur|new|tmp]/...
   [...]

the mails in your afew folder will be tagged with 'devel' and 'afew'.

If instead your hierarchy is split by a more conventional '/' or any
other divider

.. code-block:: ini

   [...]
   /path/to/maildir/devel/afew/[cur|new|tmp]/...
   /path/to/maildir/devel/alot/[cur|new|tmp]/...
   /path/to/maildir/devel/notmuch/[cur|new|tmp]/...
   [...]

you need to configure that divider to have your mails properly tagged:

.. code-block:: ini

   maildir_separator = /

Customizing filters
-------------------

To customize these filters, there are basically two different
possibilities:

Let's say you like the SpamFilter, but it is way too polite

1. Create an filter object and customize it

.. code-block:: ini

    [SpamFilter.0] # note the index
    message = meh

The index is required iff you want to create a new SpamFilter *in
addition to* the default one. If you need just one customized
SpamFilter, you can drop the index and customize the default instance.

2. Create a new type...

.. code-block:: ini

    [ShitFilter(SpamFilter)]
    message = I hatez teh spam!

and create an object or two

.. code-block:: ini

    [ShitFilter.0]
    [ShitFilter.1]
    message = Me hatez it too.
