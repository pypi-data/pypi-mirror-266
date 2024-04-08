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
id3scam

Scan a directory full of music files for ID3 data,
parse the data, and then generate XML files for
each musical album.

(Assuming each album is a musical CD)

'''

import argparse
import os
import os.path
import sys
from tinytag import TinyTag
from musicscan.fileops.scanner import Walker
from musicscan.fileops.filenames import FilenameMatches
from musicscan.fileops.xmlwriter import XMLFileWriter
from musicscan.generic.stats import Stats
from musicscan.data.library import Library, Organizer


def get_files(in_path, in_stats):
    '''
    Get all the music files from the stated path.
    '''
    file_list = []
    walker = Walker([in_path], debug=True)
    walker.scan()
    walker.pass_stats(in_stats)
    pattern = FilenameMatches.Music_Media
    for file in walker.files:
        if pattern.search(file):
            file_list.append(file)
    return file_list


def scan_files(in_files):
    '''
    Generate a TinyTag object from each file identified.
    '''
    tag_objects = []
    for file in in_files:
        print(f"Source file : {file}")
        tagdata = TinyTag.get(file)
        tag_objects.append(tagdata)
    return tag_objects


def report_xml_files(in_args, in_organizer):
    '''
    Report on the XML files that will be generated
    from the collected data.
    '''
    done = []
    not_done = []
    writer = XMLFileWriter(in_args.outdir)
    writer.set_split_xml(in_args.splitxml)
    for alb_i in in_organizer.albums:
        out_files = writer.identify_files(alb_i)
        for file in out_files:
            if os.path.isfile(file):
                done.append(file)
            else:
                not_done.append(file)
    print("\nExisting XML Files\n------------------\n")
    for alxml in done:
        print(alxml)
    print("\nNon-existing XML files\n--------------\n")
    for alxml in not_done:
        print(alxml)


def write_xml_files(in_organizer, in_args, in_stats):
    '''
    Write out the XML files with the accumulated ID3 data.
    '''
    if not os.path.isdir(in_args.outdir):
        print("\nFAILURE: Cannot write to output path {in_args.outdir}\n")
        sys.exit(1)
    writer = XMLFileWriter(in_args.outdir)
    writer.set_debug(in_args.debug)
    writer.set_overwrite(in_args.overwrite)
    writer.set_split_xml(in_args.splitxml)
    for alb_i in in_organizer.albums:
        writer.write_xml(alb_i)
    in_stats.files_written = writer.files_written


def show_debug_data(in_data):
    '''
    Output a bunch of data for debugging purposes.
    '''
    for tag_entry in in_data:
        print(f"\nTitle: {tag_entry.title} {tag_entry.track}\n")
        entry_d = tag_entry.as_dict()
        for field in entry_d:
            print(f"Field: {field} {entry_d[field]}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scan music files',
                                     epilog='Report music data and output XML')
    parser.add_argument('--musicpath', help='path of music files')
    parser.add_argument('--write', action='store_true',
                        default=False,
                        help='write out XML files')
    parser.add_argument('--split-xml', action='store_true',
                        default=False,
                        dest='splitxml',
                        help='split output XML files')
    parser.add_argument('--outdir', help='XML output directory')
    parser.add_argument('--overwrite', action='store_true',
                        default=False,
                        help='overwrite existing files')
    parser.add_argument('--flags', action='store_true',
                        default=True,
                        help='Add edit flags to output XML')
    parser.add_argument('--debug', action='store_true',
                        default=False,
                        help='write debug info in XML files')

    args = parser.parse_args()
    musicpath = args.musicpath
    if not musicpath:
        if 'MUSICPATH' in os.environ:
            musicpath = os.environ['MUSICPATH']
        else:
            print("\nFAILURE: Can't find a source path for music files.\n")
            parser.print_help()
            sys.exit(2)
    stats = Stats()
    all_files = get_files(musicpath, stats)
    data = scan_files(all_files)
    library = Library()
    organizer = Organizer(library)
    if args.debug:
        show_debug_data(data)
    for entry in data:
        organizer.examine_track(entry)
    print(f"\nData count: {len(data)}")
    print(f"Track count: {organizer.track_count}")
    print(f"Artist count: {len(organizer.artists)}\n")
    organizer.build_albums()
    organizer.analyze()
    organizer.push_stats(stats)
    for alb in organizer.albums:
        alb.report()

    if args.outdir:
        report_xml_files(args, organizer)

    if args.write and args.outdir:
        write_xml_files(organizer, args, stats)
    else:
        print("\nXML output was not specified.")

    stats.close()

    print(stats.report())
