Quick Start
===========

The steps to get up and running are:

* install the afew package
* create the config files
* add a notmuch post-new hook that calls afew

Install
-------

The following commands will get you going on Debian/Ubuntu systems:

.. code-block:: sh

    $ sudo aptitude install notmuch python-notmuch dbacl
    $ git clone git://github.com/teythoon/afew.git
    $ cd afew
    $ python setup.py install --prefix

Ensure that `~/.local/bin` is in your path. One way is to add the following to
your `~/.bashrc`:

.. code-block:: sh

    if [ -d ~/.local/bin ]; then
        PATH=$PATH:~/.local/bin
    fi

See :doc:`installation` for a more detailed guide.

Initial Config
--------------

Create the directories to hold the config files:

.. code-block:: sh

    $ mkdir -p ~/.config/afew ~/.local/share/afew/categories

Make sure that `~/.notmuch-config` reads:

.. code-block:: ini

    [new]
    tags=new

Put a list of filters into `~/.config/afew/config`:

.. code-block:: ini

    # This is the default filter chain
    [SpamFilter]
    [KillThreadsFilter]
    [ListMailsFilter]
    [ArchiveSentMailsFilter]
    [InboxFilter]

And create a post-new hook for notmuch.

.. code-block:: sh

    $ mkdir -p path/to/maildir/.notmuch/hooks
    $ touch path/to/maildir/.notmuch/hooks/post-new

Then edit the `post-new` file to contain:

.. code-block:: sh

    #!/bin/sh
    $HOME/.local/bin/afew --tag --new

Next Steps
----------

You can:

* add extra :doc:`filters` for more custom filtering
* make use of the :doc:`move_mode` to move your email between folders
* run afew against all your old mail by running `afew --tag --all`
* start :doc:`extending` afew
