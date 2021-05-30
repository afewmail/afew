====
afew
====

|GithubTag| |CodeCov| |CI Status|

About
-----

afew is an initial tagging script for notmuch mail:

* http://notmuchmail.org/
* http://notmuchmail.org/initial_tagging/

Its basic task is to provide automatic tagging each time new mail is registered
with notmuch. In a classic setup, you might call it after 'notmuch new' in an
offlineimap post sync hook.

It can do basic thing such as adding tags based on email headers or maildir
folders, handling killed threads and spam.

In move mode, afew will move mails between maildir folders according to
configurable rules that can contain arbitrary notmuch queries to match against
any searchable attributes.

fyi: afew plays nicely with alot, a GUI for notmuch mail ;)

* https://github.com/pazz/alot



IRC
---

Feel free to ask your questions and discuss usage in the `#afewmail IRC Channel`_ on Libera.Chat.

.. _#afewmail IRC Channel: http://web.libera.chat/?channels=#afewmail


Features
--------

* spam handling (flush all tags, add spam)
* killed thread handling
* automatic propagation of tags to whole thread
* tags posts to lists with ``lists``, ``$list-id``
* autoarchives mails sent from you
* catchall -> remove ``new``, add ``inbox``
* can operate on new messages [default], ``--all`` messages or on custom
  query results
* can move mails based on arbitrary notmuch queries, so your sorting
  may show on your traditional mail client (well, almost ;))
* has a ``--dry-run`` mode for safe testing
* works with python 3.6+



Installation and Usage
----------------------

Full documentation is available in the `docs/`_ directory and in
rendered form at afew.readthedocs.io_.

.. _afew.readthedocs.io: https://afew.readthedocs.io/en/latest/
.. _docs/: docs/

Have fun :)


.. |GithubTag| image:: https://img.shields.io/github/tag/afewmail/afew.svg
    :target: https://github.com/afewmail/afew/releases
.. |CodeCov| image:: https://codecov.io/gh/afewmail/afew/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/afewmail/afew
.. |CI Status| image:: https://github.com/afewmail/afew/workflows/CI/badge.svg
    :target: https://github.com/afewmail/afew/actions
