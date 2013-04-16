Installation
============

Requirements
------------

You'll need dbacl for the text classification:

.. code-block:: sh

    # aptitude install dbacl

Unprivileged Install
--------------------

And I'd like to suggest to install afew as your unprivileged user.
If you do, make sure `~/.local/bin` is in your path.

.. code-block:: sh

    $ python setup.py install --prefix=~/.local
    $ mkdir -p ~/.config/afew ~/.local/share/afew/categories
