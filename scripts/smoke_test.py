"""GUI'siz smoke test — agent'lar teslimden once bunu calistirir.

Kullanim:
    python3 scripts/smoke_test.py

Pencereyi ekranda acmadan (offscreen) uygulamayi kurar, panelleri ve
temayi degistirir, hata almadan kapatabiliyorsa PASS der. GUI'nin
gorsel dogrulugunu KANITLAMAZ; sadece "acilir ve patlamaz" garantisidir.
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from core.browser_window import BrowserWindow
from ui.motion import Motion


def run() -> int:
    app = QApplication(sys.argv)
    # Animasyonlari kapat ki toggle'lar deterministik calissin.
    Motion.configure(False)

    window = BrowserWindow()
    window.show()

    window.toggle_left_sidebar(True)
    window.toggle_right_sidebar(True)
    assert window.left_sidebar.isVisible(), "sol panel acilmadi"
    assert window.right_sidebar.isVisible(), "sag panel acilmadi"

    window.toggle_left_sidebar(False)
    window.toggle_right_sidebar(False)
    assert not window.left_sidebar.isVisible(), "sol panel kapanmadi"
    assert not window.right_sidebar.isVisible(), "sag panel kapanmadi"

    window.toggle_theme_mode()
    window.toggle_theme_mode()

    QTimer.singleShot(500, app.quit)
    app.exec()
    print("SMOKE TEST PASS")
    return 0


if __name__ == "__main__":
    sys.exit(run())
