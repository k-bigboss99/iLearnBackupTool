import os
import requests
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtWidgets import QProgressBar, QLabel
from PyQt5.QtCore import QCoreApplication, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
import language
import subprocess
import img_qr


downfile = 'iLearnBackupTool.exe'
tempfile = '~$iLearnBackupTool.exe'


class UpdaterGUI(QWidget):
    class Downloader(QThread):
        gotchunk = pyqtSignal(float)
        finished = pyqtSignal()
        error = pyqtSignal(str)

        def __init__(self, url):
            super().__init__()
            self.url = url

        def run(self):
            try:
                binfile = open(tempfile, 'wb')
                dlink = requests.Session().get(self.url, stream=True)
                total_size = int(dlink.headers['Content-Length'])
                chunk_size = 512
                recived = 0

                for chunk in dlink.iter_content(chunk_size=chunk_size):
                    recived += binfile.write(chunk)
                    self.gotchunk.emit(recived / total_size)

                self.finished.emit()
                binfile.close()
                dlink.close()
            except Exception as e:
                self.error.emit(str(e))

    def __init__(self):
        super().__init__()
        self.durl = 'https://raw.githubusercontent.com/fcu-d0441320/iLearnBackupTool/master/iLearnBackupTool.exe'
        self.progressbar = QProgressBar(self)
        self.progresslabel = QLabel(self.progressbar)
        self.initGUI()
        self.setWindowIcon(QIcon(":img/Main_Icon.png"))

        self.downloader = self.Downloader(self.durl)
        self.downloader.gotchunk.connect(self.setProgressValue)
        self.downloader.error.connect(self.errorHandler)
        self.downloader.finished.connect(self.finished)
        self.string = language.string()

    def startDownload(self,language):
        self.string.setLanguage(language)
        self.setWindowTitle(self.string._('iLearnBackupTool Updater'))
        self.show()
        self.downloader.start()

    def initGUI(self):

        self.resize(975, 35)

        self.progressbar.setGeometry(5, 5, 1000, 25)
        self.progressbar.setValue(0)

        w = 50
        h = 30
        x = (self.progressbar.width() / 2 - w / 2)
        y = (self.progressbar.height() / 2 - h / 2)
        self.progresslabel.setGeometry(x, y, w, h)
        self.progresslabel.setText('{0:2d}%'.format(0))

    def setProgressValue(self, val):
        self.progressbar.setValue(round(val * 100, 2))
        self.progresslabel.setText('{0:.2f}%'.format(val * 100))

    def errorHandler(self, err_msg):
        QMessageBox.information(self, self.string._('Oops! Something error!'), err_msg, QMessageBox.Ok)
        os.remove(tempfile)
        QCoreApplication.instance().quit()

    def finished(self):
        QMessageBox.information(self, self.string._('Download finish!'), self.string._('Download success!'), QMessageBox.Ok)
        with open("update.cmd","w")as f:
            f.write('@ echo %s\n'%(self.string._('Update is in process...')))
            f.write('@ Title %s\n'%(self.string._('Update is in process...')))
            f.write('@ ping 127.0.0.1 -n 3 -w 1000 > nul\n')
            f.write('@ taskkill -F -T -FI "IMAGENAME eq iLearnBackupTool.exe"\n')
            f.write('@ ping 127.0.0.1 -n 2 -w 1000 > nul\n')
            f.write("@ del iLearnBackupTool.exe\n")
            f.write("@ rename %s %s\n"%(tempfile,downfile))
            f.write("@ start iLearnBackupTool\n")
            f.write("@ exit\n")
        subprocess.Popen("update.cmd")
        QCoreApplication.instance().quit()

    def closeWindow(self):
        QCoreApplication.instance().quit()
