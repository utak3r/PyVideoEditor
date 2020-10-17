import sys
import subprocess
import asyncio
from PySide2.QtWidgets import (QApplication, QLabel, QPushButton,
                               QVBoxLayout, QWidget, QMessageBox,
                               QFileDialog, QMainWindow, QDialog)
from PySide2.QtCore import (QCoreApplication, Qt, Slot, QUrl, QFile, QIODevice, QFileInfo)
from PySide2.QtUiTools import QUiLoader
from PySide2.QtMultimedia import (QMediaPlayer, QMediaPlaylist)
from PySide2.QtMultimediaWidgets import QVideoWidget
from Settings import Settings


class ProcessLogView(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.initUI("ProcessLogView.ui")

        self.process = None
        self.Form.btnOk.clicked.connect(self.accept)
        self.Form.btnCancel.clicked.connect(self.terminate)

    def initUI(self, filename):
        loader = QUiLoader()
        file = QFile(filename)
        file.open(QIODevice.ReadOnly)
        self.Form = loader.load(file, self)
        file.close()

    def runCommand(self, command):
        self.show()
        self.addLog(command)
        QCoreApplication.processEvents()
        asyncio.run(self.run(command))

    async def readStream(self, stream):
        while self.process.returncode is None:
            try:
                line = await stream.readline()
            except (asyncio.LimitOverrunError, ValueError):
                continue
            if line:
                line = line.decode("utf-8")[:-1]
                print(line)
                self.addLog(line)
                QCoreApplication.processEvents()
            else:
                break

    async def run(self, command):
        self.Form.btnOk.setEnabled(False)
        self.process = await asyncio.create_subprocess_shell(command, stdin=asyncio.subprocess.DEVNULL, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        self.Form.btnCancel.setEnabled(True)
        await asyncio.wait([self.readStream(self.process.stdout), self.readStream(self.process.stderr)])
        self.Form.btnCancel.setEnabled(False)
        self.Form.btnOk.setEnabled(True)


    @Slot()
    def terminate(self):
        if self.process is not None:
            self.process.terminate()
        self.reject()

    @Slot()
    def addLog(self, text):
        self.Form.logText.appendPlainText(text)


class VideoEditorMainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.initUI("PyVideoEditorMainWindow.ui")

        self.videoSourceFile = ''
        videoWidget = QVideoWidget()
        videoplayerlayout = QVBoxLayout()
        videoplayerlayout.addWidget(videoWidget)
        self.centralWidget().playerWidget.setLayout(videoplayerlayout)

        self.player = QMediaPlayer()
        self.player.setVideoOutput(videoWidget)
        self.player.durationChanged.connect(self.videoDurationChanged)
        self.player.positionChanged.connect(self.videoPositionChanged)

        self.centralWidget().videoSlider.valueChanged.connect(self.videoSeekSliderMoved)
        self.centralWidget().btnPlayPause.clicked.connect(self.playPauseClicked)
        self.centralWidget().btnLoadVideo.clicked.connect(self.openVideo)

        self.fillTargetFormats()
        self.centralWidget().btnConvert.clicked.connect(self.convertButtonClicked)

        self.settings = Settings("utak3r", "PyVideoEditor")
        self.settings.readSettings()
        #print("LastDir = " + self.settings.getLastDir())

    def initUI(self, filename):
        loader = QUiLoader()
        file = QFile(filename)
        file.open(QIODevice.ReadOnly)
        self.setCentralWidget(loader.load(file, self))
        file.close()

    def closeEvent(self, event):
        self.settings.writeSettings()
        event.accept()

    @Slot()
    def openVideo(self):
        filename = QFileDialog.getOpenFileName(self, "Open video", self.settings.getLastDir(), "Video files (*.avi *.mp4)")
        if filename[0] != "":
            self.videoSourceFile = filename[0]
            self.player.setMedia(QUrl.fromUserInput(self.videoSourceFile))
            print('Opening video: ' + self.videoSourceFile)
            self.settings.setLastDir(QFileInfo(self.videoSourceFile).absolutePath())
            self.player.play()

    @Slot()
    def videoDurationChanged(self, duration):
        print('Video duration: ' + repr(duration))
        self.centralWidget().videoSlider.setRange(0, duration)
        self.centralWidget().videoSlider.setSingleStep(duration/500)
        self.centralWidget().videoSlider.setPageStep(duration/2000)

    @Slot()
    def videoPositionChanged(self, position):
        if not self.centralWidget().videoSlider.isSliderDown():
            self.centralWidget().videoSlider.setValue(position)

    @Slot()
    def videoSeekSliderMoved(self, value):
        self.player.setPosition(value)

    @Slot()
    def playPauseClicked(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def fillTargetFormats(self):
        self.centralWidget().cbxTargetFormat.clear()
        self.centralWidget().cbxTargetFormat.addItem('H.264 AAC', ('H.264 AAC', '.mp4', '-c:v libx264 -preset medium -tune film -c:a aac'))
        self.centralWidget().cbxTargetFormat.addItem('DNxHD 185Mbps PCM s24LE', ('DNxHD 185Mbps PCM s24LE', '.mov', '-c:v dnxhd -b:v 185M -c:a pcm_s24le'))
        self.centralWidget().cbxTargetFormat.addItem('ProRes YUV422', ('ProRes YUV422', '.mov', '-c:v prores_ks -profile:v 3 -vendor ap10 -pix_fmt yuv422p10le'))

    @Slot()
    def convertButtonClicked(self):
        ffmpeg = "c:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe"
        codec = self.centralWidget().cbxTargetFormat.currentData()
        params = '-i ' + '"' + self.videoSourceFile + '" ' + codec[2] + ' "' + self.videoSourceFile + '.converted' + codec[1] + '"'
        command = '"' + ffmpeg + '" ' + params

        self.logView = ProcessLogView()
        #self.logView.show()
        self.logView.runCommand(command)


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)

    mainWnd = VideoEditorMainWindow()
    mainWnd.resize(800, 600)
    mainWnd.show()

    sys.exit(app.exec_())
