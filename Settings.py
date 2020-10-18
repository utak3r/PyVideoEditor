from PySide2.QtCore import QSettings, QSize, QPoint, QRect

class Settings():
    def __init__(self, org, appName):
        self.settings_ = QSettings(org, appName)
        self.organization_ = org
        self.appName_ = appName

        # settings
        self.lastdir_ = "."
        self.mainWndGeometry_ = QRect(640, 250, 800, 500)

    def readSettings(self):
        self.settings_.beginGroup("General")
        self.setLastDir(self.settings_.value("LastDir", "."))
        self.settings_.endGroup()
        self.settings_.beginGroup("Geometry")
        self.setMainWndGeometry(self.settings_.value("MainWindowGeometry"))
        self.settings_.endGroup()

    def writeSettings(self):
        self.settings_.beginGroup("General")
        self.settings_.setValue("LastDir", self.getLastDir())
        self.settings_.endGroup()
        self.settings_.beginGroup("Geometry")
        self.settings_.setValue("MainWindowGeometry", self.getMainWndGeometry())
        self.settings_.endGroup()
        self.settings_.sync()

    def setLastDir(self, dir):
        self.lastdir_ = dir

    def getLastDir(self):
        return self.lastdir_

    def setMainWndGeometry(self, geometry):
        self.mainWndGeometry_ = geometry
    
    def getMainWndGeometry(self):
        return self.mainWndGeometry_

