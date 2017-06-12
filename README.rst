====
afew
====

|GithubTag| |TravisStatus|

About
-----

afew is an initial tagging script for notmuch mail:

* http://notmuchmail.org/
* http://notmuchmail.org/initial_tagging/

Its basic task is to provide automatic tagging each time new mail is registered
with notmuch. In a classic setup, you might call it after 'notmuch new' in an
offlineimap post sync hook.

It can do basic thing such as adding tags based on email headers or maildir
folders, handling killed threads and spam.

In move mode, afew will move mails between maildir folders according to
configurable rules that can contain arbitrary notmuch queries to match against
any searchable attributes.

fyi: afew plays nicely with alot, a GUI for notmuch mail ;)

* https://github.com/pazz/alot



Current NEWS
------------

afew is quite young, so expect a few user visible API or configuration
format changes, though I'll try to minimize such disruptive events.

Please keep an eye on NEWS.md for important news.



Features
--------

* spam handling (flush all tags, add spam)
* killed thread handling
* tags posts to lists with ``lists``, ``$list-id``
* autoarchives mails sent from you
* catchall -> remove ``new``, add ``inbox``
* can operate on new messages [default], ``--all`` messages or on custom
  query results
* can move mails based on arbitrary notmuch queries, so your sorting
  may show on your traditional mail client (well, almost ;))
* has a ``--dry-run`` mode for safe testing
* works with python 2.7, 3.1 and 3.2



Installation
------------

And I'd like to suggest to install afew as your unprivileged user.
If you do, make sure ``~/.local/bin`` is in your path.

.. code:: bash

  $ python setup.py install --prefix=~/.local
  $ mkdir -p ~/.config/afew ~/.local/share/afew/categories



Configuration
-------------

Make sure that ``~/.notmuch-config`` reads:

.. code:: ini

  [new]
  tags=new

Put a list of filters into ``~/.config/afew/config``:

.. code:: ini

  # This is the default filter chain
  [SpamFilter]
  [KillThreadsFilter]
  [ListMailsFilter]
  [ArchiveSentMailsFilter]
  [InboxFilter]

And configure rules to sort mails on your disk, if you want:

.. code:: ini

  [MailMover]
  folders = INBOX Junk
  max_age = 15

  # rules
  INBOX = 'tag:spam':Junk 'NOT tag:inbox':Archive
  Junk = 'NOT tag:spam AND tag:inbox':INBOX 'NOT tag:spam':Archive



Commandline help
----------------

.. code:: ini

  $ afew --help
  Usage: afew [options] [--] [query]

  Options:
    -h, --help            show this help message and exit

    Actions:
      Please specify exactly one action.

      -t, --tag           run the tag filters
      -m, --move-mails    move mail files between maildir folders

    Query modifiers:
      Please specify either --all or --new or a query string.

      -a, --all           operate on all messages
      -n, --new           operate on all new messages

    General options:
      -C NOTMUCH_CONFIG, --notmuch-config=NOTMUCH_CONFIG
                          path to the notmuch configuration file [default:
                          $NOTMUCH_CONFIG or ~/.notmuch-config]
      -e ENABLE_FILTERS, --enable-filters=ENABLE_FILTERS
                          filter classes to use, separated by ',' [default:
                          filters specified in afew's config]
      -d, --dry-run       don't change the db [default: False]
      -R REFERENCE_SET_SIZE, --reference-set-size=REFERENCE_SET_SIZE
                          size of the reference set [default: 1000]
      -T DAYS, --reference-set-timeframe=DAYS
                          do not use mails older than DAYS days [default: 30]
      -v, --verbose       be more verbose, can be given multiple times



Boring stuff
============

Simulation
----------
Adding ``--dry-run`` to any ``--tag`` or ``--sync-tags`` action prevents
modification of the notmuch db. Add some ``-vv`` goodness to see some
action.



Initial tagging
---------------
Basic tagging stuff requires no configuration, just run

.. code:: bash

  $ afew --tag --new

To do this automatically you can add the following hook into your
``~/.offlineimaprc``:

.. code:: ini
  postsynchook = ionice -c 3 chrt --idle 0 /bin/sh -c "notmuch new && afew --tag --new"



Tag filters
-----------
Tag filters are plugin-like modules that encapsulate tagging
functionality. There is a filter that handles the archiving of mails
you sent, one that handles spam, one for killed threads, one for
mailing list magic...

The tag filter concept allows you to easily extend afew's tagging
abilities by writing your own filters. Take a look at the default
configuration file (``afew/defaults/afew.config``) for a list of
available filters and how to enable filters and create customized
filter types.



Move mode
---------

To invoke afew in move mode, provide the ``--move-mails`` option on the
command line.  Move mode will respect ``--dry-run``, so throw in
``--verbose`` and watch what effects a real run would have.

In move mode, afew will check all mails (or only recent ones) in the
configured maildir folders, deciding whether they should be moved to
another folder.

The decision is based on rules defined in your config file. A rule is
bound to a source folder and specifies a target folder into which a
mail will be moved that is matched by an associated query.

This way you will be able to transfer your sorting principles roughly
to the classic folder based maildir structure understood by your
traditional mail server. Tag your mails with notmuch, call afew
``--move-mails`` in an offlineimap presynchook and enjoy a clean inbox
in your webinterface/GUI-client at work.

For information on how to configure rules for move mode, what you can
do with it and what you can't, please refer to ``docs/move_mode``.


Have fun :)


.. |GithubTag| image:: https://img.shields.io/github/tag/afewmail/afew.svg
    :target: https://travis-ci.org/afewmail/afew
.. |TravisStatus| image:: https://travis-ci.org/afewmail/afew.svg?branch=master
    :target: https://github.com/afewmail/afew/releases
