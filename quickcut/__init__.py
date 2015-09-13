import os
import subprocess
import sys
import shutil
import pkg_resources
import datetime as dt
from pathlib import Path

import pysrt
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QLabel, QPushButton, QMessageBox

from quickcut.widgets import Picker, MinuteSecondEdit, BiggerMessageBox

"""
Uses ffmpeg - http://manpages.ubuntu.com/manpages/vivid/en/man1/ffmpeg.1.html
"""

__author__ = 'Edward Oubrayrie'

package = Path(__file__).parent.name
__version__ = pkg_resources.get_distribution(package).version
icon_path = pkg_resources.resource_filename('quickcut', 'quickcut.png')
print(icon_path)


def packagekit_install(pack='ffmpeg'):
    """
    Equivalent of:
     qdbus org.freedesktop.PackageKit /org/freedesktop/PackageKit
           org.freedesktop.PackageKit.Modify.InstallPackageNames
           0 ffmpeg  "show-confirm-search,hide-finished"
    Or:
     qdbus org.freedesktop.PackageKit /org/freedesktop/PackageKit
           org.freedesktop.PackageKit.Query.IsInstalled 0 ffmpeg
    See also (dbus) http://www.freedesktop.org/software/PackageKit/pk-faq.html#session-methods
    Doc: http://blog.fpmurphy.com/2013/11/packagekit-d-bus-abstraction-layer.html
    """
    from PyQt5.QtDBus import QDBusConnection
    from PyQt5.QtDBus import QDBusInterface

    bus = QDBusConnection.sessionBus()
    service_name = 'org.freedesktop.PackageKit'
    service_path = '/org/freedesktop/PackageKit'

    interface = 'org.freedesktop.PackageKit.Query.IsInstalled'
    install = QDBusInterface(service_name, service_path, interface, bus)
    reply = install.call(0, pack, 'show-confirm-search,hide-finished')
    print(reply.arguments())

    interface = 'org.freedesktop.PackageKit.Modify.InstallPackageNames'
    install = QDBusInterface(service_name, service_path, interface, bus)
    reply = install.call(0, pack, 'show-confirm-search,hide-finished')
    print(reply.arguments())


def duration(start: dt.time, stop: dt.time) -> dt.timedelta:
    return dt.datetime.combine(dt.date.min, stop) - dt.datetime.combine(dt.date.min, start)


