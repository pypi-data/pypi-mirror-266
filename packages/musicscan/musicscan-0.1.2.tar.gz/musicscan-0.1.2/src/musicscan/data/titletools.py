#!/usr/bin/env python

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
Objects to generate unique identification values for
track titles.
'''

# pylint: disable=too-few-public-methods

from musicscan.data.stringtools import drop_punct


class ShortTitleIndex():
    '''
    An album level index to track the title
    of every track for the purpose of
    maintaining a unique XML id value for the index.
    '''
    def __init__(self):
        self.t_list = {}

    def add(self, new_object):
        '''
        Try and add the short title to the index.
        If the new value conflicts, force the
        passed object to increment its index value.
        '''
        short_title_s = str(new_object)
        while short_title_s in self.t_list:
            new_object.increment()
            short_title_s = str(new_object)
        self.t_list[short_title_s] = new_object


class ShortTitle():
    '''
    A short string based on the first letter
    of the first three words of the title of the
    track, and a numerical index.  The value is
    used as a unique indentity value for
    mapping between the song and
    the physical media index.

    Ex: The song "Rock Me Amadeus" would
    have an index value of "rma01".

    The song "99 Luftballons" would
    have an index value of "n9l01"
    because the index value cannot start
    with a number.

    The song "2112" would have an identity
    string value of "n2-01" because the
    code adds a dash between title portion
    and the incrementor.

    The song "A Little Respect" would
    have an index value of "lr01" because
    the code skips the first word if it's
    an article, like 'A', 'An', or 'The'.

    If the there are two songs that have
    similar titles the incrementor value is
    automatically increased to guarauntee
    a unique value.
    '''
    def __init__(self, in_title, in_index):
        self.text = ''
        self.index = 1
        self._process(in_title, in_index)

    def _process(self, in_title, in_index):
        '''
        Check the index to ensure it has
        a unique value against other tracks.
        '''
        self.text = self._build_str(in_title)
        in_index.add(self)

    def _build_str(self, in_title):
        '''
        Ensure a short string is properly
        created based on the title of the
        track.
        '''
        lc_t = in_title.upper()
        words = lc_t.split()
        final_word = ''
        if words[0] in ['A', 'An', 'The']:
            if len(words) > 1:
                words.pop(0)
        for e_wrd in words[0:3]:
            no_punc = drop_punct(e_wrd)
            if len(no_punc) > 0:
                final_word += no_punc[0].lower()
        if final_word[0].isdigit():
            final_word = 'n' + final_word[:-1]
        return final_word

    def increment(self):
        '''
        Increment the index value.
        '''
        self.index += 1

    def __str__(self):
        if self.text[-1].isdigit():
            return f"{self.text}-{self.index:02d}"
        return f"{self.text}{self.index:02d}"
