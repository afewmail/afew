# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

import os
import re
import logging
import queue
import threading
import notmuch

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

BLACKLIST = {'.', '..', 'tmp'}


class EventHandler(FileSystemEventHandler):
    ignore_re = re.compile('(/xapian/.*(base.|tmp)$)|(\.lock$)|(/dovecot)')

    def __init__(self, options, database):
        self.options = options
        self.database = database
        super().__init__()

    def on_deleted(self, event):
        if self.ignore_re.search(event.src_path):
            return

        logging.debug(f"Detected file removal: {event.src_path}")
        self.database.remove_message(event.src_path)
        self.database.close()

    def on_moved(self, event):
        if self.ignore_re.search(event.src_path):
            return

        logging.debug(f"Detected file rename: {event.src_path} -> {event.dest_path}")

        def new_mail(message):
            for filter_ in self.options.enable_filters:
                try:
                    filter_.run('id:"{}"'.format(message.get_message_id()))
                    filter_.commit(self.options.dry_run)
                except Exception as e:
                    logging.warn(f'Error processing mail with filter {filter_.message}: {e}')

        try:
            self.database.add_message(event.dest_path,
                                      sync_maildir_flags=True,
                                      new_mail_handler=new_mail)
        except notmuch.FileError as e:
            logging.warn(f'Error opening mail file: {e}')
            return
        except notmuch.FileNotEmailError as e:
            logging.warn(f'File does not look like an email: {e}')
            return
        else:
            if event.src_path:
                self.database.remove_message(event.src_path)
        finally:
            self.database.close()


def watch_for_new_files(options, database, paths, daemonize=False):
    observer = Observer()
    handler = EventHandler(options, database)

    logging.debug('Registering inotify watch descriptors')

    for path in paths:
        observer.schedule(handler, path)

    logging.debug('Running mainloop')
    observer.start()

    try:
        while True:
            pass

    except KeyboardInterrupt:
        logging.info('Exiting file watch.')
        observer.stop()
        observer.join()


def __walk(channel, path):
    channel.put(path)

    with os.scandir(path) as it:
        for entry in it:
            if entry.is_dir() and entry.name not in BLACKLIST:
                __walk(channel, os.path.join(path, entry.name))


def walker(channel, path):
    __walk(channel, path)
    channel.put(None)


def quick_find_dirs_hack(path):
    results = queue.Queue()

    walker_thread = threading.Thread(target=walker, args=(results, path))
    walker_thread.daemon = True
    walker_thread.start()

    while True:
        result = results.get()

        if result is not None:
            yield result
        else:
            break
