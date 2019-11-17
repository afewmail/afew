# SPDX-License-Identifier: ISC
# Copyright (c) Justus Winter <4winter@informatik.uni-hamburg.de>

import os
import glob

__all__ = list(filename[:-3]
               for filename in glob.glob1(os.path.dirname(__file__), '*.py')
               if filename != '__init__.py')
