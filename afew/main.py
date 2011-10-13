# coding=utf-8

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

import sys
import random

from .Database import Database
from .DBACL import DBACL as Classifier
from .Settings import notmuch_config
from .utils import extract_mail_body

def main(options, query_string):
    maildir_path = notmuch_config.get('database', 'path')
    database = Database(maildir_path)

    if options.tag:
        for filter_class in options.enable_filters:
            filter_ = filter_class(maildir_path)
            filter_.run(query_string)
            filter_.commit(options.dry_run)
    elif options.learn != False:
        classifier = Classifier()
        classifier.learn(
            options.learn,
            database.mail_bodies_matching(query_string)
        )
    elif options.update or options.update_reference:
        classifier = Classifier()
        if options.update:
            for category in (category
                             for category in classifier.categories
                             if category != classifier.reference_category):
                classifier.learn(
                    category,
                    database.mail_bodies_matching('tag:%s' % category)
                )

        if options.update_reference:
            all_messages = list(database.mail_bodies_matching(query_string))
            random.shuffle(all_messages)
            classifier.learn(
                classifier.reference_category,
                all_messages[:options.reference_set_size]
            )
    elif options.classify:
        classifier = Classifier()
        for message in database.get_messages(query_string):
            scores = classifier.classify(extract_mail_body(message))

            category = scores[0][0]

            if category == classifier.reference_category:
                category = 'no match'

            print('%s --> %s' % (unicode(message), category))
    else:
        sys.exit('Weird... please file a bug containing your command line.')
