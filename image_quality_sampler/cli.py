import sys

from PyQt5.QtWidgets import QApplication

from image_quality_sampler.GUI import ImageSamplerApp


def main():  # pragma: no cover
    app = QApplication(sys.argv)
    ex = ImageSamplerApp()
    ex.show()
    sys.exit(app.exec_())
