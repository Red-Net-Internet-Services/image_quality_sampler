import sys

from PyQt5.QtWidgets import QApplication

from image_quality_sampler.GUI import ImageSamplerApp


def main():  # pragma: no cover
    # print("This will do something")
    app = QApplication(sys.argv)
    ex = ImageSamplerApp()
    sys.exit(app.exec_())
