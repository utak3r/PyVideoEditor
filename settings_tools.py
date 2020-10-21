from PySide2.QtCore import QSettings, QRect

class Settings():
    def __init__(self, org, appName):
        self.settings_ = QSettings(org, appName)
        self.organization_ = org
        self.app_name_ = appName

        # settings
        self.ffmpeg_ = "ffmpeg.exe"
        self.lastdir_ = "."
        self.main_wnd_geometry_ = QRect(640, 250, 800, 500)

    def read_settings(self):
        self.settings_.beginGroup("General")
        self.set_ffmpeg(self.settings_.value("FFmpegPath", "ffmpeg.exe"))
        self.set_last_dir(self.settings_.value("LastDir", "."))
        self.settings_.endGroup()
        self.settings_.beginGroup("Geometry")
        self.set_main_wnd_geometry(self.settings_.value("MainWindowGeometry"))
        self.settings_.endGroup()

    def write_settings(self):
        self.settings_.beginGroup("General")
        self.settings_.setValue("FFmpegPath", self.ffmpeg_)
        self.settings_.setValue("LastDir", self.last_dir())
        self.settings_.endGroup()
        self.settings_.beginGroup("Geometry")
        self.settings_.setValue("MainWindowGeometry", self.main_wnd_geometry())
        self.settings_.endGroup()
        self.settings_.sync()

    def ffmpeg(self):
        return self.ffmpeg_

    def set_ffmpeg(self, path):
        self.ffmpeg_ = path

    def set_last_dir(self, directory):
        self.lastdir_ = directory

    def last_dir(self):
        return self.lastdir_

    def set_main_wnd_geometry(self, geometry):
        self.main_wnd_geometry_ = geometry
    
    def main_wnd_geometry(self):
        return self.main_wnd_geometry_

