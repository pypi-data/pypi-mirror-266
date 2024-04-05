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
Testing code to identify possible edit flags.
'''

import re
from musicscan.data.flags import FlagCodes


class Analyzer():
    '''
    Perform tests against the data and
    add flags when appropriate.
    '''

    def main_test(self, in_album):
        '''
        Main album testing routine.
        '''
        self.test_album_title(in_album)
        self.test_album_artist(in_album)
        self.test_soundtrack(in_album)
        self.test_score(in_album)
        for dsc in sorted(in_album.discs):
            for trk in sorted(in_album.discs[dsc].tracks,
                              key=lambda x: x.track_no):
                self.test_album_track_chrs(trk)
                self.test_album_track_featured(trk)
                self.test_album_track_live(trk)
                self.test_album_track_blank(trk)

    def test_album_title(self, in_album):
        '''
        Test album title for keywords that may indicate
        a compilation of some kind.
        '''
        greatest_p = re.compile(r'Greatest', re.IGNORECASE)
        hits_p = re.compile(r'\s+Hit', re.IGNORECASE)
        if greatest_p.search(in_album.title):
            in_album.flags.add_flag(FlagCodes.p_greatest)
        if hits_p.search(in_album.title):
            in_album.flags.add_flag(FlagCodes.p_hits_compo)

    def test_soundtrack(self, in_album):
        '''
        Test album title for keywords that may indicate
        a soundtrack album.
        '''
        first_track = in_album.first_track()
        soundtrack_p = re.compile(r'\s+Soundtrack\s+', re.IGNORECASE)
        if soundtrack_p.search(in_album.title):
            in_album.flags.add_flag(FlagCodes.p_soundtrack)
        if first_track.genre == 'Soundtrack':
            if FlagCodes.p_soundtrack not in in_album.flags.flags:
                in_album.flags.add_flag(FlagCodes.p_soundtrack)

    def test_score(self, in_album):
        '''
        Test album title for keywords that may indicate
        a score album.
        '''
        score_p = re.compile(r'\s+Score\s+', re.IGNORECASE)
        if score_p.search(in_album.title):
            in_album.flags.add(FlagCodes.p_score)

    def test_album_artist(self, in_album):
        '''
        Test the name of the artist for indicators
        the band may be a group.
        '''
        and_p = re.compile(r'\s+and\s+', re.IGNORECASE)
        if and_p.search(str(in_album.artist)):
            in_album.flags.add_flag(FlagCodes.l_group)

    def test_album_track_chrs(self, in_track):
        '''
        Test the track title to indicate metadata may
        have been embeded in the track name in parenthesis.
        '''
        if '[' in in_track.title or ']' in in_track.title:
            in_track.flags.add_flag(FlagCodes.d_sq_brackets)
        if '(' in in_track.title or ')' in in_track.title:
            in_track.flags.add_flag(FlagCodes.d_parenthesis)

    def test_album_track_featured(self, in_track):
        '''
        Test the track title or track artist to see if
        there may be additional artists for this particular track.
        '''
        feature_p = re.compile(r'Feat', re.IGNORECASE)
        with_p = re.compile(r'With\s+', re.IGNORECASE)
        if feature_p.search(in_track.title) or with_p.search(in_track.title):
            in_track.flags.add_flag(FlagCodes.p_feat_artist)
        if feature_p.search(in_track.artist) or with_p.search(in_track.artist):
            in_track.flags.add_flag(FlagCodes.p_feat_artist)

    def test_album_track_live(self, in_track):
        '''
        Test the track title to see if it might
        indicate a live recording.
        '''
        live_p = re.compile(r'Live\s+', re.IGNORECASE)
        if live_p.search(in_track.title):
            in_track.flags.add_flag(FlagCodes.p_live)

    def test_track_genre(self, in_track):
        '''
        Test the track for bad genre values.
        '''
        country_p = re.compile(r'Country & Folk', re.IGNORECASE)
        if country_p.search(in_track.genre):
            in_track.flags.add_flag(FlagCodes.p_genre_country_folk)

    def test_album_track_demo(self, in_track):
        '''
        Test the track title to see if it might
        be a demo recording.
        '''
        demo_p = re.compile(r'Demo', re.IGNORECASE)
        if demo_p.search(in_track.title):
            in_track.flags.add_flag(FlagCodes.p_demo)

    def test_album_track_blank(self, in_track):
        '''
        Test the track title to see if it might
        be a blank track to pad the CD content.
        '''
        blank_p = re.compile(r'Blank', re.IGNORECASE)
        if blank_p.search(in_track.title):
            in_track.flags.add_flag(FlagCodes.p_blank_track)
