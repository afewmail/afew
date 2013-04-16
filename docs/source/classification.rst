Classification
==============

In Action
---------

Let's train on an existing tag `spam`:

.. code-block:: sh

    $ afew --learn spam -- tag:spam

Let's build the reference category. This is important to reduce the
false positive rate. This may take a while...

.. code-block:: sh

    $ afew --update-reference

And now let's create a new tag from an arbitrary query result:

.. code-block:: sh

    $ afew -vv --learn sourceforge -- sourceforge

Let's see how good the classification is:

.. code-block:: sh

    $ afew --classify -- tag:inbox and not tag:killed
    Sergio López <slpml@sinrega.org> (2011-10-08) (bug-hurd inbox lists unread) --> no match
    Patrick Totzke <reply+i-1840934-9a702d09342dca2b120126b26b008d0deea1731e@reply.github.com> (2011-10-08) (alot inbox lists) --> alot
    [...]

As soon as you trained some categories, afew will automatically
tag your new mails using the classifier. If you want to disable this
feature, either use the `--enable-filters` option to override the default
set of filters or remove the files in your afew state dir:

.. code-block:: sh

    $ ls ~/.local/share/afew/categories
    alot juggling  reference_category  sourceforge  spam

You need to update the category files periodically. I'd suggest to run

.. code-block:: sh

    $ afew --update

on a weekly and

.. code-block:: sh

    $ afew --update-reference

on a monthly basis.
