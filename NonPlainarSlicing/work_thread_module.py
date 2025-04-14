import pyvista as pv
from PyQt5.QtCore import QMetaObject, Qt, QObject, pyqtSlot, pyqtSignal, QThread
from time import sleep

from .globals import Glob





class WorkerThread(QThread):
    progress_signal1 = pyqtSignal(int)  # First progress bar signal
    progress_signal2 = pyqtSignal(int)  # Second progress bar signal

    def run(self):
        while not self.isInterruptionRequested():  # Thread-safe exit condition
            p1 = Glob.get_progress() * 100
            p2 = Glob.get_progress2() * 100
            self.progress_signal1.emit(int(p1))  # Emit progress for first bar
            self.progress_signal2.emit(int(p2))  # Emit progress for second bar
            sleep(0.01)  # Prevent CPU overus