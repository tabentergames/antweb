"""F6 snippet library window and active-page runner."""

from __future__ import annotations

import json

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.theme import Theme

from .snippet_store import SnippetStore


class SnippetInputDialog(QDialog):
    """Yeni JS/CSS snippet'i icin token tabanli modal."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Yeni snippet")
        self.setModal(True)
        self.setFixedWidth(560)
        self.setStyleSheet(self._style())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Theme.SPACE_XL, Theme.SPACE_XL, Theme.SPACE_XL, Theme.SPACE_LG
        )
        layout.setSpacing(Theme.SPACE_MD)

        title = QLabel("Yeni snippet")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Snippet adı")
        layout.addWidget(self.name_input)

        self.language_input = QComboBox()
        self.language_input.addItem("JavaScript", "javascript")
        self.language_input.addItem("CSS", "css")
        layout.addWidget(self.language_input)

        self.code_input = QPlainTextEdit()
        self.code_input.setPlaceholderText("Çalıştırılacak kod")
        self.code_input.setMinimumHeight(240)
        layout.addWidget(self.code_input)

        actions = QHBoxLayout()
        actions.addStretch(1)
        cancel = QPushButton("Vazgeç")
        cancel.setObjectName("secondaryButton")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Kaydet")
        save.setObjectName("primaryButton")
        save.clicked.connect(self._accept_if_valid)
        actions.addWidget(cancel)
        actions.addWidget(save)
        layout.addLayout(actions)

    def _accept_if_valid(self) -> None:
        if self.name_input.text().strip() and self.code_input.toPlainText().strip():
            self.accept()

    @classmethod
    def get_snippet(
        cls, parent: QWidget | None = None
    ) -> tuple[str, str, str, bool]:
        dialog = cls(parent)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return "", "", "", False
        return (
            dialog.name_input.text().strip(),
            str(dialog.language_input.currentData()),
            dialog.code_input.toPlainText().strip(),
            True,
        )

    @staticmethod
    def _style() -> str:
        return f"""
            QDialog {{
                background-color: {Theme.glass_strong};
                border: 1px solid {Theme.glass_border};
                border-radius: {Theme.RADIUS_LG}px;
            }}
            QLabel#dialogTitle {{
                color: {Theme.text};
                font-size: 18px;
                font-weight: 800;
            }}
            QLineEdit, QComboBox, QPlainTextEdit {{
                border: 1px solid {Theme.border};
                border-radius: {Theme.RADIUS_MD}px;
                background-color: {Theme.input};
                color: {Theme.text};
                padding: {Theme.SPACE_MD}px;
                font-size: 13px;
            }}
            QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus {{
                border-color: {Theme.purple};
            }}
            QPushButton {{
                min-width: 84px;
                min-height: 34px;
                border-radius: {Theme.RADIUS_MD}px;
                padding: 0 {Theme.SPACE_LG}px;
                font-size: 12px;
                font-weight: 800;
            }}
            QPushButton#primaryButton {{
                border: 1px solid {Theme.purple};
                background-color: {Theme.purple};
                color: {Theme.card};
            }}
            QPushButton#secondaryButton {{
                border: 1px solid {Theme.border};
                background-color: {Theme.panel_alt};
                color: {Theme.muted};
            }}
        """


class SnippetLibraryWindow(QMainWindow):
    """Profil snippet'lerini yoneten ayrik ve tasinabilir kutuphane penceresi."""

    runRequested = pyqtSignal(int)
    closed = pyqtSignal()

    def __init__(
        self, store: SnippetStore, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.store = store
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setWindowTitle("TabX Snippet Kütüphanesi")
        self.resize(920, 620)

        root = QFrame()
        root.setObjectName("snippetRoot")
        root.setStyleSheet(self._style())
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(
            Theme.SPACE_XL, Theme.SPACE_XL, Theme.SPACE_XL, Theme.SPACE_XL
        )
        layout.setSpacing(Theme.SPACE_LG)

        header = QHBoxLayout()
        heading = QLabel("Snippet Kütüphanesi")
        heading.setObjectName("heading")
        header.addWidget(heading)
        header.addStretch(1)
        add = QPushButton("+ Yeni")
        add.setObjectName("secondaryButton")
        add.clicked.connect(self._add_snippet)
        run = QPushButton("▶ Çalıştır")
        run.setObjectName("primaryButton")
        run.clicked.connect(self._run_selected)
        remove = QPushButton("Sil")
        remove.setObjectName("dangerButton")
        remove.clicked.connect(self._remove_selected)
        header.addWidget(add)
        header.addWidget(run)
        header.addWidget(remove)
        layout.addLayout(header)

        content = QHBoxLayout()
        content.setSpacing(Theme.SPACE_LG)
        self.list = QListWidget()
        self.list.setObjectName("snippetList")
        self.list.currentItemChanged.connect(self._show_selected)
        content.addWidget(self.list, 2)

        preview_host = QFrame()
        preview_host.setObjectName("previewHost")
        preview_layout = QVBoxLayout(preview_host)
        preview_layout.setContentsMargins(
            Theme.SPACE_LG, Theme.SPACE_LG, Theme.SPACE_LG, Theme.SPACE_LG
        )
        preview_layout.setSpacing(Theme.SPACE_SM)
        self.meta = QLabel("Bir snippet seç")
        self.meta.setObjectName("meta")
        preview_layout.addWidget(self.meta)
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("Snippet kodu burada görünür")
        preview_layout.addWidget(self.preview, 1)
        content.addWidget(preview_host, 3)
        layout.addLayout(content, 1)

        self.status = QLabel("Kod yalnızca açıkça Çalıştır dediğinde aktif sekmeye uygulanır.")
        self.status.setObjectName("status")
        layout.addWidget(self.status)
        self.refresh()

    def refresh(self, select_id: int | None = None) -> None:
        self.list.clear()
        selected_item = None
        for snippet in self.store.all():
            language = "JS" if snippet.language == "javascript" else "CSS"
            item = QListWidgetItem(f"{snippet.name}   ·   {language}")
            item.setData(Qt.ItemDataRole.UserRole, snippet.id)
            self.list.addItem(item)
            if snippet.id == select_id:
                selected_item = item
        if selected_item is not None:
            self.list.setCurrentItem(selected_item)
        elif self.list.count():
            self.list.setCurrentRow(0)
        else:
            self.meta.setText("Henüz snippet yok")
            self.preview.clear()

    def set_run_status(self, message: str, success: bool) -> None:
        color = Theme.purple if success else Theme.muted
        self.status.setText(message)
        self.status.setStyleSheet(f"color: {color};")

    def closeEvent(self, event) -> None:  # noqa: N802
        self.closed.emit()
        super().closeEvent(event)

    def _add_snippet(self) -> None:
        name, language, code, ok = SnippetInputDialog.get_snippet(self)
        if not ok:
            return
        snippet_id = self.store.add(name, language, code)
        self.refresh(snippet_id)

    def _selected_id(self) -> int | None:
        item = self.list.currentItem()
        if item is None:
            return None
        return int(item.data(Qt.ItemDataRole.UserRole))

    def _show_selected(self, current, _previous=None) -> None:
        if current is None:
            self.meta.setText("Bir snippet seç")
            self.preview.clear()
            return
        snippet = self.store.get(int(current.data(Qt.ItemDataRole.UserRole)))
        if snippet is None:
            return
        language = "JavaScript" if snippet.language == "javascript" else "CSS"
        self.meta.setText(f"{snippet.name}  ·  {language}")
        self.preview.setPlainText(snippet.code)

    def _run_selected(self) -> None:
        snippet_id = self._selected_id()
        if snippet_id is not None:
            self.runRequested.emit(snippet_id)

    def _remove_selected(self) -> None:
        snippet_id = self._selected_id()
        if snippet_id is None:
            return
        self.store.remove(snippet_id)
        self.refresh()

    @staticmethod
    def _style() -> str:
        return f"""
            QFrame#snippetRoot {{ background-color: {Theme.bg}; }}
            QLabel#heading {{
                color: {Theme.text};
                font-size: 20px;
                font-weight: 850;
            }}
            QListWidget#snippetList, QFrame#previewHost {{
                border: 1px solid {Theme.border};
                border-radius: {Theme.RADIUS_LG}px;
                background-color: {Theme.card};
            }}
            QListWidget#snippetList {{
                padding: {Theme.SPACE_SM}px;
                color: {Theme.text};
                font-size: 13px;
            }}
            QListWidget#snippetList::item {{
                border-radius: {Theme.RADIUS_MD}px;
                padding: {Theme.SPACE_MD}px;
            }}
            QListWidget#snippetList::item:selected {{
                background-color: {Theme.purple_soft};
                color: {Theme.purple};
            }}
            QLabel#meta {{
                color: {Theme.text};
                font-size: 13px;
                font-weight: 750;
            }}
            QPlainTextEdit {{
                border: 1px solid {Theme.border_soft};
                border-radius: {Theme.RADIUS_MD}px;
                background-color: {Theme.input};
                color: {Theme.text};
                padding: {Theme.SPACE_MD}px;
                font-family: Menlo, monospace;
                font-size: 12px;
            }}
            QLabel#status {{ color: {Theme.subtle}; font-size: 11px; }}
            QPushButton {{
                min-height: 34px;
                border-radius: {Theme.RADIUS_MD}px;
                padding: 0 {Theme.SPACE_LG}px;
                font-size: 12px;
                font-weight: 800;
            }}
            QPushButton#primaryButton {{
                border: 1px solid {Theme.purple};
                background-color: {Theme.purple};
                color: {Theme.card};
            }}
            QPushButton#secondaryButton {{
                border: 1px solid {Theme.border};
                background-color: {Theme.card};
                color: {Theme.muted};
            }}
            QPushButton#dangerButton {{
                border: 1px solid {Theme.border};
                background-color: transparent;
                color: {Theme.muted};
            }}
            QPushButton:hover {{ background-color: {Theme.purple_soft}; color: {Theme.purple}; }}
        """


class SnippetController(QObject):
    """Profil store'u, kutuphane penceresi ve aktif sayfa runner'i."""

    runRequested = pyqtSignal(int)

    def __init__(self, profile: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._host = parent
        self.store = SnippetStore(profile)
        self._window: SnippetLibraryWindow | None = None

    @property
    def window(self) -> SnippetLibraryWindow | None:
        return self._window

    def open(self) -> SnippetLibraryWindow:
        if self._window is None:
            window = SnippetLibraryWindow(self.store, self._host)
            window.runRequested.connect(self.runRequested.emit)
            window.closed.connect(lambda current=window: self._clear_window(current))
            self._window = window
        self._window.refresh()
        self._window.show()
        self._window.raise_()
        self._window.activateWindow()
        return self._window

    def execute(self, snippet_id: int, page: QWebEnginePage | None) -> bool:
        snippet = self.store.get(snippet_id)
        if snippet is None or page is None:
            self._set_status("Çalıştırılacak aktif sekme bulunamadı.", False)
            return False
        if snippet.language == "javascript":
            script = snippet.code
        else:
            marker = json.dumps(f"tabx-snippet-{snippet.id}")
            css = json.dumps(snippet.code)
            script = (
                "(() => {"
                f"const marker = {marker};"
                "let style = document.querySelector(`style[data-tabx-snippet=\"${marker}\"]`);"
                "if (!style) { style = document.createElement('style');"
                "style.dataset.tabxSnippet = marker; document.documentElement.appendChild(style); }"
                f"style.textContent = {css};"
                "})()"
            )
        page.runJavaScript(script)
        self._set_status(f"{snippet.name} aktif sekmede çalıştırıldı.", True)
        return True

    def close_window(self) -> None:
        window = self._window
        if window is None:
            return
        self._window = None
        window.close()

    def close(self) -> None:
        self.close_window()
        self.store.close()

    def _set_status(self, message: str, success: bool) -> None:
        if self._window is not None:
            self._window.set_run_status(message, success)

    def _clear_window(self, window: SnippetLibraryWindow) -> None:
        if self._window is window:
            self._window = None
