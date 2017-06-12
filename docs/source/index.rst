Welcome to afew's documentation!
================================

`afew` is an initial tagging script for notmuch mail:

* http://notmuchmail.org/
* http://notmuchmail.org/initial_tagging/

Its basic task is to provide automatic tagging each time new mail is registered
with notmuch. In a classic setup, you might call it after `notmuch new` in an
offlineimap post sync hook or in the notmuch `post-new` hook.

It can do basic thing such as adding tags based on email headers or maildir
folders, handling killed threads and spam.

fyi: afew plays nicely with `alot`, a GUI for notmuch mail ;)

* https://github.com/pazz/alot

Contents:

.. toctree::
   :maxdepth: 2

   quickstart
   installation
   commandline
   configuration
   filters
   move_mode
   extending
   implementation

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

