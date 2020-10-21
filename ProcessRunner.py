import asyncio
from PySide2.QtWidgets import QDialog
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QCoreApplication, Slot, QFile, QIODevice

class ProcessRunner(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.init_ui("ProcessRunner.ui")

        self.process = None
        self.Form.btnOk.clicked.connect(self.accept)
        self.Form.btnCancel.clicked.connect(self.terminate)

    def init_ui(self, filename):
        loader = QUiLoader()
        file = QFile(filename)
        file.open(QIODevice.ReadOnly)
        self.Form = loader.load(file, self)
        file.close()

    def run_command(self, command):
        self.show()
        self.add_log(command)
        QCoreApplication.processEvents()
        asyncio.run(self.run(command))

    async def read_stream(self, stream):
        while self.process.returncode is None:
            try:
                line = await stream.readline()
            except (asyncio.LimitOverrunError, ValueError):
                continue
            if line:
                line = line.decode("utf-8")[:-1]
                print(line)
                self.add_log(line)
                QCoreApplication.processEvents()
            else:
                break

    async def run(self, command):
        self.Form.btnOk.setEnabled(False)
        try:
            self.process = await asyncio.create_subprocess_shell(command, stdin=asyncio.subprocess.DEVNULL, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            self.Form.btnCancel.setEnabled(True)
            await asyncio.wait([self.read_stream(self.process.stdout), self.read_stream(self.process.stderr)])
        finally:
            self.Form.btnCancel.setEnabled(False)
            self.Form.btnOk.setEnabled(True)


    @Slot()
    def terminate(self):
        if self.process is not None:
            self.process.terminate()
        self.reject()

    @Slot()
    def add_log(self, text):
        self.Form.logText.appendPlainText(text)
