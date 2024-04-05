#!/usr/bin/env/python

#
# Copyright 2024 Chris Josephes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

'''
String functions.
'''

import re
import string

UNICODE_SQ = "\u2018\u2019\u201c\u201d"


def transform_string(in_value):
    '''Low level change to remove all punctuation from a string.'''
    if in_value is not None:
        no_punctuation = drop_punct(in_value)
        return no_punctuation.casefold()
    return "SHOULDNT BE HERE"


def build_filename_string(in_value):
    '''Convert all whitespace into underscores suitable for a filename'''
    level1 = transform_string(in_value)
    level2 = level1.translate(level1.maketrans(" \t\n\r", "____"))
    return level2.replace("__", "_")


def build_complete_filename(in_album, in_suffix='audiocd'):
    '''
    Build the proper filename for an output file.
    '''
    art = build_filename_string(in_album.artist.name)
    alb = build_filename_string(in_album.title)
    year = in_album.first_track().year
    name = f"{art}_{alb}-{year}-{in_suffix}.xml"
    return name


def sanitize_year(in_year):
    '''
    Ensure a year value either matches the correct pattern,
    or a year value can be extracted.
    '''
    year_p = re.compile(r'\d\d\d\d')
    mtch = year_p.match(in_year)
    return mtch.group(0) or "UNKN"


def sanitize_for_xml(in_string):
    '''
    Fix a string so it is suitable to go into
    XML output.
    '''
    out = in_string.replace('&', '&amp;') \
        .replace('<', '&lt;').replace('>', '&gt;')
    return out


def transform_ampersand(in_value):
    '''
    Simple function to transform an ampersand.
    '''
    return in_value.replace("&", "&amp;")


def drop_punct(in_str):
    '''
    Remove all punctuation symbols from a string.

    Also make a pass at removing unicode smart quotes
    '''
    level1 = in_str.translate(in_str.maketrans("", "", string.punctuation))
    out_str = level1.translate(level1.maketrans("", "", UNICODE_SQ))
    return out_str
