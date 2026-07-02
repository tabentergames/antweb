"""
TabX F3 — PrivacyService.

Single entry-point for all F3 privacy infrastructure.  BrowserWindow creates
one instance and calls attach_tab() for every new tab so the HTTPS fallback
signal is wired automatically.

Usage in BrowserWindow.__init__:
    self.privacy = PrivacyService(QWebEngineProfile.defaultProfile())

Usage in BrowserWindow.add_new_tab:
    self.privacy.attach_tab(new_view)
"""

from __future__ import annotations

from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo
from PyQt6.QtWebEngineWidgets import QWebEngineView

from features.privacy.ad_blocker import AdBlockInterceptor
from features.privacy.https_upgrade import HttpsUpgradeInterceptor
from features.extensions.runtime import ExtensionRuntime


class _ChainedInterceptor(QWebEngineUrlRequestInterceptor):
    """Runs ad-blocker then HTTPS upgrade through a single profile slot."""

    def __init__(self, ad_blocker: AdBlockInterceptor, https: HttpsUpgradeInterceptor) -> None:
        super().__init__()
        self._ad = ad_blocker
        self._https = https

    def interceptRequest(self, info: QWebEngineUrlRequestInfo) -> None:  # noqa: N802
        self._ad.interceptRequest(info)
        self._https.interceptRequest(info)


class PrivacyService:
    """Owns all F3 privacy objects and wires them to a QWebEngineProfile."""

    def __init__(self, profile: QWebEngineProfile) -> None:
        self.ad_blocker = AdBlockInterceptor()
        self.https_interceptor = HttpsUpgradeInterceptor()
        self.extension_runtime = ExtensionRuntime(profile=profile)

        self._interceptor = _ChainedInterceptor(self.ad_blocker, self.https_interceptor)
        profile.setUrlRequestInterceptor(self._interceptor)

        self.extension_runtime.load_all()

    def attach_tab(self, view: QWebEngineView) -> None:
        """Connect a new tab's loadFinished signal to the HTTPS fallback handler."""
        view.loadFinished.connect(lambda ok, v=view: self._on_load_finished(ok, v))

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _on_load_finished(self, ok: bool, view: QWebEngineView) -> None:
        fallback_url: QUrl | None = self.https_interceptor.on_load_finished(ok, view.url())
        if fallback_url is not None:
            view.setUrl(fallback_url)
