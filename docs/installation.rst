Installation
============

Requirements
------------

afew works with python 3.6+, and requires notmuch and its python bindings.
On Debian/Ubuntu systems you can install these by doing:

.. code-block:: sh

    $ sudo aptitude install notmuch python-notmuch python-dev python-setuptools

Note: if you are installing `notmuch` using Homebrew on macOS, make sure
to run ``$ brew install --with-python3 notmuch``, because the brew formula
doesn't install python3 notmuch bindings by default.

Unprivileged Install
--------------------

It is recommended to install `afew` itself inside a virtualenv as an unprivileged
user, either via checking out the source code and installing via setup.py, or
via pip.

.. code:: bash

  # create and activate virtualenv
  $ python -m venv --system-site-packages .venv
  $ source .venv/bin/activate

  # install via pip from PyPI:
  $ pip install afew

  # or install from source:
  $ python setup.py install --prefix=~/.local


You might want to symlink `.venv/bin/afew` somewhere inside your path
(~/bin/ in this case):

.. code:: bash

  $ ln -snr .venv/bin/afew ~/.bin/afew

Building documentation
----------------------

Documentation can be built in various formats using Sphinx:

.. code:: bash

  # build docs into build/sphinx/{html,man}
  $ python setup.py build_sphinx -b html,man
