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

# pylint: disable=too-few-public-methods

import musicscan.data.artist
import musicscan.data.analyzer
from musicscan.data.cd import Album


class Library():
    '''
    A completed library of albums that can be iterated against.
    '''
    def __init__(self):
        self.albums = []

    def add_album(self, in_album):
        '''
        Add an album object to the library.
        '''
        self.albums.append(in_album)


class Organizer():
    '''
    A class for taking parsed id3 tags and assigning them to class
    objects for the purpose of building a library.

    Dictionary artists uses artist name string as key.
    Value is a nested dictionary based on the album name.
    That dictionary value is an array holding all the TinyTag
    objects.

    Yes, it's ugly.
    '''
    def __init__(self, in_library):
        self.track_count = 0
        self.library = in_library
        self.albums = []
        self.artists = {}

    def examine_track(self, in_tag):
        '''
        Examine a TinyTag and identify both album and artist.

        Build a data structure to accomodate the tag objects.
        '''
        artist = in_tag.albumartist or in_tag.artist
        album = in_tag.album
        if artist not in self.artists:
            self.artists[artist] = {}
            self.artists[artist][album] = [in_tag]
            self.track_count += 1
        else:
            if album not in self.artists[artist]:
                self.artists[artist][album] = [in_tag]
                self.track_count += 1
            else:
                self.artists[artist][album].append(in_tag)
                self.track_count += 1

    def build_albums(self):
        '''
        Build Album and Artist objects based on the collected
        tag data.
        '''
        for art in self.artists:
            if art == 'Various Artists':
                art_o = musicscan.data.artist.AlbumVariousArtists()
            else:
                art_o = musicscan.data.artist.AlbumArtist(art)
            for album in self.artists[art]:
                album_o = Album(art_o, album)
                for tag in self.artists[art][album]:
                    album_o.import_tag(tag)
                self.albums.append(album_o)
        for album_o in self.albums:
            album_o.finalize()

    def analyze(self):
        '''
        Perform additional tests on the data
        to flag possible inconsistencies or
        inaccuracies that can be fixed.
        '''
        analyzer = musicscan.data.analyzer.Analyzer()
        for alb in self.albums:
            analyzer.main_test(alb)

    def push_stats(self, in_stats):
        '''
        Take a Stats() object and pass data to it.
        '''
        in_stats.album_count = len(self.albums)
        in_stats.track_count = 0
        for alb in self.albums:
            for dsc in sorted(alb.discs):
                in_stats.track_count += len(alb.discs[dsc].tracks)
