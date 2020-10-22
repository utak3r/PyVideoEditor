"""All the settings related stuff.
   Storing, restoring, accessing etc. any individual setting, or all of them at once.
   Provides also a dialog for editing some of the settings.
"""

from PySide2.QtCore import QSettings, QRect, QFile, QIODevice, Slot, QFileInfo
from PySide2.QtWidgets import QDialog, QFileDialog
from PySide2.QtUiTools import QUiLoader

class Settings():
    """This class holds all the settings for the app."""
    def __init__(self, org, appName):
        self.settings_ = QSettings(org, appName)
        self.organization_ = org
        self.app_name_ = appName

        # settings
        self.ffmpeg_ = "ffmpeg.exe"
        self.lastdir_ = "."
        self.main_wnd_geometry_ = QRect(640, 250, 800, 500)

    def read_settings(self):
        """Read settings from a storage and save them in internal variables for later use."""
        self.settings_.beginGroup("General")
        self.set_ffmpeg(self.settings_.value("FFmpegPath", "ffmpeg.exe"))
        self.set_last_dir(self.settings_.value("LastDir", "."))
        self.settings_.endGroup()
        self.settings_.beginGroup("Geometry")
        self.set_main_wnd_geometry(self.settings_.value("MainWindowGeometry"))
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
        self.settings_.sync()

    def ffmpeg(self):
        """Get FFmpeg path"""
        return self.ffmpeg_

    def set_ffmpeg(self, path):
        """Set FFmpeg path"""
        self.ffmpeg_ = path

    def set_last_dir(self, directory):
        """Set last used directory for opening a video"""
        self.lastdir_ = directory

    def last_dir(self):
        """Get last used directory for opening a video"""
        return self.lastdir_

    def set_main_wnd_geometry(self, geometry):
        """Save main window's position and size"""
        self.main_wnd_geometry_ = geometry

    def main_wnd_geometry(self):
        """Get main window's position and size"""
        return self.main_wnd_geometry_


class SettingsDialog(QDialog):
    """SettingsDialog class shows a dialog where user can set various settings for the app."""
    def __init__(self, settings):
        QDialog.__init__(self)
        self.init_ui("Settings.ui")
        self.settings_ = settings
        self.Form.btnOk.clicked.connect(self.accept_settings)
        self.Form.btnFFmpegPath.clicked.connect(self.browse_for_ffmpeg_exec)
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

