#!/usr/bin/env python3
"""
TabX Browser — Minimal QtWebEngine Tarayıcı (F1 MVP)
"""

import sys
import os

os.environ['QT_WEBENGINE_CHROMIUM_FLAGS'] = '--enable-features=NetworkService'

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

from core.browser_window import BrowserWindow


def main():
    os.environ['QT_WEBENGINE_CHROMIUM_FLAGS'] = '--enable-features=NetworkService'
    app = QApplication(sys.argv)
    app.setApplicationName("TabX Browser")

    window = BrowserWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
