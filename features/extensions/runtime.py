"""
TabX F3 — Extension runtime (JS/CSS injection).

Each extension lives in data/extensions/<name>/manifest.json.

Manifest schema:
{
    "name": "Dark Mode Everywhere",
    "version": "1.0",
    "description": "...",
    "matches": ["https://example.com/*", "*://*.github.com/*"],
    "js":  ["content.js"],
    "css": ["style.css"],
    "run_at": "document_end"   // "document_start" | "document_end" (default)
}

URL match pattern format (Chrome extension subset):
  <scheme>://<host>/<path>
  scheme : "*" | "http" | "https" | "ftp" | "file"
  host   : "*" | "*.example.com" | "example.com"
  path   : any string with optional "*" wildcards
  Special shorthand: "*" alone means "match every URL".

QWebEngineScript has no built-in URL filter — it fires on every page.
We wrap every injected payload in a JS guard that checks window.location
against the manifest patterns at run time and bails immediately on mismatch.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from PyQt6.QtWebEngineCore import (
    QWebEngineProfile,
    QWebEngineScript,
)

log = logging.getLogger(__name__)

_EXTENSIONS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "extensions"


# ---------------------------------------------------------------------------
# URL pattern matching (Python — used for validation / tests)
# ---------------------------------------------------------------------------

def _pattern_to_regex(pattern: str) -> re.Pattern[str]:
    """Convert a match-pattern string to a compiled regex.

    Raises ValueError for malformed patterns.
    """
    if pattern == "*":
        return re.compile(r".*")

    m = re.fullmatch(r"(\*|https?|ftp|file)://([^/]+)(/.*)$", pattern)
    if not m:
        raise ValueError(f"Invalid match pattern: {pattern!r}")

    scheme_part, host_part, path_part = m.group(1), m.group(2), m.group(3)

    # scheme
    scheme_re = r"https?" if scheme_part == "*" else re.escape(scheme_part)

    # host: "*" = any, "*.example.com" = any subdomain of example.com
    if host_part == "*":
        host_re = r"[^/]+"
    elif host_part.startswith("*."):
        base = re.escape(host_part[2:])
        host_re = rf"(?:[^/]+\.)?{base}"
    else:
        host_re = re.escape(host_part)

    # path: "*" wildcards → .*
    path_re = re.escape(path_part).replace(r"\*", ".*")

    return re.compile(rf"^{scheme_re}://{host_re}{path_re}$")


def matches_url(url: str, patterns: list[str]) -> bool:
    """Return True if *url* matches any pattern in *patterns*."""
    for pat in patterns:
        try:
            if _pattern_to_regex(pat).match(url):
                return True
        except ValueError:
            log.warning("Skipping malformed match pattern: %r", pat)
    return False


# ---------------------------------------------------------------------------
# Compact JS URL matcher (embedded verbatim into every script wrapper)
# ---------------------------------------------------------------------------

# This runs inside the page at injection time to decide whether to proceed.
# Kept intentionally small — no external deps, no closures leaked to page.
_JS_MATCH_FN = r"""
function __tabxMatch(url, patterns) {
  for (var i = 0; i < patterns.length; i++) {
    var p = patterns[i];
    if (p === '*') return true;
    var pm = p.match(/^(\*|https?|ftp|file):\/\/([^/]+)(\/.*)?$/);
    if (!pm) continue;
    var scheme = pm[1], host = pm[2], path = pm[3] || '/';
    var um = url.match(/^([a-z]+):\/\/([^/]+)(\/.*)?$/);
    if (!um) continue;
    var us = um[1], uh = um[2], up = um[3] || '/';
    if (scheme !== '*' && scheme !== us) continue;
    if (host !== '*') {
      if (host.startsWith('*.')) {
        var base = host.slice(2);
        if (uh !== base && !uh.endsWith('.' + base)) continue;
      } else {
        if (uh !== host) continue;
      }
    }
    var pr = new RegExp('^' + path.replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*') + '$');
    if (pr.test(up)) return true;
  }
  return false;
}
""".strip()


def _guard_wrap(payload: str, patterns: list[str]) -> str:
    """Wrap *payload* so it only executes when window.location matches *patterns*."""
    patterns_json = json.dumps(patterns)
    return f"""\
(function() {{
  {_JS_MATCH_FN}
  if (!__tabxMatch(window.location.href, {patterns_json})) return;
  {payload}
}})();"""


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class ExtensionManifest:
    name: str
    version: str
    description: str
    matches: list[str]
    js_files: list[Path]
    css_files: list[Path]
    run_at: str
    directory: Path


# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------

@dataclass
class ExtensionRuntime:
    """Loads extensions and registers guarded scripts into a QWebEngineProfile."""

    profile: QWebEngineProfile
    extensions: list[ExtensionManifest] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_all(self, extensions_dir: Path | None = None) -> int:
        """Scan *extensions_dir* and register all valid extensions.

        Returns the number of extensions successfully loaded.
        """
        base = extensions_dir or _EXTENSIONS_DIR
        base.mkdir(parents=True, exist_ok=True)
        loaded = 0
        for manifest_path in sorted(base.rglob("manifest.json")):
            try:
                ext = self._parse_manifest(manifest_path)
                self._register_extension(ext)
                self.extensions.append(ext)
                loaded += 1
                log.info("Extension loaded: %s v%s  patterns=%s", ext.name, ext.version, ext.matches)
            except Exception as exc:  # noqa: BLE001
                log.warning("Failed to load extension at %s: %s", manifest_path, exc)
        return loaded

    def inject_css(self, css: str, name: str = "tabx-inline", matches: list[str] | None = None) -> None:
        """Inject raw CSS into pages matching *matches* (default: all pages)."""
        payload = (
            f"var s=document.createElement('style');"
            f"s.id={json.dumps(name)};"
            f"s.textContent={json.dumps(css)};"
            f"document.head.appendChild(s);"
        )
        src = _guard_wrap(payload, matches or ["*"])
        self._add_script(name, src, QWebEngineScript.InjectionPoint.DocumentReady)

    def inject_js(self, js: str, name: str = "tabx-inline-js", matches: list[str] | None = None) -> None:
        """Inject raw JS into pages matching *matches* (default: all pages)."""
        src = _guard_wrap(js, matches or ["*"])
        self._add_script(name, src, QWebEngineScript.InjectionPoint.DocumentReady)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _parse_manifest(self, manifest_path: Path) -> ExtensionManifest:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        ext_dir = manifest_path.parent
        return ExtensionManifest(
            name=data["name"],
            version=str(data.get("version", "1.0")),
            description=data.get("description", ""),
            matches=data.get("matches", ["*"]),
            js_files=[ext_dir / f for f in data.get("js", [])],
            css_files=[ext_dir / f for f in data.get("css", [])],
            run_at=data.get("run_at", "document_end"),
            directory=ext_dir,
        )

    def _register_extension(self, ext: ExtensionManifest) -> None:
        injection_point = (
            QWebEngineScript.InjectionPoint.DocumentCreation
            if ext.run_at == "document_start"
            else QWebEngineScript.InjectionPoint.DocumentReady
        )

        for css_path in ext.css_files:
            if not css_path.exists():
                log.warning("CSS file missing: %s", css_path)
                continue
            css_src = css_path.read_text(encoding="utf-8")
            payload = (
                f"var s=document.createElement('style');"
                f"s.textContent={json.dumps(css_src)};"
                f"document.head.appendChild(s);"
            )
            src = _guard_wrap(payload, ext.matches)
            self._add_script(f"{ext.name}:css:{css_path.name}", src, injection_point)

        for js_path in ext.js_files:
            if not js_path.exists():
                log.warning("JS file missing: %s", js_path)
                continue
            js_src = js_path.read_text(encoding="utf-8")
            src = _guard_wrap(js_src, ext.matches)
            self._add_script(f"{ext.name}:js:{js_path.name}", src, injection_point)

    def _add_script(
        self,
        name: str,
        source: str,
        injection_point: QWebEngineScript.InjectionPoint,
    ) -> None:
        script = QWebEngineScript()
        script.setName(name)
        script.setSourceCode(source)
        script.setInjectionPoint(injection_point)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        script.setRunsOnSubFrames(False)
        self.profile.scripts().insert(script)
