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
Flags represent additional data added to XML output for the purpose
of identifying likely data that will probably need closer scrutiny.

Each album and song has a flag object, which will contain zero or
more flags that will be output as an XML comment with the XML elements.
'''

# pylint: disable=R0903


class Flags():
    '''
    Flags are warnings that are output in the XML
    so users can identify possible issues with
    the interpreted data.
    '''
    def __init__(self):
        self.flags = []

    def add_flag(self, in_code):
        '''
        Add a FlagCode to the array.
        '''
        self.flags.append(in_code)

    def to_xml_comment(self):
        '''
        Convert each flag code to an XML comment string value.
        '''
        if len(self.flags) > 0:
            flag_string = ''
            for f_code in self.flags:
                flag_string += FlagCodes.to_str(f_code) + ' '
            return f"<!-- EDIT FLAGS: {flag_string} -->\n"
        return ''


class FlagCodes():
    '''
    All possible flag values
    '''
    p_greatest = 1
    p_hits_compo = 2
    p_soundtrack = 3
    p_score = 4
    d_sq_brackets = 10
    d_parenthesis = 11
    l_group = 20
    p_feat_artist = 30
    p_live = 31
    p_demo = 32
    p_blank_track = 40
    p_genre_country_folk = 50
    m_year = 60

    @classmethod
    def to_str(cls, in_code):
        '''
        Convert a flag value to a usable string.
        '''
        matrix = {FlagCodes.p_greatest: 'possible_greatest_hits',
                  FlagCodes.p_hits_compo: 'possible_hits_compilation',
                  FlagCodes.p_soundtrack: 'possible_soundtrack',
                  FlagCodes.p_score: 'possible_score',
                  FlagCodes.d_sq_brackets: 'detected_square_brackets',
                  FlagCodes.d_parenthesis: 'detected_parenthesis',
                  FlagCodes.l_group: 'likely_group_artist',
                  FlagCodes.p_feat_artist: 'possible_featured_artist',
                  FlagCodes.p_live: 'possible_live_performance',
                  FlagCodes.p_demo: 'possible_demo_performance',
                  FlagCodes.p_blank_track: 'possible_blank_track',
                  FlagCodes.p_genre_country_folk:
                  'country_and_folk_genre_is_too_vague',
                  FlagCodes.m_year: 'missing_copyright_year'}
        if in_code in matrix:
            return matrix[in_code]
        return ''
