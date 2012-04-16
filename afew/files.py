# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals

#
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

import os
import re
import stat
import logging
import platform
import threading

if platform.system() != 'Linux':
    raise ImportError('Unsupported platform: {!r}'.format(platform.system()))

try:
    # py3k
    import queue
except ImportError:
    import Queue as queue

import notmuch
import pyinotify

class EventHandler(pyinotify.ProcessEvent):
    def __init__(self, options, database):
        self.options = options
        self.database = database
        super(EventHandler, self).__init__()

    ignore_re = re.compile('(/xapian/.*(base.|tmp)$)|(\.lock$)|(/dovecot)')

    def process_IN_DELETE(self, event):
        if self.ignore_re.search(event.pathname):
            return

        logging.debug("Detected file removal: {!r}".format(event.pathname))
        self.database.remove_message(event.pathname)
        self.database.close()

    def process_IN_MOVED_TO(self, event):
        if self.ignore_re.search(event.pathname):
            return

        src_pathname = event.src_pathname if hasattr(event, 'src_pathname') else None
        logging.debug("Detected file rename: {!r} -> {!r}".format(src_pathname, event.pathname))

        def new_mail(message):
            for filter_ in self.options.enable_filters:
                try:
                    filter_.run('id:"{}"'.format(message.get_message_id()))
                    filter_.commit(self.options.dry_run)
                except Exception as e:
                    logging.warn('Error processing mail with filter {!r}: {}'.format(filter_.message, e))

        try:
            self.database.add_message(event.pathname,
                                      sync_maildir_flags=True,
                                      new_mail_handler=new_mail)
        except notmuch.FileError as e:
            logging.warn('Error opening mail file: {}'.format(e))
            return
        except notmuch.FileNotEmailError as e:
            logging.warn('File does not look like an email: {}'.format(e))
            return
        else:
            if src_pathname:
                self.database.remove_message(src_pathname)
        finally:
            self.database.close()

def watch_for_new_files(options, database, paths, daemonize=False):
    wm = pyinotify.WatchManager()
    mask = (
        pyinotify.IN_DELETE |
        pyinotify.IN_MOVED_FROM |
        pyinotify.IN_MOVED_TO)
    handler = EventHandler(options, database)
    notifier = pyinotify.Notifier(wm, handler)

    logging.debug('Registering inotify watch descriptors')
    wdds = dict()
    for path in paths:
        wdds[path] = wm.add_watch(path, mask)

    # TODO: honor daemonize
    logging.debug('Running mainloop')
    notifier.loop()

import ctypes
import contextlib

try:
    libc = ctypes.CDLL(ctypes.util.find_library("c"))
except ImportError as e:
    raise ImportError('Could not load libc: {}'.format(e))

class Libc(object):
    class c_dir(ctypes.Structure):
        pass
    c_dir_p = ctypes.POINTER(c_dir)

    opendir = libc.opendir
    opendir.argtypes = [ctypes.c_char_p]
    opendir.restype = c_dir_p

    closedir = libc.closedir
    closedir.argtypes = [c_dir_p]
    closedir.restype = ctypes.c_int

    @classmethod
    @contextlib.contextmanager
    def open_directory(cls, path):
        handle = cls.opendir(path)
        yield handle
        cls.closedir(handle)

    class c_dirent(ctypes.Structure):
        '''
        man 3 readdir says::

        On Linux, the dirent structure is defined as follows:

           struct dirent {
               ino_t          d_ino;       /* inode number */
               off_t          d_off;       /* offset to the next dirent */
               unsigned short d_reclen;    /* length of this record */
               unsigned char  d_type;      /* type of file; not supported
                                              by all file system types */
               char           d_name[256]; /* filename */
           };
        '''
        _fields_ = (
            ('d_ino', ctypes.c_long),
            ('d_off', ctypes.c_long),
            ('d_reclen', ctypes.c_ushort),
            ('d_type', ctypes.c_byte),
            ('d_name', ctypes.c_char * 4096),
        )
    c_dirent_p = ctypes.POINTER(c_dirent)

    readdir = libc.readdir
    readdir.argtypes = [c_dir_p]
    readdir.restype = c_dirent_p

    # magic value for directory
    DT_DIR = 4

blacklist = {'.', '..', 'tmp'}

def walk_linux(channel, path):
    channel.put(path)

    with Libc.open_directory(path) as handle:
        while True:
            dirent_p = Libc.readdir(handle)
            if not dirent_p:
                break

            if dirent_p.contents.d_type == Libc.DT_DIR and \
                    dirent_p.contents.d_name not in blacklist:
                walk_linux(channel, os.path.join(path, dirent_p.contents.d_name))

def walk(channel, path):
    channel.put(path)

    for child_path in (os.path.join(path, child)
                       for child in os.listdir(path)
                       if child not in blacklist):
        try:
            stat_result = os.stat(child_path)
        except:
            continue

        if stat_result.st_mode & stat.S_IFDIR:
            walk(channel, child_path)

def walker(channel, path):
    walk_linux(channel, path)
    channel.put(None)

def quick_find_dirs_hack(path):
    results = queue.Queue()

    walker_thread = threading.Thread(target=walker, args=(results, path))
    walker_thread.daemon = True
    walker_thread.start()

    while True:
        result = results.get()

        if result != None:
            yield result
        else:
            break
