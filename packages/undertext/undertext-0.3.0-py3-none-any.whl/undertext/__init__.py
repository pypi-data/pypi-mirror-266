#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""
MIT License

Copyright (c) 2024 utility-libraries

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__author__ = "PlayerG9"
__copyright__ = "Copyright 2024, utility-libraries"
__credits__ = ["PlayerG9"]
__license__ = "MIT"
__maintainer__ = "PlayerG9"
__email__ = None
__status__ = "Prototype"  # Prototype, Development, Production
__description__ = "library to load, edit and save different formats of subtitles"
__version_info__ = (0, 3, 0)
__version__ = '.'.join(str(_) for _ in __version_info__)

from .exceptions import *
from .structures import *
from . import readers, writers
from .readers import loads
from .writers import dumps
from .extra import clean_captions
