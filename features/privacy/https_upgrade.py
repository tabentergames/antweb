"""
TabX F3 — HTTPS upgrade interceptor with per-host fallback.

Upgrade flow:
  1. interceptRequest() sees an http:// main-frame navigation → redirect to https://.
     The original HTTP URL is stored in _pending[host].
  2. BrowserWindow calls on_load_finished(ok, url) after each page load:
     - ok=True  → upgrade succeeded; remove host from _pending.
     - ok=False → HTTPS failed; host is added to _fallback_hosts (permanent
                  session exception) and the caller receives the original HTTP
                  URL to retry with, so the user is not left on an error page.
  3. Any subsequent navigation to the same host skips the upgrade because it
     is now in _fallback_hosts.

Sub-resource requests (images, XHR, …) are not upgraded — only main-frame
navigations, so mixed-content handling is left to the browser engine.
"""

from __future__ import annotations

from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInfo, QWebEngineUrlRequestInterceptor

_HTTP_EXCEPTIONS: set[str] = {"localhost", "127.0.0.1", "::1"}

# ResourceType integer for the main document frame (PyQt6 enum value = 0)
_MAIN_FRAME = QWebEngineUrlRequestInfo.ResourceType.ResourceTypeMainFrame


class HttpsUpgradeInterceptor(QWebEngineUrlRequestInterceptor):
    """Upgrades http:// navigations to https:// with automatic per-host fallback."""

    def __init__(self) -> None:
        super().__init__()
        self._enabled = True
        self._upgrade_count = 0
        # host → original QUrl (http); cleared on successful load
        self._pending: dict[str, QUrl] = {}
        # hosts that failed HTTPS and must stay on HTTP for this session
        self._fallback_hosts: set[str] = set()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    @property
    def upgrade_count(self) -> int:
        return self._upgrade_count

    def on_load_finished(self, ok: bool, url: QUrl) -> QUrl | None:
        """Call from BrowserWindow.loadFinished.

        Returns the HTTP fallback QUrl if the load failed and an upgrade was
        responsible, otherwise returns None.
        """
        host = url.host().lower()
        if ok:
            self._pending.pop(host, None)
            return None

        original_http = self._pending.pop(host, None)
        if original_http is None:
            return None  # failure unrelated to our upgrade

        # Remember this host so we never try to upgrade it again
        self._fallback_hosts.add(host)
        return original_http

    # ------------------------------------------------------------------
    # QWebEngineUrlRequestInterceptor override
    # ------------------------------------------------------------------

    def interceptRequest(self, info: QWebEngineUrlRequestInfo) -> None:  # noqa: N802
        if not self._enabled:
            return
        # Only upgrade main-frame navigations
        if info.resourceType() != _MAIN_FRAME:
            return
        url = info.requestUrl()
        if url.scheme() != "http":
            return
        host = url.host().lower()
        if host in _HTTP_EXCEPTIONS or host in self._fallback_hosts:
            return

        upgraded = QUrl(url)
        upgraded.setScheme("https")
        self._pending[host] = QUrl(url)   # store original before redirect
        info.redirect(upgraded)
        self._upgrade_count += 1
