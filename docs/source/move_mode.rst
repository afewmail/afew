Move Mode
=========

Configuration Section
---------------------

Here is a full sample configuration for move mode:

.. code-block:: ini

    [MailMover]
    folders = INBOX Junk
    max_age = 15

    # rules
    INBOX = 'tag:spam':Junk 'NOT tag:inbox':Archive
    Junk = 'NOT tag:spam AND tag:inbox':INBOX 'NOT tag:spam':Archive

Below we explain what each bit of this means.

Rules
-----

First you need to specify which folders should be checked for mails that are to
be moved (as a whitespace separated list):

.. code-block:: ini

    folders = INBOX Junk

Then you have to specify rules that define move actions of the form

.. code-block:: ini

    <src> = ['<qry>':<dst>]+

Every mail in the `<src>` folder that matches a `<qry>` will be moved into the
assigned `<dst>` folder.

You can bind as many rules to a maildir folder as you deem necessary. Just add
them as elements of a (whitespace separated) list.

Please note, though, that you need to specify at least one rule for every folder
given by the `folders` option and at least one folder to check in order to use
the move mode.

.. code-block:: ini

    INBOX = 'tag:spam':Junk

will bind one rule to the maildir folder `INBOX` that states that all mails in
said folder that carry (potentially among others) the tag **spam** are to be moved
into the folder `Junk`.

With `<qry>` being an arbitrary notmuch query, you have the power to construct
arbitrarily flexible rules. You can check for the absence of tags and look out
for combinations of attributes:

.. code-block:: ini

    Junk = 'NOT tag:spam AND tag:inbox':INBOX 'NOT tag:spam':Archive

The above rules will move all mails in `Junk` that don't have the **spam** tag
but do have an **inbox** tag into the directory `INBOX`. All other mails not
tagged with **spam** will be moved into `Archive`.

Note how this example binds two rules to the source folder and how the sequence
in which the rules have been specified matters: If you were to specify the
second rule first, it would match *all* mails not tagged as 'spam' and then the
second rule would never be triggered. More on that under 'Limitations'.

Max Age
-------

You can limit the age of mails you want to move by setting the `max_age` option
in the configuration section. By providing

.. code-block:: ini

    max_age = 15

afew will only check mails at most 15 days old.

Limitations
-----------

**(1)** Rules don't manipulate tags.

.. code-block:: ini

    INBOX = 'NOT tag:inbox':Archive
    Junk = 'NOT tag:spam':INBOX

The above combination of rules might prove tricky, since you might expect
de-spammed mails to end up in `INBOX`. But since the `Junk` rule will *not* add
an **inbox** tag, the next run in move mode might very well move the matching
mails into `Archive`.

Then again, if you remove the **spam** tag and do not set an **inbox** tag, how
would you come to expect the mail would end up in your INBOX folder after
moving it? ;)

**(2)** There is no 1:1 mapping between folders and tags. And that's a feature. If
you tag a mail with two tags and there is a rule for each of them, the rule you
specified first will apply.

**(3)** The same principle applies if you bind two rules to a source of which one is
a prefix to the other. If rule A is more generic than rule B (as in 'easier to
satisfy', less specific), you want to give it *after* rule B, or else it will
consume all mails that would trigger rule B before that more specific rule may
apply.
