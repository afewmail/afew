About
=====

afew is an initial tagging script for notmuch mail:

* http://notmuchmail.org/
* http://notmuchmail.org/initial_tagging/

Its basic task is to provide automatic tagging each time new mail is registered
with notmuch. In a classic setup, you might call it after 'notmuch new' in an
offlineimap post sync hook.

In addition to more elementary features such as adding tags based on email
headers or maildir folders, handling killed threads and spam, it can do some
heavy magic in order to /learn/ how to initially tag your mails based on their
content.

In sync mode, afew will sync tags back to the underlying maildir structure by
moving tagged mails between folders according to configurable rules.

fyi: afew plays nicely with alot, a GUI for notmuch mail ;)

* https://github.com/pazz/alot


Current NEWS
============

afew is quite young, so expect a few user visible API or configuration
format changes, though I'll try to minimize such disruptive events.

Please keep an eye on NEWS.md for important news.


Features
========

* text classification, magic tags aka the mailing list without server
* spam handling (flush all tags, add spam)
* killed thread handling
* tags posts to lists with `lists`, `$list-id`
* autoarchives mails sent from you
* catchall -> remove `new`, add `inbox`
* can operate on new messages [default], `--all` messages or on custom
  query results
* can sync tags to maildir folders, so your sorting will show on your
  traditional mail server (well, almost ;))
* has a `--dry-run` mode for safe testing
* works with both python2.7 and python3.2


Installation
============

You'll need dbacl for the text classification:

    # aptitude install dbacl

And I'd like to suggest to install afew as your unprivileged user.
If you do, make sure `~/.local/bin` is in your path.

    $ python setup.py install --prefix=~/.local
    $ mkdir -p ~/.config/afew ~/.local/share/afew/categories


Configuration
=============

Make sure that `~/.notmuch-config` reads:

```
[new]
tags=new
```

Put a list of filters into `~/.config/afew/config`:

```
# This is the default filter chain
[SpamFilter]
[ClassifyingFilter]
[KillThreadsFilter]
[ListMailsFilter]
[ArchiveSentMailsFilter]
[InboxFilter]
```

And configure rules to sync your tags back to disk, if you want:
~~~ snip ~~~
[TagSyncher]
folders = INBOX Junk
max_age = 15

#rules
INBOX = spam:Junk !inbox:Archive
Junk = !spam:Archive
~~~ snip ~~~


Commandline help
================

```
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
    -s, --sync-tags     sync tags to maildirs

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
```


Boring stuff
============

Simulation
----------
Adding `--dry-run` to any `--tag` or `--sync-tags` action prevents
modification of the notmuch db. Add some `-vv` goodness to see some
action.


Initial tagging
---------------
Basic tagging stuff requires no configuration, just run

    $ afew --tag --new

To do this automatically you can add the following hook into your
~/.offlineimaprc:

    postsynchook = ionice -c 3 chrt --idle 0 /bin/sh -c "notmuch new && afew --tag --new"


Tag filters
-----------
Tag filters are plugin-like modules that encapsulate tagging
functionality. There is a filter that handles the archiving of mails
you sent, one that handles spam, one for killed threads, one for
mailing list magic...

The tag filter concept allows you to easily extend afew's tagging
abilities by writing your own filters. Take a look at the default
configuration file (`afew/defaults/afew.config`) for a list of
available filters and how to enable filters and create customized
filter types.


Sync mode
---------
To invoke afew in sync mode, provide the --sync-tags option on the command line.
Sync mode will respect --dry-run, so throw in --verbose and watch what effects
a real run would have.

In sync mode, afew will check all mails (or only recent ones) in the configured
maildir folders, deciding whether they should be moved to another folder by
inspecting their tags. 

The decision is based on rules defined in your config file. A rule is bound to a
source folder and specifies a target folder into which a mail will be moved
that is or is not tagged with an associated tag.


-- Rules --

First you need to specify which folders should be synced (as a whitespace
separated list): 

~~~ snip ~~~
folders = INBOX Junk
~~~ snip ~~~

Then the option

~~~ snip ~~~
INBOX = spam:Junk
~~~ snip

will bind one rule to the maildir folder 'INBOX' that states that all mails in
said folder that carry (potentially among others) the tag 'spam' are to be moved
into the folder 'Junk'.

You can also check for the absence of tags:

~~~ snip ~~~
Junk = !spam:Archive
~~~ snip ~~~

Above rule will move all mails in 'Junk' that don't have the spam tag into the
directory 'Archive'.

You can bind as many rules to a maildir folder as you deem necessary and mix
positive and negative tags. Just provide additional rules for the same maildir
folder as a whitespace separated list:

~~~ snip ~~~
INBOX = spam:Junk !inbox:Archive juggling:sparetime work:office
~~~ snip ~~~

Just note that you need to specify at least one rule for every folder given
by the 'folders' option and at least one folder to sync in order to use the sync
mode.


-- Max Age --

If checking *all* the mails in a maildir folder *every* time you sync proves
problematic, you can limit the age of mails you wanna sync. By providing

~~~ snip ~~~
max_age = 15
~~~ snip ~~~

afew will only check mails at most 15 days old. This might help performance with
large maildir folders.


-- Limitations --

(1) Rules don't manipulate tags.

~~~ snip ~~~
INBOX = !inbox:Archive
Junk = !spam:INBOX
~~~ snip ~~~

Above combination of rules might prove tricky, since you might expect de-spammed
mails to end up in 'INBOX'. But since the 'Junk' rule *doesn't* add an inbox
tag, the next run in sync mode might very well move the matching mails into
'Archive'.

Then again, if you remove the spam tag and do not add an inbox tag, how would
you come to expect the mail would end up in your INBOX folder after a sync? ;)

(2) There is no 1:1 mapping between folders and tags. And that's a feature. If
you tag a mail with two tags and there is a rule for each of them, the rule you
specified first will apply.

(3) The rules syntax only supports atomic rules so far. I.e. you can emulate
disjunctions by binding several rules with different tags but the same target to
one source folder, but you cannot have conjunctions of tags.

~~~ snip ~~~
Junk = !spam,inbox:INBOX !spam,!inbox:Archive
~~~ snip ~~~

Above rules cannot be enforced at this point.


The real deal
=============

Let's train on an existing tag `spam`:

    $ afew --learn spam -- tag:spam

Let's build the reference category. This is important to reduce the
false positive rate. This may take a while...

    $ afew --update-reference

And now let's create a new tag from an arbitrary query result:

    $ afew -vv --learn sourceforge -- sourceforge

Let's see how good the classification is:

    $ afew --classify -- tag:inbox and not tag:killed
    Sergio López <slpml@sinrega.org> (2011-10-08) (bug-hurd inbox lists unread) --> no match
    Patrick Totzke <reply+i-1840934-9a702d09342dca2b120126b26b008d0deea1731e@reply.github.com> (2011-10-08) (alot inbox lists) --> alot
    [...]

As soon as you trained some categories, afew will automatically
tag your new mails using the classifier. If you want to disable this
feature, either use the `--enable-filters` option to override the default
set of filters or remove the files in your afew state dir:

    $ ls ~/.local/share/afew/categories
    alot juggling  reference_category  sourceforge  spam

You need to update the category files periodically. I'd suggest to run

    $ afew --update

on a weekly and

    $ afew --update-reference

on a monthly basis.



Have fun :)
