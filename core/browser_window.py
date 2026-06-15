#!/usr/bin/env python3
"""
TabX Browser — Modern Glassmorphic Chrome UI (Stable Version)
"""

import sys
import os
os.environ['QT_WEBENGINE_CHROMIUM_FLAGS'] = '--enable-features=NetworkService'

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QFrame,
    QPushButton,
    QLabel,
    QStackedWidget,
)
from PyQt6.QtCore import QUrl, pyqtSignal, Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView


class BrowserTab(QWebEngineView):
    """Tek sekme için web view."""


class TabButton(QFrame):
    """Modern sekme butonu."""
    
    clicked = pyqtSignal()
    closed = pyqtSignal()

    def __init__(self, title="Tab", active=False, closable=True, parent=None):
        super().__init__(parent)
        self._title = title
        self._active = active
        self._closable = closable
        
        self.setFixedHeight(32)
        self.setMinimumWidth(150)
        self.setMaximumWidth(230)
        
        self.setup_ui()
        self.apply_style()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 8, 0)
        layout.setSpacing(7)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(8, 8)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.title_label = QLabel(self._title)
        self.title_label.setStyleSheet("color: #111827; font-size: 13px; font-weight: 600;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.title_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label, 1)

        # Close button (only if closable)
        if self._closable:
            self.close_btn = QPushButton("×")
            self.close_btn.setFixedSize(18, 18)
            self.close_btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    border-radius: 9px;
                    background: transparent;
                    color: #6b7c8d;
                    font-size: 15px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background-color: rgba(0,0,0,0.08);
                    color: #1a2b3c;
                }
            """)
            self.close_btn.clicked.connect(self.closed.emit)
            layout.addWidget(self.close_btn)

        # Click handler
        self.mousePressEvent = self._handle_mouse_press

    def _handle_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def apply_style(self):
        """Glassmorphic stillendirme."""
        bg_color = "#eef3f9" if not self._active else "#ffffff"
        border_top = "1px solid #d7e0ea"
        border_color = "#d7e0ea" if not self._active else "#ffffff"
        hover_bg = "#f8fafc" if not self._active else "#ffffff"
        dot_color = "#2683ff" if self._active else "#94a3b8"
        self.icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: {dot_color};
                border-radius: 4px;
            }}
        """)
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 9px;
                border-top: {border_top};
                border-left: 1px solid {border_color};
                border-right: 1px solid {border_color};
                border-bottom: 1px solid #ffffff;
            }}
            QFrame:hover {{
                background-color: {hover_bg};
            }}
        """)

    def setTitle(self, text):
        self._title = text
        self.title_label.setText(text)
        self.setMaximumWidth(260 if len(text) > 20 else 230)

    def setActive(self, active):
        self._active = active
        self.apply_style()


class TabWidget(QWidget):
    """Modern sekme yönetim widget'ı."""

    tabClosed = pyqtSignal(int)
    tabActivated = pyqtSignal(int)
    newTabRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tabs = []
        self._active_index = 0
        self._views = []
        
        self.layout = QHBoxLayout(self)
        self.setObjectName("tabStrip")
        self.layout.setContentsMargins(16, 8, 16, 0)
        self.layout.setSpacing(5)
        self.setFixedHeight(42)
        self.setStyleSheet("""
            QWidget#tabStrip {
                background-color: #e5e9ef;
            }
        """)

    def add_tab(self, url=None, title="Yeni Sekme", icon_data=None):
        """Yeni sekme ekle."""
        tab_info = {
            'url': url or QUrl("about:blank"),
            'title': title,
            'icon': icon_data
        }
        self._tabs.append(tab_info)
        index = len(self._tabs) - 1
        self._render_tabs()
        self.setCurrentIndex(index)
        return index

    def remove_tab(self, index):
        """Sekme kapat."""
        if 0 <= index < len(self._tabs):
            self._tabs.pop(index)
            if index < len(self._views):
                self._views.pop(index)
            self._render_tabs()
            new_index = min(index, max(0, len(self._tabs) - 1))
            self.setCurrentIndex(new_index)

    def setTabText(self, index, text):
        """Sekme başlığını güncelle."""
        if 0 <= index < len(self._tabs):
            self._tabs[index]['title'] = text
            self._render_tabs()

    def setCurrentIndex(self, index):
        """Aktif sekme belirle."""
        if 0 <= index < len(self._tabs):
            self._active_index = index
            self.tabActivated.emit(index)
            self._render_tabs()

    def currentIndex(self):
        """Aktif sekme indeksini döndür."""
        return self._active_index

    def count(self):
        """Sekme sayısı."""
        return len(self._tabs)

    def widget(self, index):
        """Sekmeye karşılık gelen web view."""
        if 0 <= index < len(self._views):
            return self._views[index]
        return None

    def _render_tabs(self):
        """Tüm sekmeleri yeniden oluştur."""
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for i, tab_info in enumerate(self._tabs):
            is_active = (i == self._active_index)
            tab_button = TabButton(
                title=tab_info['title'],
                active=is_active,
                closable=True
            )
            if i < len(self._views):
                tab_button._view = self._views[i]
            
            tab_button.clicked.connect(lambda idx=i: self.setCurrentIndex(idx))
            tab_button.closed.connect(lambda idx=i: self.tabClosed.emit(idx))
            self.layout.addWidget(tab_button)

        add_btn = QPushButton("+")
        add_btn.setFixedSize(30, 30)
        add_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 9px;
                background-color: #f8fafc;
                font-size: 17px;
                font-weight: bold;
                color: #2683ff;
            }
            QPushButton:hover {
                background-color: #dcecff;
            }
        """)
        add_btn.clicked.connect(self.newTabRequested.emit)
        self.layout.addWidget(add_btn)
        self.layout.addStretch(1)

    def updateViewReference(self, index, view):
        """Web view referansını güncelle."""
        while len(self._views) <= index:
            self._views.append(None)
        self._views[index] = view
        self._render_tabs()


class BrowserWindow(QMainWindow):
    """Ana tarayıcı penceresi."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TabX Browser")
        self.setGeometry(100, 100, 1400, 900)
        
        central = QWidget()
        central.setObjectName("root")
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        central.setStyleSheet("""
            QWidget#root {
                background-color: #f5f7fb;
            }
        """)

        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Tab strip
        self.tabs = TabWidget(self)
        self.tabs.tabClosed.connect(self.close_tab)
        self.tabs.tabActivated.connect(self.handle_tab_activated)
        self.tabs.newTabRequested.connect(self.add_new_tab)
        
        layout.addWidget(self.tabs)

        # Web view container
        self.web_container = QStackedWidget()
        self.current_view = None
        
        layout.addWidget(self.web_container, 1)

        # Default tab
        self.add_new_tab(QUrl("about:blank"), "Yeni Sekme")
        
        self.setCentralWidget(central)

    def _create_toolbar(self):
        """Navigation toolbar."""
        container = QFrame()
        container.setObjectName("toolbar")
        container.setFixedHeight(74)
        container.setStyleSheet("""
            QFrame#toolbar {
                background-color: #e5e9ef;
                border-bottom: 1px solid #d5dbe5;
            }
        """)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(24, 14, 24, 14)
        layout.setSpacing(12)

        nav_frame = QFrame()
        nav_frame.setObjectName("navControls")
        nav_frame.setStyleSheet("""
            QFrame#navControls {
                background-color: #f8fafc;
                border-radius: 16px;
            }
        """)
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(8, 6, 8, 6)
        nav_layout.setSpacing(6)

        for icon, callback in [
            ("←", self.go_back),
            ("→", self.go_forward),
            ("↻", self.reload_page),
        ]:
            btn = QPushButton(icon)
            btn.setFixedWidth(34)
            btn.setFixedHeight(34)
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    border-radius: 10px;
                    background-color: #eef2f7;
                    color: #475569;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #e2e8f0;
                }
            """)
            btn.clicked.connect(callback)
            nav_layout.addWidget(btn)

        layout.addWidget(nav_frame)

        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Adres girin veya arayın...")
        self.address_bar.setFixedHeight(38)
        self.address_bar.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d8dee8;
                border-radius: 16px;
                background-color: #ffffff;
                padding: 0 14px;
                font-size: 14px;
                color: #1a2b3c;
            }
        """)
        self.address_bar.returnPressed.connect(self.navigate_to_url)
        
        layout.addWidget(self.address_bar, 1)

        icons_frame = QFrame()
        icons_frame.setObjectName("actionControls")
        icons_frame.setStyleSheet("""
            QFrame#actionControls {
                background-color: #f8fafc;
                border-radius: 16px;
            }
        """)
        icons_layout = QHBoxLayout(icons_frame)
        icons_layout.setContentsMargins(8, 6, 8, 6)
        icons_layout.setSpacing(6)

        for icon, tooltip in [
            ("⭐", "Yer İmi"),
            ("⚙️", "Uzantılar"),
            ("👤", "Profil"),
            ("⋯", "Menü"),
        ]:
            btn = QPushButton(icon)
            btn.setFixedWidth(32)
            btn.setFixedHeight(32)
            btn.setToolTip(tooltip)
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    border-radius: 10px;
                    background-color: transparent;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #e2e8f0;
                }
            """)
            icons_layout.addWidget(btn)

        layout.addWidget(icons_frame)

        return container

    def add_new_tab(self, url=None, title="Yeni Sekme"):
        """Yeni sekme ekle."""
        if url is None:
            url = QUrl("about:blank")

        new_view = BrowserTab(self)
        new_view.setUrl(url)
        new_view.urlChanged.connect(lambda changed_url, view=new_view: self._handle_url_changed(view, changed_url))
        new_view.titleChanged.connect(lambda text, view=new_view: self._handle_title_changed(view, text))

        index = self.tabs.add_tab(url, title)
        self.tabs.updateViewReference(index, new_view)

        self.web_container.addWidget(new_view)
        self.current_view = new_view
        self.web_container.setCurrentWidget(new_view)
        self.tabs.setCurrentIndex(index)

        return index

    def close_tab(self, index):
        """Sekme kapat."""
        if self.tabs.count() > 1:
            if index < len(self.tabs._views):
                view = self.tabs._views[index]
                self.web_container.removeWidget(view)
                view.deleteLater()
            
            self.tabs.remove_tab(index)
            
            new_index = min(index, max(0, self.tabs.count() - 1))
            if new_index < len(self.tabs._views):
                self.current_view = self.tabs._views[new_index]
                self.web_container.setCurrentWidget(self.current_view)
                self.update_address_bar(self.current_view.url())

    def handle_tab_activated(self, index):
        """Sekme değiştirildiğinde."""
        if hasattr(self.tabs, '_views') and index < len(self.tabs._views):
            self.current_view = self.tabs._views[index]
            if self.current_view:
                self.web_container.setCurrentWidget(self.current_view)
                self.update_address_bar(self.current_view.url())

    def navigate_to_url(self):
        """Adresteki URL'e git."""
        text = self.address_bar.text().strip()
        if not text:
            return
        url = QUrl.fromUserInput(text)
        if self.current_view:
            self.current_view.setUrl(url)

    def update_address_bar(self, url):
        """Adres çubuğunu güncelle."""
        self.address_bar.setText(url.toString())

    def _handle_url_changed(self, view, url):
        """Yalnızca aktif sekme için adres çubuğunu güncelle."""
        if view is self.current_view:
            self.update_address_bar(url)

    def _handle_title_changed(self, view, title):
        """Sayfa başlığını ilgili sekmeye yaz."""
        try:
            index = self.tabs._views.index(view)
        except ValueError:
            return

        clean_title = title.strip() or "Yeni Sekme"
        self.tabs.setTabText(index, clean_title)

    def go_back(self):
        if self.current_view and hasattr(self.current_view, "back"):
            self.current_view.back()

    def go_forward(self):
        if self.current_view and hasattr(self.current_view, "forward"):
            self.current_view.forward()

    def reload_page(self):
        if self.current_view and hasattr(self.current_view, "reload"):
            self.current_view.reload()


def main():
    os.environ['QT_WEBENGINE_CHROMIUM_FLAGS'] = '--enable-features=NetworkService'
    app = QApplication(sys.argv)
    app.setApplicationName("TabX Browser")

    window = BrowserWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