def timedelta_str(d: dt.timedelta) -> str:
    assert (d.days == 0)
    hours, remainder = divmod(d.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '%02d:%02d:%02d' % (hours, minutes, seconds)


def duration_str(h_m_s_start: [int, int, int], h_m_s_stop: [int, int, int]):
    return timedelta_str(duration(dt.time(*h_m_s_start), dt.time(*h_m_s_stop)))


def video_cut(vid_in, vid_out, ss, to, d, parent):
    # input validation:
    if os.path.isfile(vid_out):
        # QMessageBox(icon, '{} already exists', 'Do you want to replace it ?',
        #             buttons=QMessageBox.Yes, parent=parent)

        msg = '{} already exists\n\nDo you want to replace it ?'.format(vid_out)
        video_ret = QMessageBox.warning(parent, 'File exists', msg, defaultButton=QMessageBox.Cancel)
        if video_ret == QMessageBox.Cancel:
            return
        try:
            os.remove(vid_out)
        except OSError as e:
            msg = 'Cannot write {}, system returned {}.\n\n' \
                  'Change output file name and retry,'.format(vid_out, str(e))
            QMessageBox.critical(parent, 'Wrong file', msg)
            return None

    video_ret = 0
    if os.path.isfile(vid_in):
        ffmpeg = shutil.which('ffmpeg')
        avconv = shutil.which('avconv')
        exe = ffmpeg or avconv
        if not exe:
            msg = 'Install ffmpeg or avconv'
            QMessageBox.critical(parent, 'Missing dependency', msg)
            return

        if exe == avconv:  # end_as_duration:
            stop = ['-t', d]
        else:
            stop = ['-to', to]

        command = [ffmpeg, '-nostdin', '-noaccurate_seek',
                   '-i', vid_in,
                   '-ss', ss,
                   stop[0], stop[1],
                   '-vcodec', 'copy',
                   '-acodec', 'copy',
                   vid_out]
        # "ffmpeg -i input.avi -vcodec copy -acodec copy -ss 00:00:00 -t 00:05:00 output1.avi"
        # 'avconv -i "/media/eoubrayrie/STORENGO/v.mp4" -vcodec copy -acodec copy -ss 00:00:00 -t 00:05:16 output1.avi'
        print(command)  # FIXME output is seemingly random start/duration....
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  #, stderr=subprocess.STDOUT)
        stdout, stderr = p.communicate()
        video_ret = p.poll()
        if video_ret != 0:
            msg = "Error {:d} occured. Check video file or see details.".format(video_ret)
            dmsg = "\n\n{}\n\n{}\n\n{}".format(stdout.decode(), '_' * 30, stderr.decode())
            err_dialog = BiggerMessageBox(QMessageBox.Critical, 'Error during video cut', msg, parent=parent)
            err_dialog.setDetailedText(dmsg)
            err_dialog.exec()

    return video_ret


class Main(QtWidgets.QWidget):
    def __init__(self):
        super(Main, self).__init__()

        # File Picker
        self.video_pick = Picker('Open video', filters='Videos (*.mp4 *.mpg *.avi);;All files (*.*)')
        self.subtitle_pick = Picker('Open subtitle', filters='SubRip Subtitles (*.srt);;All files (*.*)')
        self.save_pick = Picker('Save as', check_exists=False, check_writable=True)

        # Times
        self.start = MinuteSecondEdit(self)
        self.stop = MinuteSecondEdit(self)

        icon_ok = self.style().standardIcon(QtWidgets.QStyle.SP_DialogOkButton)
        self.ok_btn = QPushButton(icon_ok, 'Do it !', self)

        self.init()

    def init(self):

        # events

        self.video_pick.textChanged.connect(self.video_changed)
        for w in (self.video_pick, self.subtitle_pick, self.start, self.stop, self.save_pick):
            w.textChanged.connect(self.doit_controller)

        # times

        times = QtWidgets.QHBoxLayout()
        times.addWidget(self.start)
        times.addWidget(self.stop)
        times.addStretch(1)

        # Buttons

        self.ok_btn.setEnabled(False)
        self.ok_btn.clicked.connect(self.do_it)
        icon_quit = self.style().standardIcon(QtWidgets.QStyle.SP_DialogCancelButton)
        quit_btn = QPushButton(icon_quit, 'Quit', self)
        quit_btn.clicked.connect(exit)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.ok_btn)
        hbox.addWidget(quit_btn)

        # Stitch it

        # vbox = QtWidgets.QVBoxLayout()
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel('Video:'), 1, 0)
        grid.addWidget(self.video_pick, 1, 1)
        grid.addWidget(QLabel('Subtitles:'), 2, 0)
        grid.addWidget(self.subtitle_pick, 2, 1)
        grid.addWidget(QLabel('Start / Stop (HHMMSS):'), 3, 0)
        grid.addLayout(times, 3, 1)
        grid.addWidget(QLabel('Output:'), 4, 0)
        grid.addWidget(self.save_pick, 4, 1)
        # grid.addStretch(1)
        grid.addLayout(hbox, 5, 1)

        self.setLayout(grid)

    # noinspection PyUnusedLocal
    @QtCore.pyqtSlot()
    def video_changed(self, *args, **kw):
        p = self.video_pick.get_text()
        if p:
            self.subtitle_pick.set_text(str(Path(p).with_suffix('.srt')))

    # noinspection PyUnusedLocal
    @QtCore.pyqtSlot()
    def doit_controller(self, *args, **kw):
        ok = lambda w: w.hasAcceptableInput()
        self.ok_btn.setEnabled((ok(self.video_pick) or ok(self.subtitle_pick)) and
                               ok(self.start) and ok(self.stop) and ok(self.save_pick))

    def do_it(self):
        vid_in = self.video_pick.get_text()
        vid_out = self.save_pick.get_text() + os.path.splitext(vid_in)[1]
        ss = self.start.get_time()
        to = self.stop.get_time()
        d = duration_str(self.start.get_h_m_s(), self.stop.get_h_m_s())

        video_ret = video_cut(vid_in, vid_out, ss, to, d, self)

        if video_ret == 0:
            sbt_out = self.cut_subtitle()
            opn = shutil.which('xdg-open')
            if vid_out and os.path.isfile(vid_out):
                f = vid_out
            elif sbt_out and os.path.isfile(sbt_out):
                f = sbt_out
            else:  # This should not happen as button is greyed out
                msg = ''
                QMessageBox.warning(self, 'no file was generated', msg, defaultButton=QMessageBox.NoButton)
                return
            if opn:
                subprocess.Popen([opn, f])

    def cut_subtitle(self):
        sbt_in = self.subtitle_pick.get_text()
        if os.path.isfile(sbt_in):
            sbt_out = self.save_pick.get_text() + os.path.splitext(sbt_in)[1]
            h1, m1, s1 = self.start.get_h_m_s()
            h2, m2, s2 = self.stop.get_h_m_s()
            subs = pysrt.open(sbt_in, error_handling=pysrt.ERROR_LOG)  # , encoding='iso-8859-1')
            print('Decoded {} with {} items'.format(sbt_out, len(subs)))
            part = subs.slice(starts_after={'hours': h1, 'minutes': m1, 'seconds': s1},
                              ends_before={'hours': h2, 'minutes': m2, 'seconds': s2})
            print('Sliced {} items'.format(len(part)))
            part.shift(seconds=-duration(dt.time(h1, m1, s1), dt.time(h2, m2, s2)).total_seconds())
            part.save(path=sbt_out)
            print('Successfully written', sbt_out)
            return sbt_out


def main():
    app = QtWidgets.QApplication(sys.argv)

    # for path in QtGui.QIcon.themeSearchPaths():
    #     print("%s/%s" % (path, QtGui.QIcon.themeName()))

    icon = QtGui.QIcon()
    # icon.addPixmap(QtGui.QPixmap(":/icons/hicolor/128x128/apps/quickcut.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)

    app.setWindowIcon(icon)

    w = Main()

    # Set window size.
    # screen = QDesktopWidget().screenGeometry()
    # w.setGeometry(0, 0, screen.width(), screen.height())
    # w.showMaximized()
    w.normalGeometry()

    # Set window title
    w.setWindowTitle("QuickCut")

    # Show window
    w.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
