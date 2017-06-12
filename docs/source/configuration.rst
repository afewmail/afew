Configuration
=============

Configuration File
------------------

Customization of tag filters takes place in afew's config file in
`~/.config/afew/config`.

NotMuch Config
--------------

afew tries to adapt to the new tag that notmuch sets on new email, but has
mostly been developed and used against the **new** tag.  To use that,
make sure that `~/.notmuch-config` contains:

.. code-block:: ini

    [new]
    tags=new

Filter Configuration
--------------------

You can modify filters, and define your own versions of the base Filter that
allow you to tag messages in a similar way to the `notmuch tag` command, using
the config file.  The default config file is:

.. code-block:: ini

    [SpamFilter]
    [KillThreadsFilter]
    [ListMailsFilter]
    [ArchiveSentMailsFilter]
    [InboxFilter]

See the :doc:`filters` page for the details of those filters and the custom
arguments they accept.

You can add filters based on the base filter as well.  These can be customised
by specifying settings beneath them.  The standard settings, which apply to all
filters, are:

message
  text that will be displayed while running this filter if the verbosity is high
  enough.

query
  the query to use against the messages, specified in standard notmuch format.
  Note that you don't need to specify the **new** tag - afew will add that when
  run with the `--new` flag.

tags
  the tags to add or remove for messages that match the query. Tags to add are
  preceded by a **+** and tags to remove are preceded by a **-**.  Multiple tags
  are separated by semicolons.

tags_blacklist
  if the message has one of these tags, don't add `tags` to it. Tags are
  separated by semicolons.

So to add the **deer** tag to any message to or from `antelope@deer.com` you
could do:

.. code-block:: ini

    [Filter.1]
    query = 'antelope@deer.com'
    tags = +deer
    message = Wild animals ahoy

You can also (in combination with the InboxFilter) have email skip the Inbox
by removing the new tag before you get to the InboxFilter:

.. code-block:: ini

    [Filter.2]
    query = from'pointyheaded@boss.com'
    tags = -new;+boss
    message = Message from above

Full Sample Config
------------------

Showing some sample configs is the easiest way to understand.  The 
`notmuch initial tagging page`_ shows a sample config:

.. _notmuch initial tagging page: http://notmuchmail.org/initial_tagging/

.. code-block:: sh

    # immediately archive all messages from "me"
    notmuch tag -new -- tag:new and from:me@example.com

    # delete all messages from a spammer:
    notmuch tag +deleted -- tag:new and from:spam@spam.com

    # tag all message from notmuch mailing list
    notmuch tag +notmuch -- tag:new and to:notmuch@notmuchmail.org

    # finally, retag all "new" messages "inbox" and "unread"
    notmuch tag +inbox +unread -new -- tag:new

The (roughly) equivalent set up in afew would be:

.. code-block:: ini

    [ArchiveSentMailsFilter]

    [Filter.spamcom]
    message = Delete all messages from spammer
    query = from:spam@spam.com
    tags = +deleted;-new

    [Filter.notmuch]
    message = Tag all messages from the notmuch mailing list
    query = to:notmuch@notmuchmail.org
    tags = +notmuch

    [InboxFilter]

Not that the queries do not generally include `tag:new` because this is implied when afew
is run with the `--new` flag.

The differences between them is that 

* the ArchiveSentMailsFilter will add the **sent** tag, as well as archiving the
  email.  And it will not archive email that has been sent to one of your own
  addresses.
* the InboxFilter does not add the **unread** tag.  But most mail clients will
  manage the unread status directly in maildir.

More Filter Examples
--------------------

Here are a few more example filters from github dotfiles:

.. code-block:: ini

    [Filter.1]
    query = 'sicsa-students@sicsa.ac.uk'
    tags = +sicsa
    message = sicsa

    [Filter.2]
    query = 'from:foosoc.ed@gmail.com OR from:GT Silber OR from:lizzie.brough@eusa.ed.ac.uk'
    tags = +soc;+foo
    message = foosoc

    [Filter.3]
    query = 'folder:gmail/G+'
    tags = +G+
    message = gmail spam

    # skip inbox
    [Filter.6]
    query = 'to:notmuch@notmuchmail.org AND (subject:emacs OR subject:elisp OR "(defun" OR "(setq" OR PATCH)'
    tags = -new
    message = notmuch emacs stuff
