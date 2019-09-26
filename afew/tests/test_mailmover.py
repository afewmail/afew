# SPDX-License-Identifier: ISC

import email.message
from email.utils import make_msgid
from freezegun import freeze_time
import mailbox
import notmuch
import os
import shutil
import tempfile
import unittest

from afew.Database import Database
from afew.NotmuchSettings import notmuch_settings, write_notmuch_settings

def create_mail(msg, maildir, notmuch_db, tags, old=False):
    email_message = email.message.EmailMessage()
    # freezegun doesn't handle time zones properly when generating UNIX
    # timestamps.  When the local timezone is UTC+2, the generated timestamp
    # is 2 hours ahead of what it should be.  Due to this we need to make sure
    # that the dates are always sufficiently far behind 2019-01-30 12:00 to
    # handle up to UTC+12 .
    if old:
        email_message['Date'] = 'Wed, 10 Jan 2019 13:00:00 +0100'
    else:
        email_message['Date'] = 'Wed, 20 Jan 2019 13:00:00 +0100'
    email_message['From'] = 'You <you@example.org>'
    email_message['To'] = 'Me <me@example.com>'
    email_message['Message-ID'] = make_msgid()
    email_message.set_content(msg)

    maildir_message = mailbox.MaildirMessage(email_message)
    message_key = maildir.add(maildir_message)

    fname = os.path.join(maildir._path, maildir._lookup(message_key))
    notmuch_msg = notmuch_db.add_message(fname)
    for tag in tags:
        notmuch_msg.add_tag(tag, False)

    # Remove the angle brackets automatically added around the message ID by make_msgid.
    stripped_msgid = email_message['Message-ID'].strip('<>')
    return (stripped_msgid, msg)


@freeze_time("2019-01-30 12:00:00")
class TestMailMover(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

        os.environ['MAILDIR'] = self.test_dir
        os.environ['NOTMUCH_CONFIG'] = os.path.join(self.test_dir, 'notmuch-config')

        notmuch_settings['database'] = {'path': self.test_dir}
        notmuch_settings['new'] = {'tags': 'new'}
        write_notmuch_settings()

        # Create notmuch database
        Database().open(create=True).close()

        self.root = mailbox.Maildir(self.test_dir)
        self.inbox = self.root.add_folder('inbox')
        self.archive = self.root.add_folder('archive')
        self.spam = self.root.add_folder('spam')

        # Dict of rules that are passed to MailMover.
        #
        # The top level key represents a particular mail directory to work on.
        #
        # The second level key is the notmuch query that MailMover will execute,
        # and its value is the directory to move the matching emails to.
        self.rules = {
            '.inbox': {
                'tag:archive AND NOT tag:spam': '.archive',
                'tag:spam': '.spam',
            },
            '.archive': {
                'NOT tag:archive AND NOT tag:spam': '.inbox',
                'tag:spam': '.spam',
            },
            '.spam': {
                'NOT tag:spam AND tag:archive': '.archive',
                'NOT tag:spam AND NOT tag:archive': '.inbox',
            },
        }


    def tearDown(self):
        shutil.rmtree(self.test_dir)


    @staticmethod
    def get_folder_content(db, folder):
        return {
            (os.path.basename(msg.get_message_id()), msg.get_part(1).decode())
            for msg in db.do_query('folder:{}'.format(folder)).search_messages()
        }


    def test_all_rule_cases(self):
        from afew import MailMover

        with Database() as db:
            expect_inbox = set([
                create_mail('In inbox, untagged\n', self.inbox, db, []),
                create_mail('In archive, untagged\n', self.archive, db, []),
                create_mail('In spam, untagged\n', self.spam, db, []),
            ])

            expect_archive = set([
                create_mail('In inbox, tagged archive\n', self.inbox, db, ['archive']),
                create_mail('In archive, tagged archive\n', self.archive, db, ['archive']),
                create_mail('In spam, tagged archive\n', self.spam, db, ['archive']),
            ])

            expect_spam = set([
                create_mail('In inbox, tagged spam\n', self.inbox, db, ['spam']),
                create_mail('In inbox, tagged archive, spam\n', self.inbox, db, ['archive', 'spam']),
                create_mail('In archive, tagged spam\n', self.archive, db, ['spam']),
                create_mail('In archive, tagged archive, spam\n', self.archive, db, ['archive', 'spam']),
                create_mail('In spam, tagged spam\n', self.spam, db, ['spam']),
                create_mail('In spam, tagged archive, spam\n', self.spam, db, ['archive', 'spam']),
            ])

        mover = MailMover.MailMover(quiet=True)
        mover.move('.inbox', self.rules['.inbox'])
        mover.move('.archive', self.rules['.archive'])
        mover.move('.spam', self.rules['.spam'])
        mover.close()

        with Database() as db:
            self.assertEqual(expect_inbox, self.get_folder_content(db, '.inbox'))
            self.assertEqual(expect_archive, self.get_folder_content(db, '.archive'))
            self.assertEqual(expect_spam, self.get_folder_content(db, '.spam'))


    def test_max_age(self):
        from afew import MailMover

        with Database() as db:
            expect_inbox = set([
                create_mail('In inbox, tagged archive, old\n', self.inbox, db, ['archive'], old=True),
            ])

            expect_archive = set([
                create_mail('In inbox, tagged archive\n', self.inbox, db, ['archive']),
            ])

            expect_spam = set([])

        mover = MailMover.MailMover(max_age=15, quiet=True)
        mover.move('.inbox', self.rules['.inbox'])
        mover.move('.archive', self.rules['.archive'])
        mover.move('.spam', self.rules['.spam'])
        mover.close()

        with Database() as db:
            self.assertEqual(expect_inbox, self.get_folder_content(db, '.inbox'))
            self.assertEqual(expect_archive, self.get_folder_content(db, '.archive'))
            self.assertEqual(expect_spam, self.get_folder_content(db, '.spam'))
