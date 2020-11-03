__version__ = "0.1.0"

import sys
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QCoreApplication, Qt
from PySide2.QtGui import QIcon
from PyVideoEditor.video_editor import VideoEditorMainWindow

if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('app.ico'))

    mainWnd = VideoEditorMainWindow()
    mainWnd.show()

    sys.exit(app.exec_())
