Installation
============

Requirements
------------

afew works with python 2.7, 3.1 and 3.2, and requires notmuch and its python bindings.
On Debian/Ubuntu systems you can install these by doing:

.. code-block:: sh

    $ sudo aptitude install notmuch python-notmuch python-dev python-setuptools

Unprivileged Install
--------------------

And I'd like to suggest to install afew as your unprivileged user.

.. code-block:: sh

    $ python setup.py install --prefix=~/.local
    $ mkdir -p ~/.config/afew

If you do, make sure `~/.local/bin` is in your path, say by putting the
following in your `~/.bashrc`:

.. code-block:: sh

    if [ -d ~/.local/bin ]; then
        PATH=$PATH:~/.local/bin
    fi

If you want to do a system wide install you can leave off the `--prefix` option.
