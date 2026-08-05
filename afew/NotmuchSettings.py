# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

import os

from afew.configparser import RawConfigParser

notmuch_settings = RawConfigParser()


def _notmuch_config_path(path=None):
    path = os.environ.get("NOTMUCH_CONFIG", path)
    if path is not None:
        return path
    profile = os.environ.get("NOTMUCH_PROFILE", "default")
    xdg_conf = os.path.join(
        os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
        "notmuch",
        profile,
        "config",
    )
    if os.path.exists(xdg_conf):
        return xdg_conf
    if profile == "default":
        return os.path.expanduser("~/.notmuch-config")
    else:
        return os.path.expanduser(f"~/.notmuch-config.{profile}")


def read_notmuch_settings(path=None):
    with open(_notmuch_config_path(path)) as fp:
        notmuch_settings.read_file(fp)


def write_notmuch_settings(path=None):
    with open(_notmuch_config_path(path), 'w+') as fp:
        notmuch_settings.write(fp)


def get_notmuch_new_tags():
    # see issue 158
    return filter(lambda x: x != 'unread', notmuch_settings.get_list('new', 'tags'))


def get_notmuch_new_query():
    return '(%s)' % ' AND '.join('tag:%s' % tag for tag in get_notmuch_new_tags())
