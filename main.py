import os
import subprocess
import sys
import shutil
import datetime as dt
from pathlib import Path

import pysrt

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox

"""
Uses ffmpeg - http://manpages.ubuntu.com/manpages/vivid/en/man1/ffmpeg.1.html
"""

__author__ = 'Edward Oubrayrie'

lastDir = os.path.expandvars('$HOME')
# or, better, save & take it from config file:
# file_path =  os.path.join(QDir.home().absolutePath(), ".application_name")


def duration(start: dt.time, stop: dt.time) -> dt.timedelta:
    return dt.datetime.combine(dt.date.min, stop) - dt.datetime.combine(dt.date.min, start)


def timedelta_str(d: dt.timedelta) -> str:
    assert (d.days == 0)
    hours, remainder = divmod(d.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '%02d:%02d:%02d' % (hours, minutes, seconds)


def duration_str(h_m_s_start: [int, int, int], h_m_s_stop: [int, int, int]):
    return timedelta_str(duration(dt.time(*h_m_s_start), dt.time(*h_m_s_stop)))


class FileValidator(QValidator):
    def __init__(self, *args):
        super().__init__(*args)

    def validate(self, s, pos):
        if os.path.isfile(s):
            return QValidator.Acceptable, s, pos
        return QValidator.Intermediate, s, pos

    def fixup(self, s):
        pass


class Picker(QtWidgets.QWidget):  # TODO composition instead of inheritance

    def __init__(self, title, label='Select', exists=True, save=False, filters=None):
        super(Picker, self).__init__()
        self.save = save
        self.title = title
        self.filters = filters

        hbox = QtWidgets.QHBoxLayout()
        if exists:
            self.wtext = ValidatedLineEdit(FileValidator(), self)
        else:
            self.wtext = QLineEdit(self)
        self.wtext.setMinimumWidth(300)
        hbox.addWidget(self.wtext)
        # Expose some methods
        self.textChanged = self.wtext.textChanged
        self.hasAcceptableInput = self.wtext.hasAcceptableInput
        self.set_text = self.wtext.setText

        # self.icon = QtWidgets.QIcon.fromTheme("places/user-folders")
        icon = self.style().standardIcon(QtWidgets.QStyle.SP_DialogOpenButton)
        # self.icon.addPixmap(QPixmap(":/icons/folder_16x16.gif"), QtWidgets.QIcon.Normal, QtWidgets.QIcon.Off)
        self.wbtn = QPushButton(icon, label, self)

        self.wbtn.clicked.connect(self.pick)
        hbox.addWidget(self.wbtn)
        self.setLayout(hbox)

    @pyqtSlot()
    def pick(self):
        dlg = QFileDialog(self, self.title, lastDir, self.filters)
        if self.save:
            dlg.setDefaultSuffix(self._extension)
            dlg.setAcceptMode(QFileDialog.AcceptSave)
        else:
            dlg.setAcceptMode(QFileDialog.AcceptOpen)
            dlg.setFileMode(QFileDialog.ExistingFile)
        if not dlg.exec():
            return

        self.wtext.setText(dlg.selectedFiles()[0])

    def get_text(self):
        return self.wtext.text()


class ValidatedLineEdit(QLineEdit):
    """ http://snorf.net/blog/2014/08/09/using-qvalidator-in-pyqt4-to-validate-user-input/ """

    def __init__(self, validator, *args):
        super().__init__(*args)

        self.setValidator(validator)
        self.textChanged.connect(self.check_state)
        self.textChanged.emit(self.text())  # check initial text

    @pyqtSlot()
    def check_state(self, *args, **kwargs):
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            color = '#c4df9b'  # green
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a'  # yellow
        else:
            color = '#f6989d'  # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)


class MinuteSecond(ValidatedLineEdit):

    def __init__(self, *args):
        regexp = QtCore.QRegExp('^(([0-9]?[0-9]:?)?[0-5][0-9]:?)?[0-5][0-9]$')
        validator = QtGui.QRegExpValidator(regexp)
        super().__init__(validator, *args)

        self.setValidator(validator)
        self.textChanged.connect(self.check_state)
        self.textChanged.emit(self.text())  # check initial text

    def get_time(self):
        t = self.text()
        if len(t) > 2 and ':' not in t:
            t = t[:-2] + ':' + t[-2:]
        if len(t) > 5 and ':' not in t[:-5]:
            t = t[:-5] + ':' + t[-5:]
        return t

    def get_h_m_s(self):
        t = self.get_time()
        if len(t) < 8:
            t = '00:00:00'[:8 - len(t)] + t
        h = int(t[0:2])
        m = int(t[3:5])
        s = int(t[6:8])
        return h, m, s


class BiggerMessageBox(QMessageBox):

    # This is a much better way to extend __init__
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizeGripEnabled(True)  # ... but still not resizable
        self.resize(self.sizeHint())

    def resizeEvent(self, event):
        result = super().resizeEvent(event)

        details_box = self.findChild(QtWidgets.QTextEdit)
        if details_box is not None:
            details_box.setFixedSize(details_box.sizeHint())  # not good
            details_box.setFixedSize(1000, 700)

        return result


class Main(QtWidgets.QWidget):
    def __init__(self):
        super(Main, self).__init__()

        # File Picker
        self.video_pick = Picker('Open video', filters='Videos (*.mp4 *.mpg *.avi);;All files (*.*)')
        self.subtitle_pick = Picker('Open subtitle', filters='SubRip Subtitles (*.srt);;All files (*.*)')
        self.save_pick = Picker('Save as', exists=False, save=True)

        # Times
        self.start = MinuteSecond(self)
        self.stop = MinuteSecond(self)

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

    def video_changed(self, *args, **kw):
        p = self.video_pick.get_text()
        if p:
            self.subtitle_pick.set_text(str(Path(p).with_suffix('.srt')))

    def doit_controller(self, *args, **kw):
        ok = lambda w: w.hasAcceptableInput()
        self.ok_btn.setEnabled((ok(self.video_pick) or ok(self.subtitle_pick))
                               and ok(self.start) and ok(self.stop) and ok(self.save_pick))

    def do_it(self):
        vid_in = self.video_pick.get_text()
        vid_out = self.save_pick.get_text() + os.path.splitext(vid_in)[1]
        ss = self.start.get_time()
        d = duration_str(self.start.get_h_m_s(), self.stop.get_h_m_s())

        # input validation:
        if os.path.isfile(vid_out):
            # QMessageBox(icon, '{} already exists', 'Do you want to replace it ?',
            #             buttons=QMessageBox.Yes, parent=self)

            msg = '{} already exists\n\nDo you want to replace it ?'.format(vid_out)
            ret = QMessageBox.warning(self, 'File exists', msg, defaultButton=QMessageBox.Cancel)
            if ret == QMessageBox.Cancel:
                return
            try:
                os.remove(vid_out)
            except OSError as e:
                msg = 'Cannot write {}, system returned {}.\n\n' \
                      'Change output file name and retry,'.format(vid_out, str(e))
                QMessageBox.critical(self, 'Wrong file', msg)
                return

        ffmpeg = shutil.which('ffmpeg') or shutil.which('avconv')
        command = [ffmpeg, '-nostdin', '-noaccurate_seek',
                   '-ss', ss,
                   '-t', d,
                   '-i', vid_in,
                   '-vcodec', 'copy',
                   '-acodec', 'copy',
                   vid_out]
        # "ffmpeg -i input.avi -vcodec copy -acodec copy -ss 00:00:00 -t 00:05:00 output1.avi"
        # 'avconv -i "/media/eoubrayrie/STORENGO/v.mp4" -vcodec copy -acodec copy -ss 00:00:00 -t 00:05:16 output1.avi'
        print(command)
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  #, stderr=subprocess.STDOUT)
        stdout, stderr = p.communicate()
        ret = p.poll()
        if ret != 0:
            msg = "Error {:d} occured. Check video file or see details.".format(ret)
            dmsg = "\n\n{}\n\n{}\n\n{}".format(stdout.decode(), '_'*30, stderr.decode())
            err_dialog = BiggerMessageBox(QMessageBox.Critical, 'Error during video cut', msg, parent=self)
            err_dialog.setDetailedText(dmsg)
            err_dialog.exec()
        else:
            self.cut_subtitle()
            opn = shutil.which('xdg-open')
            if opn:
                subprocess.Popen([opn, vid_out])

    def cut_subtitle(self):
        sbt_in = self.subtitle_pick.get_text()
        if os.path.isfile(sbt_in):
            sbt_out = self.save_pick.get_text() + os.path.splitext(sbt_in)[1]
            h1, m1, s1 = self.start.get_h_m_s()
            h2, m2, s2 = self.stop.get_h_m_s()
            subs = pysrt.open(sbt_in)  # , encoding='iso-8859-1')
            part = subs.slice(starts_after={'hours': h1, 'minutes': m1, 'seconds': s1},
                              ends_before={'hours': h2, 'minutes': m2, 'seconds': s2})
            part.shift(seconds=-2)
            part.save(path=sbt_out)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

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

