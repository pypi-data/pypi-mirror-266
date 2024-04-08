# musicscan - Music File Scanner

The `musicscan` package is a software library for extracting metadata from a digital
music collection and builds a set of XML files adhering to the vtmedia schema.

It includes a tool that will recursively scan a directory for audio files
containing ID3 tags and uses that data as the basis for bulding XML files.

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

## Scanning Example

If you have a directory like this.

```
$ ls -1 "~/Music/iTunes/iTunes Media/Music/Garth Brooks/No Fences/"
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

The `id3scan` tool will search that directory and create three files.

```
$ python3 -m musicscan.tools.id3scan --musicpath "~/Music/iTunes/iTunes Media/Music/Garth Brooks/No Fences" --write --outdir ~/tmp --split-xml
```

```
$ ls -1 ~/tmp/
garth_brooks_no_fences-1990-album.xml
garth_brooks_no_fences-1990-audiocd.xml
garth_brooks_no_fences-1990-cd01-index.xml
```

Each file contains different aspects of the album data.

| File | Data |
|------|------|
| garth_brooks_no_fences-1990-audiocd.xml | Information on the physical media |
| garth_brooks_no_fences-1990-album.xml | Information about each song |
| garth_brooks_no_fences-1990-cd01-index.xml | Track order information for each song |

The XML files are nested together with XInclude directives tying them together.  If a user skips the `---split-xml` diretive, only
one output file is generated.

### The Audio CD file

The audio cd file is the main file of the data structure.  Most of the relevant information is on the
physical CD structure.

```
<medialist xmlns='http://vectortron.com/xml/media/media' xmlns:xi='http://www.w3.org/2001/XInclude'>
 <!-- created by id3scan (2024-04-06 15:33:06.931311) -->
 <media>
  <title>
   <main>No Fences</main>
 </title>
 <medium>
 <release>
  <type><audiocd/></type>
 </release>
 <productSpecs>
  <inventory>
   <case>
    <cd id='cd01'/>
   </case>
  </inventory>
 </productSpecs>
</medium>
```

### The Index File

The index file contains information about track order, with references to the songs on the album.

```
<cdIndex ref='cd01' xmlns='http://vectortron.com/xml/media/media'>
 <track no='1'>
  <index no='01'>
   <content ref='ttr01'/>
  </index>
</track>
...
```

### The Album File

The album file contains all of the information about the songs.

```
<album xmlns='http://vectortron.com/xml/media/audio'>
 <title>No Fences</title>
 <catalog>
  <artists>
  <artist><unkn>Garth Brooks</unkn></artist>
  </artists>
 </catalog>
 <classification>
  <genres>
   <primary>Country</primary>
  </genres>
 </classification>
 <elements>
  <song id='w01'>
   <title>
    <main>Wolves</main>
   </title>
   <catalog>
    <composers>
     <composer><unkn>Stephanie Davis</unkn></composer>
    </composers>
    </catalog>
    <technical>
     <studioRecording/>
     <runtime>
      <overall>PT4M8.89S</overall>
     </runtime>
    </technical>
   </song>
...
```

## Documentation

There is RST documentation for the [id3scan.rst](doc/id3scan.rst)  tool in the [doc](doc/) directory.

## Building And Installing From Source Code

Assuming a normal Python 3 environment with setuptools and build modules
installed, run the build module in the top level directory of the repository.

```
$ cd musicscan
$ python -m build 
```

This code has a dependency on the [TinyTag](https://pypi.org/project/tinytag/)
module, which should automatically be installed during the build process.

## Package Distribution

[![PyPi version](https://img.shields.io/pypi/v/musicscan)](https://pypi.org/project/musicscan/)

Installation can be done through the python pip command.

```
$ python -m pip install --user musicscan
```

