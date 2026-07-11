"""
TabX F3 — Ad & tracker blocker.

Uses QWebEngineUrlRequestInterceptor to block requests matching a domain
blocklist before they leave the browser. The blocklist is loaded once at
startup; future versions can hot-reload it without restarting.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInfo, QWebEngineUrlRequestInterceptor

# ---------------------------------------------------------------------------
# Default blocklist (common ad/tracker domains — minimal MVP set)
# ---------------------------------------------------------------------------

_BUILTIN_DOMAINS: list[str] = [
    # Google Ads / Analytics
    "doubleclick.net",
    "googleadservices.com",
    "googlesyndication.com",
    "google-analytics.com",
    "googletagmanager.com",
    "googletagservices.com",
    # Facebook / Meta
    # Note: the FB pixel fires to www.facebook.com/tr/ — blocking that host
    # would break the social site itself.  connect.facebook.net covers the
    # separately-loaded pixel SDK; that is sufficient for MVP.
    "connect.facebook.net",
    # Common tracker networks
    "scorecardresearch.com",
    "quantserve.com",
    "moatads.com",
    "criteo.com",
    "adnxs.com",
    "rubiconproject.com",
    "openx.net",
    "casalemedia.com",
    "serving-sys.com",
    "mathtag.com",
    "taboola.com",
    "outbrain.com",
    "zergnet.com",
    "revcontent.com",
    # Analytics / telemetry
    "hotjar.com",
    "mixpanel.com",
    "segment.io",
    "segment.com",
    "fullstory.com",
    "loggly.com",
    # General ad networks
    "ads.twitter.com",
    "advertising.com",
    "adform.net",
    "adtech.de",
    "intellicheck.com",
    "buysellads.com",
    "carbonads.com",
]


class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    """Blocks ad/tracker requests before they are dispatched."""

    def __init__(self, extra_domains: list[str] | None = None) -> None:
        super().__init__()
        self._blocked: set[str] = set(_BUILTIN_DOMAINS)
        if extra_domains:
            self._blocked.update(extra_domains)
        self._blocked_count = 0
        self._enabled = True

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_hosts_file(self, path: Path | str) -> int:
        """Parse a hosts-style blocklist file and add its domains.

        Returns the number of new domains added.
        """
        path = Path(path)
        if not path.exists():
            return 0
        added = 0
        with path.open(encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # hosts format: "0.0.0.0 tracker.example.com"
                parts = line.split()
                domain = parts[1] if len(parts) >= 2 else parts[0]
                if domain not in self._blocked:
                    self._blocked.add(domain)
                    added += 1
        return added

    @property
    def blocked_count(self) -> int:
        """Cumulative number of requests blocked since startup."""
        return self._blocked_count

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    def is_enabled(self) -> bool:
        return self._enabled

    # ------------------------------------------------------------------
    # QWebEngineUrlRequestInterceptor override
    # ------------------------------------------------------------------

    def interceptRequest(self, info: QWebEngineUrlRequestInfo) -> None:  # noqa: N802
        if not self.is_enabled():
            return
        url = info.requestUrl()
        host = url.host().lower()
        if self._should_block(host):
            info.block(True)
            self._blocked_count += 1

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _should_block(self, host: str) -> bool:
        # Exact match or subdomain match
        if host in self._blocked:
            return True
        # Walk up sub-domains: "ads.tracker.example.com" → "tracker.example.com" → …
        parts = host.split(".")
        for i in range(1, len(parts) - 1):
            candidate = ".".join(parts[i:])
            if candidate in self._blocked:
                return True
        return False
