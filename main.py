import os
import subprocess
import sys
from pathlib import Path
try:
    from PyQt4.QtCore import __init__ as QtCore  # stupid PyCharm
    from PyQt4.QtCore.__init__ import pyqtSlot
    from PyQt4.QtGui import __init__ as QtGui  # stupid PyCharm
    from PyQt4.QtGui.__init__ import QFileDialog, QApplication, QWidget, QMainWindow, QLineEdit, \
        QDesktopWidget, QHBoxLayout, QVBoxLayout, QPushButton
except ImportError:
    from PyQt4.QtCore import pyqtSlot
    from PyQt4 import QtGui, QtCore
    from PyQt4.QtGui import QFileDialog, QApplication, QWidget, QMainWindow, QLineEdit, \
        QDesktopWidget, QHBoxLayout, QVBoxLayout, QPushButton


__author__ = 'Edward Oubrayrie'

lastDir = os.path.expandvars('$HOME')


class Picker(QWidget):

    def __init__(self, title, label='Select', save=False, filters=None):
        super(Picker, self).__init__()
        self.save = save
        self.title = title
        self.filters = filters

        hbox = QtGui.QHBoxLayout()
        self.text = QLineEdit(self)
        self.text.setMinimumWidth(300)
        hbox.addWidget(self.text)

        # self.icon = QtGui.QIcon.fromTheme("places/user-folders")
        self.icon = self.style().standardIcon(QtGui.QStyle.SP_DialogOpenButton)
        # self.icon.addPixmap(QtGui.QPixmap(":/icons/folder_16x16.gif"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn = QPushButton(self.icon, label, self)

        self.btn.clicked.connect(self.pick)
        hbox.addWidget(self.btn)
        self.setLayout(hbox)

    @pyqtSlot()
    def pick(self):
        dlg = QFileDialog(self, self.title, lastDir, self.filters)
        if self.save:
            dlg.setDefaultSuffix(self._extension)
            dlg.setAcceptMode(QFileDialog.AcceptSave)
        else:
            dlg.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
            dlg.setFileMode(QtGui.QFileDialog.ExistingFile)
        if not dlg.exec():
            return

        self.text.setText(dlg.selectedFiles()[0])

    def get_text(self):
        return self.text.text()


class MinuteSecond(QLineEdit):
    """ http://snorf.net/blog/2014/08/09/using-qvalidator-in-pyqt4-to-validate-user-input/ """

    def __init__(self, *args, **kw):
        super(MinuteSecond, self).__init__(*args)

        regexp = QtCore.QRegExp('^[0-9][0-9]:?[0-9][0-9]$')
        validator = QtGui.QRegExpValidator(regexp)
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

    def get_time(self):
        t = self.text()
        if len(t) < 2:  # seconds
            return self
        if ":" not in self:
            return t[:-2] + ":" + t[-2:]
        return self




class Main(QWidget):

    def __init__(self):
        super(Main, self).__init__()

        # File Picker
        self.video_pick = Picker('Open video', filters="Videos (*.mp4 *.mpg *.avi);;All files (*.*)")
        self.subtitle_pick = Picker('Open subtitle')
        self.save_pick = Picker('Save as', save=True)

        # Times
        self.start = MinuteSecond(self)
        self.stop = MinuteSecond(self)

        self.initUI()

    def initUI(self):

        times = QtGui.QHBoxLayout()
        times.addWidget(self.start)
        times.addWidget(self.stop)
        times.addStretch(1)

        # Buttons

        ok_btn = QtGui.QPushButton("Do it !")
        ok_btn.clicked.connect(self.do_it)
        quit_btn = QtGui.QPushButton("Quit")
        quit_btn.clicked.connect(exit)

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(ok_btn)
        hbox.addWidget(quit_btn)

        # Stitch it

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.video_pick)
        vbox.addWidget(self.subtitle_pick)
        vbox.addLayout(times)
        vbox.addWidget(self.save_pick)
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def do_it(self):
        vid_in = self.video_pick.get_text()
        vid_out = self.save_pick.get_text() + os.path.splitext(vid_in)
        ss = self.start.get_time()
        st = self.stop.get_time()
        ffmpeg = 'ffmpeg' or "..."
        command = [ffmpeg, vid_in, '-out', vid_out, '-ss', ss, '-st', st]
        "ffmpeg -i input.avi -vcodec copy -acodec copy -ss 00:00:00 -t 00:05:00 output1.avi"
        'avconv -i "/media/eoubrayrie/STORENGO/some movie title.mp4" -vcodec copy -acodec copy -ss 00:00:00 -t 00:05:16 output1.avi'
        print(command)
        # subprocess.Popen(command)
            self.cut_subtitle(sbt_in, ss, st)

    def cut_subtitle(self):
        sbt_in = self.subtitle_pick.get_text()
        if os.path.isfile(sbt_in):
            sbt_out = self.save_pick.get_text() + os.path.splitext(sbt_in)
            ss = self.start.get_time()
            st = self.stop.get_time()

if __name__ == '__main__':

    app = QApplication(sys.argv)

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


# EXAMPLE

class Example(QtGui.QWidget):

    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def initUI(self):

        title = QtGui.QLabel('Title')
        author = QtGui.QLabel('Author')
        review = QtGui.QLabel('Review')

        titleEdit = QtGui.QLineEdit()
        authorEdit = QtGui.QLineEdit()
        reviewEdit = QtGui.QTextEdit()

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(title, 1, 0)
        grid.addWidget(titleEdit, 1, 1)

        grid.addWidget(author, 2, 0)
        grid.addWidget(authorEdit, 2, 1)

        grid.addWidget(review, 3, 0)
        grid.addWidget(reviewEdit, 3, 1, 5, 1)

        self.setLayout(grid)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Review')
        self.show()