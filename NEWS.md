afew 3.0.0 (2020-03-10)
=======================

MailMover: many fixes

  Previously, MailMover didn't properly preserve flags when renaming files, and
  moved all mail to `cur`. This was fixed. Also, MailMover gained a test suite.

New filters: PropagateTags[ByRegex]InThreadFilter

  These filters allow propagating tags set to a message to the whole thread.

New command line argument: --notmuch-args= in move mode

  In move mode, afew calls `notmuch new` after moving mails around. This
  prevents `afew -m` from being used in a pre-new hook in `notmuch`.

  Now it's possible to specify notmuch args, so something like `afew -m
  --notmuch-args=--no-hooks` can live happily in a pre-new hook.

Python 3.4 and 3.5 support dropped

  afew stopped supporting the older python versions 3.4 and 3.5, and removed
  some more Python 2 compatibility code. (`from __future__ import …`, utf-8
  headers, relative imports, …)

afew 2.0.0 (2019-06-16)
=======================

Python 2 support removed

  afew doesn't support Python 2 anymore, and all Python 2 specific compat hacks
  were removed.

Better support for whitespaces and quotes in folder names

  Previously, afew failed with folders containing quotes or namespaces. These
  are now properly escaped internally.

Support `MAILDIR` as fallback for database location

  In addition to reading notmuch databse location from notmuch config, afew now
  supports reading from the `MAILDIR` environment variable, like notmuch CLI
  does, too.

Support relative path for database location

  As of notmuch 0.28, a relative path may be provided for the database
  location. notmuch prepends `$HOME/` to the relative path. For feature
  parity, afew now supports the same methodology of prepending `$HOME/` if a
  relative path is provided.

Support for removing unread and read tags in filters

  In a filter rule, it was possible to add "unread" and "read" tags but
  not to remove them.

afew 1.3.0 (2018-02-06)
=======================

MeFilter added

  Add filter tagging mail sent directly to any of addresses defined in
  Notmuch config file: `primary_email` or `other_email`.
  Default tag is `to-me` and can be customized with `me_tag` option.

License comments replaced with SPDX-License-Identifier

  Where possible, license boilerplate comments were changed to just the
  SPDX-License-Identifier, while adding the license to the repo and referencing
  it in `setup.py`, too.

DMARCReportInspectionFilter added

  DMARC reports usually come in ZIP files. To check the report you have to
  unpack and search thru XML document which is very tedious. The filter tags the
  message as follows:

  if there's any SPF failure in any attachment, tag the message with
  "dmarc-spf-fail" tag, otherwise tag with "dmarc-spf-ok"

  if there's any DKIM failure in any attachment, tag the message with
  "dmarc-dkim-fail" tag, otherwise tag with "dmarc-dkim-ok"

DKIMValidityFilter added
  This filter verifies DKIM signatures of E-Mails with DKIM header, and adds
  `dkin-ok` or `dkin-fail` tags.


afew 1.2.0 (2017-08-07)
=======================

FolderNameFilter supporting mails in multiple directories

  FolderNameFilter now looks at all folders that a message is in when adding
  tags to it.

afew 1.1.0 (2017-06-12)
=======================

Classification system removed

  As of commit 86d881d948c6ff00a6475dee97551ea092e526a1, the classification
  system (--learn) was removed, as it was really broken. If someone wants to
  implement it properly in the future it would be much simpler to start from
  scratch.

afew 1.0.0 (2017-02-13)
=====================

Filter behaviour change

  As of commit d98a0cd0d1f37ee64d03be75e75556cff9f32c29, the ListMailsFilter
  does not add a tag named `list-id `anymore, but a new one called
  `lists/<list-id>`.

afew 0.1pre (2012-02-10)
========================

Configuration format change

  Previously the values for configuration entries with the key `tags`
  were interpreted as a whitespace delimited list of strings. As of
  commit e4ec3ced16cc90c3e9c738630bf0151699c4c087 those entries are
  split at semicolons (';').

  This changes the semantic of the configuration file and affects
  everyone who uses filter rules that set or remove more than one tag
  at once. Please inspect your configuration files and adjust them if
  necessary.
