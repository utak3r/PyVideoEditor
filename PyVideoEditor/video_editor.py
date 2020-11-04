import sys
import math
from PySide2.QtWidgets import QApplication, QVBoxLayout, QFileDialog, QMainWindow
from PySide2.QtCore import QCoreApplication, Qt, Slot, QUrl, QFile, QIODevice, QFileInfo
from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtMultimedia import QMediaPlayer
from PySide2.QtMultimediaWidgets import QVideoWidget
from PyVideoEditor.settings_tools import Settings, SettingsDialog
from PyVideoEditor.process_tools import ProcessRunner
from PyVideoEditor.video_tools import TimelineMarks


class VideoEditorMainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.init_ui("PyVideoEditor/PyVideoEditorMainWindow.ui")
        self.runner = None
        self.settings_dlg = None
        self.timeline_marks = TimelineMarks()

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
        self.centralWidget().btnSetMarkIn.clicked.connect(self.set_mark_in)
        self.centralWidget().btnSetMarkOut.clicked.connect(self.set_mark_out)
        self.centralWidget().btnResetMarks.clicked.connect(self.clear_inout_marks)

        self.fill_convert_target_formats()
        self.centralWidget().btnConvert.clicked.connect(self.convert_button_clicked)

        self.settings = Settings("utak3r", "PyVideoEditor")
        self.settings.read_settings()
        self.setGeometry(self.settings.main_wnd_geometry())
        self.centralWidget().btnSettings.clicked.connect(self.open_settings)

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
            #print('Opening video: ' + self.video_source_file)
            self.settings.set_last_dir(QFileInfo(self.video_source_file).absolutePath())
            self.player.play()

    @Slot()
    def video_duration_changed(self, duration):
        #print('Video duration: ' + repr(duration))
        self.centralWidget().videoSlider.setRange(0, duration)
        self.centralWidget().videoSlider.setSingleStep(duration/500)
        self.centralWidget().videoSlider.setPageStep(duration/2000)
        self.clear_inout_marks()

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
        if ffmpeg != "":
            codec = self.centralWidget().cbxTargetFormat.currentData()
            if self.video_source_file != "" and codec[2] != "" and codec[1] != "":
                duration_params = ""
                if self.timeline_marks.is_trimmed():
                    duration_params = ' -ss ' + self.timeline_marks.timecode_start() + ' -t ' + '{} '.format(math.floor(self.timeline_marks.duration() / 1000))
                params = '-i ' + '"' + self.video_source_file + '" ' + duration_params + codec[2] + ' "' + self.video_source_file + '.converted' + codec[1] + '"'
                command = '"' + ffmpeg + '" ' + params
                self.runner = ProcessRunner()
                self.runner.run_command(command)

    @Slot()
    def open_settings(self):
        """ Show settings dialog. """
        self.settings_dlg = SettingsDialog(self.settings)
        self.settings_dlg.finished.connect(self.settings_closed)
        self.settings_dlg.open()
    
    @Slot()
    def settings_closed(self):
        """ Called when settings dialog is closed. """
        self.settings.write_settings()

    @Slot()
    def set_mark_in(self):
        """ Set Mark In for the current timecode. """
        timecode = self.player.position()
        if timecode >= 0:
            self.timeline_marks.mark_in = timecode
            #print("Mark in: " + self.timeline_marks.timecode_start())
            self.centralWidget().lblTimecodeRange.setText(self.timeline_marks.current_range())
    
    @Slot()
    def set_mark_out(self):
        """ Set Mark Out for the current timecode. """
        timecode = self.player.position()
        if timecode >= 0:
            self.timeline_marks.mark_out = timecode
            #print("Mark out: " + self.timeline_marks.timecode_end())
            self.centralWidget().lblTimecodeRange.setText(self.timeline_marks.current_range())
    
    @Slot()
    def clear_inout_marks(self):
        """ Clear any in/out marks. """
        self.timeline_marks.reset(self.player.duration())
        self.centralWidget().lblTimecodeRange.setText(self.timeline_marks.current_range())
