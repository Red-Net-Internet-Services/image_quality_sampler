from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from image_quality_sampler import config
from image_quality_sampler.GUI.views.central_view import CentralView


def main():  # pragma: no cover
    app = QApplication([])
    window = CentralView()

    stylesheet = open(config.CSS_PATH, "r").read()
    app.setStyleSheet(stylesheet)

    # Ensure the window comes to the foreground
    window.setWindowFlags(window.windowFlags() | Qt.WindowStaysOnTopHint)
    window.showMaximized()  # Show the window maximized
    window.setWindowFlags(window.windowFlags() & ~Qt.WindowStaysOnTopHint)
    window.show()

    app.exec_()
