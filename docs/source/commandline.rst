Command Line Usage
==================

Ultimately afew is a command line tool.  You have to specify an action, and
whether to act on all messages, or only on new messages.  The actions you can
choose from are:

tag
  run the tag filters.  See :ref:`Initial tagging`.

move-mails
  move mail files between maildir folders

learn=LEARN
  train the category with the messages matching the
  given query

update
  update the categories [requires no query]

update-reference
  update the reference category (takes quite some time)
  [requires no query]

classify
  classify each message matching the given query (to
  test the trained categories)

Initial tagging
---------------

Basic tagging stuff requires no configuration, just run

.. code-block:: sh

    $ afew --tag --new
    # or to tag *all* messages
    $ afew --tag --all

To do this automatically you can add the following hook into your
`~/.offlineimaprc`:

.. code-block:: ini

    postsynchook = ionice -c 3 chrt --idle 0 /bin/sh -c "notmuch new && afew --tag --new"

There is a lot more to say about general filter :doc:`configuration`
and the different :doc:`filters` provided by afew.

Simulation
^^^^^^^^^^

Adding `--dry-run` to any `--tag` or `--sync-tags` action prevents
modification of the notmuch db. Add some `-vv` goodness to see some
action.

Move Mode
---------

To invoke afew in move mode, provide the `--move-mails` option on the
command line.  Move mode will respect `--dry-run`, so throw in
`--verbose` and watch what effects a real run would have.

In move mode, afew will check all mails (or only recent ones) in the
configured maildir folders, deciding whether they should be moved to
another folder.

The decision is based on rules defined in your config file. A rule is
bound to a source folder and specifies a target folder into which a
mail will be moved that is matched by an associated query.

This way you will be able to transfer your sorting principles roughly
to the classic folder based maildir structure understood by your
traditional mail server. Tag your mails with notmuch, call afew
`--move-mails` in an offlineimap presynchook and enjoy a clean inbox
in your webinterface/GUI-client at work.

For information on how to configure rules for move mode, what you can
do with it and what you can't, please refer to :doc:`move_mode`.

Classify
--------

The `--learn`, `--update`, `--update-references` and `--classify` actions
all relate to learning how to filter your email.  See the
:doc:`classification` page for details.

Commandline help
----------------

The full set of options is:

.. code-block:: sh

    $ afew --help
    Usage: afew [options] [--] [query]

    Options:
      -h, --help            show this help message and exit

      Actions:
        Please specify exactly one action (both update actions can be
        specified simultaniously).

        -t, --tag           run the tag filters
        -l LEARN, --learn=LEARN
                            train the category with the messages matching the
                            given query
        -u, --update        update the categories [requires no query]
        -U, --update-reference
                            update the reference category (takes quite some time)
                            [requires no query]
        -c, --classify      classify each message matching the given query (to
                            test the trained categories)
        -m, --move-mails    move mail files between maildir folders

      Query modifiers:
        Please specify either --all or --new or a query string. The default
        query for the update actions is a random selection of
        REFERENCE_SET_SIZE mails from the last REFERENCE_SET_TIMEFRAME days.

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
