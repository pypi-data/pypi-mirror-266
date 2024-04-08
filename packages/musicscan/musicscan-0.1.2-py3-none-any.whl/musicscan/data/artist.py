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
Data objects representing musical artists.
'''

# pylint: disable=too-few-public-methods

from musicscan.data.stringtools import sanitize_for_xml


class AbstractAlbumArtist():
    '''
    Abtract class to represent an album artist.
    '''
    def __init__(self):
        self.name = None

    def __str__(self):
        return str(self.name)


class AlbumArtist(AbstractAlbumArtist):
    '''
    Class to represent a single album artist (either band or individual)
    '''
    def __init__(self, in_name):
        super().__init__()
        self.name = in_name

    def to_xml(self):
        '''
        Return the value as an XML chunk.
        '''
        return f"<artist><unkn>{sanitize_for_xml(self.name)}</unkn></artist>"


class AlbumVariousArtists(AbstractAlbumArtist):
    '''
    Class to present a designation of "various artists" on an album.
    '''
    def __init__(self):
        super().__init__()
        self.name = 'Various Artists'

    def to_xml(self):
        '''
        Return the value as an XML chunk.
        '''
        return "<variousArtists/>"
