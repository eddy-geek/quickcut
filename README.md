# QuickCut
Video &amp; subtitle cut

[![(ci)](https://secure.travis-ci.org/eddy-geek/quickcut.png?branch=master)](http://travis-ci.org/eddy-geek/quickcut)

## Features

* Split video and subtitle based on input time range.
* Supports ffmpeg and libav (avconv) backends for video
  * all common containers (avi, mp4, mkv, ...) and codecs
  * keeping the same codec
  * 'alternate audio track' selection for multilingual movies e.g. mkv
* Support pysrt for srt subtitles
  * detect subtitle encoding
* Full input validation
  * Times: HH:MM:SS or HHMMSS or MMSS etc.
* Display backend errors if any.

## Install

### Dependencies

* Fedora -
  *Note*: you need RPMFusion repos for ffmpeg

        sudo dnf install python3-qt5 ffmpeg

* Ubuntu/Debian

        sudo apt-get install python3-pyqt5 ffmpeg

* Windows

    Windows is not supported. I guess it may work, assuming you have ffmpeg.exe in %PATH%.


### QuickCut

* Global (/usr/local)

        sudo pip3 install quickcut

* Local

        pip3 install --user quickcut

* Other: you may have issues with icons if your prefix is not /usr/local (see setup.py). Fixes welcome.
