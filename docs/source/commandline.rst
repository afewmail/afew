Command Line Usage
==================

Ultimately afew is a command line tool.  You have to specify an action, and
whether to act on all messages, or only on new messages.  The actions you can
choose from are:

.. code-block:: sh

    --tag           run the tag filters
    --learn=LEARN   train the category with the messages matching the
                    given query
    --update        update the categories [requires no query]
    --update-reference
                    update the reference category (takes quite some time)
                    [requires no query]
    --classify      classify each message matching the given query (to
                    test the trained categories)
    --move-mails    move mail files between maildir folders

Initial tagging
---------------

Basic tagging stuff requires no configuration, just run

.. code-block:: sh

    $ afew --tag --new

To do this automatically you can add the following hook into your
`~/.offlineimaprc`:

.. code-block:: ini

    postsynchook = ionice -c 3 chrt --idle 0 /bin/sh -c "notmuch new && afew --tag --new"

Simulation
----------

Adding `--dry-run` to any `--tag` or `--sync-tags` action prevents
modification of the notmuch db. Add some `-vv` goodness to see some
action.

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
