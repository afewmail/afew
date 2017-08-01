import unittest

from afew.Settings import *
from afew.NotmuchSettings import *

class TestMultiLineConfig(unittest.TestCase):
  def setUp (self):
    global settings
    global notmuch_settings
    self.test_config = """
[FolderNameFilter]
maildir_separator = /
folder_blacklist  = archive k b
folder_transforms = a:b
                    INBOX:inbox
                    "Deleted Messages":deleted
    """

    self.test_nm_config = """
[database]
path = /Mail

    """

    settings.clear ()
    notmuch_settings.clear ()

    settings.read_string (self.test_config)
    notmuch_settings.read_string (self.test_nm_config)


  def tearDown (self):
    pass


  def test_multi_line_config (self):
    from afew.filters.FolderNameFilter import FolderNameFilter

    f = FolderNameFilter (None,
        settings.get('FolderNameFilter', 'folder_blacklist'),
        settings.get('FolderNameFilter', 'folder_transforms'),
        settings.get('FolderNameFilter', 'maildir_separator'),)
    tr = f._FolderNameFilter__folder_transforms

    self.assertEqual(tr['INBOX'], 'inbox')
    self.assertEqual(tr['Deleted Messages'], 'deleted')


