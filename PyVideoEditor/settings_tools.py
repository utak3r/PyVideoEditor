"""All the settings related stuff.
   Storing, restoring, accessing etc. any individual setting, or all of them at once.
   Provides also a dialog for editing some of the settings.
"""

from PySide2.QtCore import Qt, QSettings, QRect, QFile, QIODevice, Slot, QFileInfo
from PySide2.QtWidgets import QDialog, QFileDialog, QTableWidget, QTableWidgetItem
from PySide2.QtUiTools import QUiLoader
from PyVideoEditor.video_tools import VideoPreset

class Settings():
    """This class holds all the settings for the app."""
    def __init__(self):
        self.settings_ = QSettings("PyVideoEditor.ini", QSettings.IniFormat)

        # settings
        self.ffmpeg_ = "ffmpeg.exe"
        self.lastdir_ = "."
        self.main_wnd_geometry_ = QRect(640, 250, 800, 500)
        self.video_presets = []

    def read_settings(self):
        """Read settings from a storage and save them in internal variables for later use."""
        self.settings_.beginGroup("General")
        self.set_ffmpeg(self.settings_.value("FFmpegPath", "ffmpeg.exe"))
        self.set_last_dir(self.settings_.value("LastDir", "."))
        self.settings_.endGroup()
        self.settings_.beginGroup("Geometry")
        self.set_main_wnd_geometry(self.settings_.value("MainWindowGeometry"))
        self.settings_.endGroup()
        self.settings_.beginGroup("Video presets")
        self.video_presets.clear()
        entries = self.settings_.allKeys()
        if len(entries) > 0:
            for entry in entries:
                preset = self.settings_.value(entry)
                self.video_presets.append(preset)
        else:
            # default video presets:
            preset = VideoPreset('H.264 AAC', '.mp4', '-c:v libx264 -preset medium -tune film -c:a aac')
            self.video_presets.append(preset)
            preset = VideoPreset('DNxHD 185Mbps PCM s24LE', '.mov', '-c:v dnxhd -b:v 185M -c:a pcm_s24le')
            self.video_presets.append(preset)
            preset = VideoPreset('ProRes YUV422', '.mov', '-c:v prores_ks -profile:v 3 -vendor ap10 -pix_fmt yuv422p10le')
            self.video_presets.append(preset)
        self.settings_.endGroup()

    def write_settings(self):
        """Save all the settings from internal variables into a storage."""
        self.settings_.beginGroup("General")
        self.settings_.setValue("FFmpegPath", self.ffmpeg_)
        self.settings_.setValue("LastDir", self.last_dir())
        self.settings_.endGroup()
        self.settings_.beginGroup("Geometry")
        self.settings_.setValue("MainWindowGeometry", self.main_wnd_geometry())
        self.settings_.endGroup()
        self.settings_.beginGroup("Video presets")
        # remove any existing entries
        self.settings_.remove("")
        # and fill it with actual values
        for preset in self.video_presets:
            self.settings_.setValue(preset.name, preset)
        self.settings_.endGroup()
        self.settings_.sync()

    def ffmpeg(self):
        """Get FFmpeg path"""
        return self.ffmpeg_

    def set_ffmpeg(self, path):
        """Set FFmpeg path"""
        if type(path) is str:
            self.ffmpeg_ = path

    def set_last_dir(self, directory):
        """Set last used directory for opening a video"""
        if type(directory) is str:
            self.lastdir_ = directory

    def last_dir(self):
        """Get last used directory for opening a video"""
        return self.lastdir_

    def set_main_wnd_geometry(self, geometry):
        """Save main window's position and size"""
        if type(geometry) is QRect:
            self.main_wnd_geometry_ = geometry

    def main_wnd_geometry(self):
        """Get main window's position and size"""
        return self.main_wnd_geometry_


class SettingsDialog(QDialog):
    """SettingsDialog class shows a dialog where user can set various settings for the app."""
    def __init__(self, settings):
        QDialog.__init__(self)
        self.init_ui("PyVideoEditor/Settings.ui")
        self.settings_ = settings
        self.Form.btnOk.clicked.connect(self.accept_settings)
        self.Form.btnFFmpegPath.clicked.connect(self.browse_for_ffmpeg_exec)
        self.Form.presetsTable.horizontalHeader().setStretchLastSection(True)
        self.Form.btnAddPreset.clicked.connect(self.presets_add)
        self.Form.btnRemovePreset.clicked.connect(self.presets_remove_current)
        self.load_settings_values()


    def init_ui(self, filename):
        """ Init UI from a given ui file. """
        loader = QUiLoader()
        file = QFile(filename)
        file.open(QIODevice.ReadOnly)
        self.Form = loader.load(file, self)
        file.close()

    def load_settings_values(self):
        """Get values from settings and show them in dialog"""
        self.Form.txtFFmpegPath.setText(self.settings_.ffmpeg())
        
        #self.Form.presetsTable.cellChanged.disconnect()
        presets = self.settings_.video_presets
        if len(presets) > 0:
            self.Form.presetsTable.setRowCount(len(presets))
            i = 0
            for video_preset in presets:
                if type(video_preset) is VideoPreset:
                    self.Form.presetsTable.setItem(i, 0, QTableWidgetItem(video_preset.name))
                    self.Form.presetsTable.setItem(i, 1, QTableWidgetItem(video_preset.extension))
                    self.Form.presetsTable.setItem(i, 2, QTableWidgetItem(video_preset.command_line))
                i += 1
            self.Form.presetsTable.cellChanged.connect(self.presets_cell_changed)

    @Slot()
    def accept_settings(self):
        """Save all values to settings and close the dialog"""
        self.settings_.set_ffmpeg(self.Form.txtFFmpegPath.text())
        self.accept()

    @Slot()
    def browse_for_ffmpeg_exec(self):
        """Dialog for pointing to the ffmpeg executable"""
        filename = QFileDialog.getOpenFileName(self, "Find FFmpeg executable", QFileInfo(self.Form.txtFFmpegPath.text()).absolutePath(), "Executables (*.exe)")
        if filename[0] != "":
            self.Form.txtFFmpegPath.setText(filename[0])
            self.settings_.set_ffmpeg(filename[0])

    @Slot()
    def presets_add(self):
        """Add new empty pvideo preset."""
        self.Form.presetsTable.insertRow(self.Form.presetsTable.rowCount())
        self.settings_.video_presets.append(VideoPreset())

    @Slot()
    def presets_remove_current(self):
        """Removes current preset."""
        which = self.Form.presetsTable.currentRow()
        if which > -1:
            del self.settings_.video_presets[which]
            self.Form.presetsTable.removeRow(which)

    @Slot()
    def presets_cell_changed(self, row, column):
        """User changed entry in a presets table."""
        if column == 0:
            self.settings_.video_presets[row].name = self.Form.presetsTable.item(row, column).text()
        elif column == 1:
            self.settings_.video_presets[row].extension = self.Form.presetsTable.item(row, column).text()
        elif column == 2:
            self.settings_.video_presets[row].command_line = self.Form.presetsTable.item(row, column).text()
        
