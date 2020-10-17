from PySide2.QtCore import QSettings

class Settings():
    def __init__(self, org, appName):
        self.settings_ = QSettings(org, appName)
        self.organization_ = org
        self.appName_ = appName

        # settings
        self.lastdir_ = "."

    def readSettings(self):
        self.settings_.beginGroup("General")
        self.setLastDir(self.settings_.value("LastDir", "."))
        self.settings_.endGroup()

    def writeSettings(self):
        self.settings_.beginGroup("General")
        self.settings_.setValue("LastDir", self.getLastDir())
        self.settings_.endGroup()
        self.settings_.sync()

    def setLastDir(self, dir):
        self.lastdir_ = dir

    def getLastDir(self):
        return self.lastdir_
