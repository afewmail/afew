from unittest import mock, TestCase
import tempfile
import os
import queue

from watchdog.events import FileSystemMovedEvent, FileDeletedEvent
from notmuch.errors import FileError, FileNotEmailError

from afew import files
from afew.Database import Database


class TestFileWatcher(TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

        os.environ["MAILDIR"] = self.test_dir
        files.LOOP_FOREVER = False
        self.obs_mock = mock.patch("afew.files.Observer")
        self.obs = self.obs_mock.start()

        self.notmuch_mock = mock.patch("afew.Database.Database")
        self.notmuch = self.notmuch_mock.start()

        self.event_handler = files.EventHandler(None, self.notmuch)

    def tearDown(self):
        self.obs_mock.stop()
        self.notmuch_mock.stop()

    def test_watch_for_new_files(self):
        files.watch_for_new_files(None, Database(), paths=(
            os.path.join(self.test_dir, "inbox"),))

        self.obs.assert_called_once()
        self.assertEqual(self.obs.return_value.schedule.call_count, 1)
        self.assertEqual(self.obs.return_value.start.call_count, 1)

    def test_event_handler_on_delete(self):
        event = FileDeletedEvent("/tmp/path.txt")
        self.event_handler.on_deleted(event)

        self.notmuch.remove_message.assert_called_once_with(event.src_path)
        self.notmuch.close.assert_called_once()

    def test_event_handler_on_delete_with_invalid_path(self):
        event = FileDeletedEvent("xapian/test.lock")
        self.event_handler.on_deleted(event)

        self.notmuch.remove_message.assert_not_called()
        self.notmuch.close.assert_not_called()

    def test_event_handler_on_moved(self):
        event = FileSystemMovedEvent("test.txt", "test2.txt")
        self.event_handler.on_deleted(event)

        self.notmuch.add_message.called_once_with("test2.txt",
                                                  sync_maildir_flags=True,
                                                  new_mail_handler=self.event_handler._new_mail_handler)
        self.notmuch.close.assert_called_once()

    def test_event_handler_on_moved_handles_file_error(self):
        event = FileSystemMovedEvent("test.txt", "test2.txt")
        self.notmuch.add_message.side_effect = FileError()
        self.event_handler.on_moved(event)

        self.notmuch.add_message.called_once_with("test2.txt",
                                                  sync_maildir_flags=True,
                                                  new_mail_handler=self.event_handler._new_mail_handler)
        self.notmuch.close.assert_called_once()

    def test_event_handler_on_moved_handles_file_not_email_error(self):
        event = FileSystemMovedEvent("test.txt", "test2.txt")
        self.notmuch.add_message.side_effect = FileNotEmailError()
        self.event_handler.on_moved(event)
        self.notmuch.add_message.called_once_with("test2.txt",
                                                  sync_maildir_flags=True,
                                                  new_mail_handler=self.event_handler._new_mail_handler)
        self.notmuch.close.assert_called_once()

    def test_event_handler_on_moved_handles_unknown_error(self):
        event = FileSystemMovedEvent("test.txt", "test2.txt")

        self.event_handler.on_moved(event)
        self.notmuch.add_message.called_once_with("test2.txt",
                                                  sync_maildir_flags=True,
                                                  new_mail_handler=self.event_handler._new_mail_handler)
        self.notmuch.remove_message.called_once_with("test2.txt")
        self.notmuch.close.assert_called_once()

    def test_walker(self):
        file_mock = mock.MagicMock()
        file_mock.__enter__.return_value = ('one_file',)

        with mock.patch('os.scandir', file_mock) as f:
            results = queue.Queue()
            files.walker(results, "/tmp/")

            self.assertEqual(results.qsize(), 2)
            self.assertEqual(f.call_count, 1)
