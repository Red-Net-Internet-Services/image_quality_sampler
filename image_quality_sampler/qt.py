import atexit
import logging
from multiprocessing import Process

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from image_quality_sampler import config
from image_quality_sampler.db.database_manager import DatabaseManager
from image_quality_sampler.GUI.views.central_view import CentralView
from image_quality_sampler.watcher import Watcher


def start_watcher():
    watcher = Watcher()
    watcher_process = Process(target=watcher.run)
    watcher_process.start()
    return watcher_process


def main():  # pragma: no cover
    logging.info("Watcher process started")
    watcher_process = start_watcher()
    # Register the cleanup function
    atexit.register(watcher_process.terminate)

    db = DatabaseManager()

    app = QApplication([])
    window = CentralView(db)

    stylesheet = open(config.CSS_PATH, "r").read()
    app.setStyleSheet(stylesheet)

    # Ensure the window comes to the foreground
    window.setWindowFlags(window.windowFlags() | Qt.WindowStaysOnTopHint)
    window.showMaximized()  # Show the window maximized
    window.setWindowFlags(window.windowFlags() & ~Qt.WindowStaysOnTopHint)
    window.show()

    app.exec()
    # watcher_process.join()
    logging.info("Watcher process joined")
