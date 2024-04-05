# musicscan - Music File Scanner

The `musicscan` package is a software library for extracting metadata from a digital
music collection and builds a set of XML files adhering to the vtmedia schema.

It includes a tool that will recursively scan a directory for audio files
containing ID3 tags and uses that data as the basis for bulding XML files.

## Scanning

If you have a directory like this.

```
$ ls -1 "Music/Garth Brooks/No Fences/"
01 The Thunder Rolls.m4a
02 New Way To Fly.m4a
03 Two Of A Kind, Workin' On A Full House.m4a
04 Victim Of The Game.m4a
05 Friends In Low Places.m4a
06 Wild Horses.m4a
07 Unanswered Prayers.m4a
08 Same Old Story.m4a
09 Mr. Blue.m4a
10 Wolves.m4a
```

The `id3scan` tool will search that directory and create 3 files.

```
garth_brooks_no_fences-1990-album.xml
garth_brooks_no_fences-1990-audiocd.xml
garth_brooks_no_fences-1990-cd01-index.xml
```

Each file contains different aspects of the album.

| File | Data |
|======|======|
| garth_brooks_no_fences-1990-audiocd.xml | Information on the physical media |
| garth_brooks_no_fences-1990-album.xml | Information about each song |
| garth_brooks_no_fences-1990-cd01-index.xml | Track order information for each song |

The XML files are nested, so the `audiocd.xml` file has an XInclude reference to the index
and the album XML files.  It is also possible for the tool to put all of the information
in a single file for convenience.

## How It Works

It works under the assumption that the digital library was created by importing CDs
into a music ecosystem like iTunes or Windows Media Player; so it uses 
the nomenclature of physical CDs.  That is, every audio file scanned represents
a single track that was imported from a physical Compact Disc, and it will
use the metadata to build the XML files.  If the metadata does not include 
information like track number, or disc number; the import will probably not work.

The benefits of extracting the metadata are:

1. Maintaining a separate copy of the metadata away from the music library.
2. Extending the metadata with extra fields that may not be supported with ID3 tags.
3. Searching the metadata with tools that may not be available to your music player.
4. Sharing the metadata with other users.

## XML Schema

The XML generated from the tool adheres to the VTMedia schema, which can be found here.

| Repository | Purpose |
| --- | --- |
| [vtmedia-schema](https://github.com/cjcodeproj/vtmedia-schema) | Schema and XML validation for media data |

The schema can be loaded into command line tools, IDEs, or custom code applications to examine
the validity of the metadata files.  It also contains example music data that has been generated
using the `id3tool` code, and then edited for accuracy.

## Documentation

There is RST documentation for the `id3scan` tool in the `doc/` directory.

## Building And Installing From Source Code

Assuming a normal Python 3 environment with setuptools and build modules
installed, run the build module in the top level directory of the repository.

```
$ cd musicscan
$ python -m build 
```

This code has a dependency on the [TinyTag](https://pypi.org/project/tinytag/)
module, which should automatically be installed during the build process.
