import os.path
import sys

from PySide6.QtGui import *
from PySide6.QtCore import QSysInfo
from PySide6.QtWidgets import *

from ciliaseg.app import MainApplication


version = 'v2023.11.21'

def launch():
    app = QApplication(sys.argv)
    app.setApplicationName('ciliaseg')
    app.setApplicationDisplayName('ciliaseg')
    app.setApplicationVersion(version)
    app.setOrganizationName('Indzyhkulian Lab')

    font_weight = 12 if QSysInfo.productType() == 'macos' else 8

    font = QFont('Office Code Pro', font_weight)
    # app.setFont(font, "QWidget")
    app.setFont(font)

    imageViewer = MainApplication()

    geometry = app.primaryScreen().geometry()
    w, h = geometry.width(), geometry.height()
    x = (w - imageViewer.width())/2
    y = (h - imageViewer.height())/2
    imageViewer.move(x, y)
    imageViewer.setWindowTitle(f'ciliaseg-{version}')
    imageViewer.show()


    sys.exit(app.exec())



if __name__ == '__main__':
    launch()