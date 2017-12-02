# -*- coding: utf-8 -*-
# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

from __future__ import print_function, absolute_import, unicode_literals

import sys
import os
import glob

__all__ = list(filename[:-3]
               for filename in glob.glob1(os.path.dirname(__file__),
                                          # py2.7 compat hack
                                          b'*.py' if sys.version_info[0] == 2 else '*.py')
               if filename is not '__init__.py')
