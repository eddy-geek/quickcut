# QuickCut
Video &amp; subtitle cut

## Features

* Split video and subtitle based on input time range.
* Supports ffmpeg and libav (avconv) backends for video
  * all common containers (avi, mp4, mkv, ...) and codecs
  * keeping the same codec
* Support pysrt for srt subtitles
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

* Global

      sudo pip3 install quickcut  # Hopefully soon

* Local -
  *Note*: currently provided desktop file won't work as it assumes binary in /usr/local/bin. Same for window icon.

      pip3 install --user quickcut
