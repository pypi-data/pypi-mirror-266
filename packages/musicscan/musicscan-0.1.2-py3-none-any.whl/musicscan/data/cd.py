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
Data objects for music.
'''

# pylint: disable=too-many-instance-attributes

from musicscan.data.flags import Flags
from musicscan.data.titletools import ShortTitleIndex, ShortTitle
from musicscan.data.track import Track
from musicscan.data.stringtools import build_complete_filename


class Album():
    '''
    Object class album representing an actual purchased
    CD, which could include one or more discs, with each
    disc containing one or more tracks.
    '''
    def __init__(self, in_artist, in_album_title):
        self.title = in_album_title
        self.artist = in_artist
        self.title_index = ShortTitleIndex()
        self.discs = {}
        self.flags = Flags()
        self.track_count = 0

    def import_tag(self, in_tag):
        '''
        Import an ID3 tag into the album, creating
        a Disc object if necessary.
        '''
        if not in_tag.disc:
            disc_no = 1
        else:
            disc_no = int(in_tag.disc)
        if disc_no not in self.discs:
            self.discs[disc_no] = Disc(disc_no, self)
            self.discs[disc_no].import_tag(in_tag, self)
        else:
            self.discs[disc_no].import_tag(in_tag, self)
        self.track_count += 1

    def report(self):
        '''
        Generate a simple report on the ablum.
        '''
        print(f"Album: {self.title}")
        print(f"Artist: {self.artist}")
        for dsc in sorted(self.discs):
            self.discs[dsc].report()

    def summary(self):
        '''
        Generate a summary of what the album contains.
        '''
        output = ''
        first = self.first_track()
        output += f"Album: {self.title} ({first.year})\n"
        output += f"Artist: {self.artist!s}\n"
        output += f"Discs: {len(self.discs)}  Tracks: {self.track_count}\n"
        return output

    def filename(self, in_suffix='album'):
        '''
        Create a filename based on the interpreted ID3 album name.
        '''
        return build_complete_filename(self, in_suffix)

    def first_track(self):
        '''
        Return the very first track of the album.
        '''
        return self.discs[1].tracks[0]

    def tracks_in_order(self):
        '''
        Return all tracks from all discs on the album.
        '''
        all_tracks = []
        for dsc in sorted(self.discs):
            for trk in sorted(self.discs[dsc].tracks,
                              key=lambda x: x.track_no):
                all_tracks.append(trk)
        return all_tracks

    def finalize(self):
        '''
        Finalize each object by setting up the short titles
        for each track.
        '''
        for dsc in sorted(self.discs):
            self.discs[dsc].finalize()

    def __str__(self):
        return f"{self.title} ({len(self.discs)})"


class Disc():
    '''
    Class representing a single physical compact disc.
    '''
    def __init__(self, in_number, in_album):
        self.disc_no = in_number
        self.album = in_album
        self.tracks = []
        self.raw = []

    def import_tag(self, in_tag, in_album):
        '''
        Import data from an ID3 tag into the disc object.
        '''
        self.raw.append(in_tag)
        trk = Track(in_tag)
        trk.set_album_object(in_album)
        self.tracks.append(trk)

    def finalize(self):
        '''
        Update data after all import operations are done.
        '''
        for trk in sorted(self.tracks):
            trk.short_title = ShortTitle(trk.title, self.album.title_index)

    def report(self):
        '''
        Generate a simple report on the disc object.
        '''
        print(f"Disc: {self.disc_no}")
        for trk in sorted(self.tracks, key=lambda x: x.track_no):
            print(f"{trk}")

    def __lt__(self, other):
        return self.disc_no < other.disc_no

    def __gt__(self, other):
        return self.disc_no > other.disc_no
