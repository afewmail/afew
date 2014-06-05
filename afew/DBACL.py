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
import glob
import logging
import functools
import subprocess

class ClassificationError(Exception): pass
class BackendError(ClassificationError): pass

default_db_path = os.path.join(os.environ.get('XDG_DATA_HOME',
                                              os.path.expanduser('~/.local/share')),
                               'afew', 'categories')

class Classifier(object):
    reference_category = 'reference_category'

    def __init__(self, categories, database_directory = default_db_path):
        self.categories = set(categories)
        self.database_directory = database_directory

    def learn(self, category, texts):
        pass

    def classify(self, text):
        pass

class DBACL(Classifier):
    def __init__(self, database_directory = default_db_path):
        categories = glob.glob1(database_directory, '*')
        super(DBACL, self).__init__(categories, database_directory)

    sane_environ = {
        key: value
        for key, value in os.environ.items()
        if not (
            key.startswith('LC_') or
            key == 'LANG' or
            key == 'LANGUAGE'
        )
    }

    def _call_dbacl(self, args, **kwargs):
        command_line = ['dbacl', '-T', 'email'] + args
        logging.debug('executing %r' % command_line)
        return subprocess.Popen(
            command_line,
            shell = False,
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            env = self.sane_environ,
            **kwargs
        )

    def get_category_path(self, category):
        return os.path.join(self.database_directory, category.replace('/', '_'))

    def learn(self, category, texts):
        process = self._call_dbacl(['-l', self.get_category_path(category)])

        for text in texts:
            process.stdin.write((text + '\n').encode('utf-8'))

        process.stdin.close()
        process.wait()

        if process.returncode != 0:
            raise BackendError('dbacl learning failed:\n%s' % process.stderr.read())

    def classify(self, text):
        if not self.categories:
            raise ClassificationError('No categories defined')

        categories = functools.reduce(list.__add__, [
            ['-c', self.get_category_path(category)]
            for category in self.categories
        ], [])

        process = self._call_dbacl(categories + ['-n'])
        stdout, stderr = process.communicate(text.encode('utf-8'))

        if len(stderr) == 0:
            result = stdout.split()
            scores = list()
            while result:
                category = result.pop(0).decode('utf-8', 'replace')
                score = float(result.pop(0))
                scores.append((category, score))
            scores.sort(key = lambda category_score: category_score[1])
        else:
            raise BackendError('dbacl classification failed:\n%s' % stderr)

        return scores
