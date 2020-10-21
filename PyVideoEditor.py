import sys
from PySide2.QtWidgets import QApplication, QVBoxLayout, QFileDialog, QMainWindow
from PySide2.QtCore import QCoreApplication, Qt, Slot, QUrl, QFile, QIODevice, QFileInfo
from PySide2.QtUiTools import QUiLoader
from PySide2.QtMultimedia import QMediaPlayer
from PySide2.QtMultimediaWidgets import QVideoWidget
from settings_tools import Settings
from process_tools import ProcessRunner


class VideoEditorMainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.init_ui("PyVideoEditorMainWindow.ui")
        self.runner = None

        self.video_source_file = ''
        videoWidget = QVideoWidget()
        videoplayerlayout = QVBoxLayout()
        videoplayerlayout.addWidget(videoWidget)
        self.centralWidget().playerWidget.setLayout(videoplayerlayout)

        self.player = QMediaPlayer()
        self.player.setVideoOutput(videoWidget)
        self.player.durationChanged.connect(self.video_duration_changed)
        self.player.positionChanged.connect(self.video_position_changed)

        self.centralWidget().videoSlider.valueChanged.connect(self.video_seek_slider_moved)
        self.centralWidget().btnPlayPause.clicked.connect(self.play_pause_clicked)
        self.centralWidget().btnLoadVideo.clicked.connect(self.open_video)

        self.fill_convert_target_formats()
        self.centralWidget().btnConvert.clicked.connect(self.convert_button_clicked)

        self.settings = Settings("utak3r", "PyVideoEditor")
        self.settings.read_settings()
        self.setGeometry(self.settings.main_wnd_geometry())

    def init_ui(self, filename):
        loader = QUiLoader()
        file = QFile(filename)
        file.open(QIODevice.ReadOnly)
        self.setCentralWidget(loader.load(file, self))
        file.close()

    def closeEvent(self, event):
        self.settings.set_main_wnd_geometry(self.geometry())
        self.settings.write_settings()
        event.accept()

    @Slot()
    def open_video(self):
        filename = QFileDialog.getOpenFileName(self, "Open video", self.settings.last_dir(), "Video files (*.avi *.mp4)")
        if filename[0] != "":
            self.video_source_file = filename[0]
            self.player.setMedia(QUrl.fromUserInput(self.video_source_file))
            print('Opening video: ' + self.video_source_file)
            self.settings.set_last_dir(QFileInfo(self.video_source_file).absolutePath())
            self.player.play()

    @Slot()
    def video_duration_changed(self, duration):
        print('Video duration: ' + repr(duration))
        self.centralWidget().videoSlider.setRange(0, duration)
        self.centralWidget().videoSlider.setSingleStep(duration/500)
        self.centralWidget().videoSlider.setPageStep(duration/2000)

    @Slot()
    def video_position_changed(self, position):
        if not self.centralWidget().videoSlider.isSliderDown():
            self.centralWidget().videoSlider.setValue(position)

    @Slot()
    def video_seek_slider_moved(self, value):
        self.player.setPosition(value)

    @Slot()
    def play_pause_clicked(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def fill_convert_target_formats(self):
        self.centralWidget().cbxTargetFormat.clear()
        self.centralWidget().cbxTargetFormat.addItem('H.264 AAC', ('H.264 AAC', '.mp4', '-c:v libx264 -preset medium -tune film -c:a aac'))
        self.centralWidget().cbxTargetFormat.addItem('DNxHD 185Mbps PCM s24LE', ('DNxHD 185Mbps PCM s24LE', '.mov', '-c:v dnxhd -b:v 185M -c:a pcm_s24le'))
        self.centralWidget().cbxTargetFormat.addItem('ProRes YUV422', ('ProRes YUV422', '.mov', '-c:v prores_ks -profile:v 3 -vendor ap10 -pix_fmt yuv422p10le'))

    @Slot()
    def convert_button_clicked(self):
        ffmpeg = self.settings.ffmpeg()
        ffmpeg = "c:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe"
        codec = self.centralWidget().cbxTargetFormat.currentData()
        params = '-i ' + '"' + self.video_source_file + '" ' + codec[2] + ' "' + self.video_source_file + '.converted' + codec[1] + '"'
        command = '"' + ffmpeg + '" ' + params

        self.runner = ProcessRunner()
        self.runner.run_command(command)


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)

    mainWnd = VideoEditorMainWindow()
    mainWnd.show()

    sys.exit(app.exec_())
