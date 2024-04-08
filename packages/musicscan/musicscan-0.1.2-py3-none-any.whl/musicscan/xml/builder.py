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
XML Output blocks
'''

import datetime
from musicscan.data.stringtools import sanitize_for_xml


XML_DECLARATION = "<?xml version='1.0'?>\n"


class AbstractCompactDiscXML():
    '''
    Common routines written out during the creation of the
    main medium file for the CD.
    '''
    def __init__(self, in_debug=False):
        self.debug = in_debug

    def build_head(self):
        '''
        Build the start of the album XML.
        '''
        timestamp = datetime.datetime.now()
        output = XML_DECLARATION
        output += "<medialist xmlns='http://vectortron.com/xml/media/media'"
        output += " xmlns:xi='http://www.w3.org/2001/XInclude'>\n"
        output += f" <!-- created by id3scan ({timestamp}) -->\n"
        output += " <media>\n"
        return output

    def build_foot(self):
        '''
        XML Footer
        '''
        output = " </media>\n" +\
                 "</medialist>\n"
        return output

    def build_title(self, in_title):
        '''
        XML Title Block
        '''
        output = "  <title>\n"
        output += f"   <main>{in_title}</main>\n"
        output += " </title>\n"
        return output

    def build_medium(self, in_album):
        '''
        The main elements reporting on the physical media.
        '''
        output = "  <medium>\n"
        output += "  <release>\n"
        output += "   <type><audiocd/></type>\n"
        output += "  </release>\n"
        output += "  <productSpecs>\n"
        output += "   <inventory>\n"
        output += "    <case>\n"
        for dsc in sorted(in_album.discs):
            output += f"     <cd id='cd{in_album.discs[dsc].disc_no:02}'/>\n"
        output += "    </case>\n"
        output += "   </inventory>\n"
        output += "  </productSpecs>\n"
        output += " </medium>\n"
        return output


class CompleteCompactDiscXML(AbstractCompactDiscXML):
    '''
    Builds an XML structure in a single file.
    '''
    def build(self, in_album):
        '''
        Return the CD structure as a string.
        '''
        output = self.build_head()
        output += self.build_title(in_album.title)
        output += self.build_medium(in_album)
        index = Index()
        output += index.build_single_chunk_from_album(in_album)
        output += " <contents>\n"
        album = Album()
        output += album.build_album_body(in_album)
        output += " </contents>\n"
        output += self.build_foot()
        return output


class SplitCompactDiscXML(AbstractCompactDiscXML):
    '''
    Build an XML structure in multiple files.
    '''
    def build(self, in_album):
        '''
        Return the CD structure as a string.
        '''
        output = self.build_head()
        output += self.build_title(in_album.title)
        output += self.build_medium(in_album)
        index = Index()
        output += index.build_xi_chunk_from_album(in_album)
        output += " <contents>\n"
        album = Album()
        output += album.build_album_xi(in_album)
        output += " </contents>\n"
        output += self.build_foot()
        return output


class Index():
    '''
    Index element, which contains the track/index numbers for the content.
    '''
    def __init__(self, in_debug=False):
        self.debug = in_debug

    def build_single_chunk_from_album(self, in_album):
        '''
        Build an entire index element block with child elements.
        '''
        output = ''
        output += " <index>\n"
        output += self.build_multiple_chunks_from_album(in_album)
        output += " </index>\n"
        return output

    def build_xi_chunk_from_album(self, in_album):
        '''
        Build an index element block with xi:include elements.
        '''
        output = " <index>\n"
        output += self.build_xi_refs_from_album(in_album)
        output += " </index>\n"
        return output

    def build_multiple_chunks_from_album(self, in_album):
        '''
        String together multiple disc index strings together.
        '''
        chunks = []
        for dsc in sorted(in_album.discs):
            d_str = self.build_index_per_cd(in_album.discs[dsc])
            chunks.append(d_str)
        return "".join(chunks)

    def build_index_per_cd(self, in_cd, in_namespace=False):
        '''
        Build an index structure for a single CD.
        '''
        ns_str = ''
        if in_namespace:
            ns_str = " xmlns='http://vectortron.com/xml/media/media'"
        output = f"  <cdIndex ref='cd{in_cd.disc_no:02}'{ns_str}>\n"
        for trk in sorted(in_cd.tracks):
            output += self.add_track_xml(trk)
        output += "  </cdIndex>\n"
        return output

    def build_xi_refs_from_album(self, in_album):
        '''
        Output all of the xi:include references in the index.
        '''
        chunks = []
        for dsc in sorted(in_album.discs):
            d_str = self.build_xi_per_cd(in_album.discs[dsc])
            chunks.append(d_str)
        return "".join(chunks)

    def build_xi_per_cd(self, in_cd):
        '''
        Return an XI Include reference for every CD
        in the set.
        '''
        alb = in_cd.album
        f_str = f"cd{in_cd.disc_no:02}-index"
        filename = alb.filename(f_str)
        output = f"  <xi:include href='{filename}'/>\n"
        return output

    def add_track_xml(self, in_track):
        '''
        Output the information for a single track/song.
        '''
        output = ''
        output += f"   <track no='{in_track.track_no}'>\n"
        output += "    <index no='01'>\n"
        output += f"     <content ref='{in_track.short_title}'/>"
        if self.debug:
            output += f"   <!-- TITLE {in_track.title} -->"
        output += "\n    </index>\n   </track>\n"
        return output


class Album():
    '''
    XML Element structure representing an Album.
    '''
    def __init__(self, in_debug=False):
        self.debug = in_debug

    def build_standalone_album(self, in_album):
        '''
        Write out an entire album in a separate file.
        '''
        output = XML_DECLARATION
        output += self.build_album_body(in_album)
        return output

    def build_album_body(self, in_album):
        '''
        Write out the main body of the album element.
        '''
        output = "  <album xmlns='http://vectortron.com/xml/media/audio'>\n"
        output += f"   <title>{in_album.title}</title>\n"
        output += in_album.flags.to_xml_comment()
        output += self.build_chunk_catalog(in_album)
        output += self.build_chunk_classification(in_album)
        output += self.build_chunk_elements(in_album)
        output += "  </album>\n"
        return output

    def build_album_xi(self, in_album):
        '''
        Write out an xi:include element referencing the album.
        '''
        output = ''
        f_str = in_album.filename('album')
        output = f"  <xi:include href='{f_str}'/>\n"
        return output

    def build_chunk_catalog(self, in_album):
        '''
        Write out the album catalog element.
        '''
        first_track = in_album.first_track()
        output = " <catalog>\n"
        output += "  <artists>\n"
        output += f"   {in_album.artist.to_xml()}\n"
        output += "  </artists>\n"
        if first_track.year != '0000':
            output += "  <copyright>\n" +\
                      f"   <year>{first_track.year}</year>\n" +\
                      "  </copyright>\n"
        output += " </catalog>\n"
        return output

    def build_chunk_classification(self, in_album):
        '''
        Write out the album classification element.
        '''
        first_track = in_album.first_track()
        output = " <classification>\n"
        output += "  <genres>\n"
        output += f"   <primary>{sanitize_for_xml(first_track.genre)}"
        output += "</primary>\n  </genres>\n"
        output += " </classification>\n"
        return output

    def build_chunk_elements(self, in_album):
        '''
        Output the element element and all
        child content elements.
        '''
        output = " <elements>\n"
        song = SongElementXML(self.debug)
        for dsc in sorted(in_album.discs):
            for trk in in_album.discs[dsc].tracks:
                output += song.build(trk)
        output += " </elements>\n"
        return output


class SongElementXML():
    '''
    XML output covering a single element.

    We assume every piece of element content is a song
    because it's a safe bet, and there's no metadata
    that can tell us otherwise.
    '''
    def __init__(self, in_debug=False):
        self.debug = in_debug

    def build(self, in_track):
        '''
        Output the basic song element.
        '''
        output = f"  <song id='{in_track.short_title}'>\n"
        if self.debug:
            output += f"  <!-- POSITION: Disc {in_track.disc_no} " +\
                      f"Track: {in_track.track_no} -->\n"
        output += "   <title>\n"
        output += f"    <main>{sanitize_for_xml(in_track.title)}</main>\n"
        output += "  </title>\n"
        output += in_track.flags.to_xml_comment()
        output += self.build_catalog(in_track)
        output += self.build_technical(in_track)
        output += " </song>\n"
        return output

    def build_catalog(self, in_track):
        '''
        Output the per track catalog element (if it exists)
        '''
        # output += in_track.to_xml_catalog()
        output = ''
        if in_track.artist != str(in_track.album_o.artist) \
                or in_track.composer:
            output = "  <catalog>\n"
            if in_track.artist != str(in_track.album_o.artist):
                output += "   <artists>\n" +\
                          "    <artist><unkn>" +\
                          f"{sanitize_for_xml(in_track.artist)}" +\
                          "</unkn></artist>\n" +\
                          "   </artists>\n"
            if in_track.composer:
                output += "   <composers>\n" +\
                          "    <composer><unkn>" +\
                          f"{sanitize_for_xml(in_track.composer)}" +\
                          "</unkn></composer>\n" +\
                          "   </composers>\n"
            output += "   </catalog>\n"
        return output

    def build_technical(self, in_track):
        '''
        Output the XML technical element for the song.
        '''
        output = "   <technical>\n"
        output += "    <studioRecording/>\n"
        output += "    <runtime>\n"
        output += f"      <overall>{in_track.duration_s}</overall>\n"
        output += "    </runtime>\n"
        if in_track.bpm > 0:
            output += "    <tempo>\n"
            output += f"     <bpm>{in_track.bpm}</bpm>\n"
            output += "   </tempo>\n"
        output += "  </technical>\n"
        return output
