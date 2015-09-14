## Frontend

* play support
   - phase 1: play button next to both in and out
   - phase 2: embed the vlc player by using the widget's winId as per these pages:
      * pyqt part:  http://python.6.x6.nabble.com/Embedding-VLC-td1923916.html
      * pyvlc part: https://gist.github.com/smathot/1521059

## Backend

* use VLC as alternative split backend:  
       `vlc -Idummy $in_filename --start-time $start --stop-time $stop --sout=#file{dst=$out_filename} vlc://quit`

* 'alternate audio' option -> use `'-map 0:v -map 0:a:1'`  or `'-map 0 -map -0:a:0'`

* use `ffprobe -print_format json -show_format -show_streams $file` to display information  
       print empty `{}` json in case of error

* set tab order right by reordering constructor or using http://doc.qt.io/qt-5.5/qwidget.html#setTabOrder

## Architecture

* use qml for UI as per
   - http://pyqt.sourceforge.net/Docs/PyQt5/qml.html  
   - http://doc.qt.io/qt-5/qml-qtquick-dialogs-filedialog.html
   - http://doc.qt.io/qt-5/qml-qtquick-controls-textfield.html#validator-prop
   - https://www.ics.com/files/qtdocs/qml-extending-types.html

