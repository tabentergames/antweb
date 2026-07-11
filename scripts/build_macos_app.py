#!/usr/bin/env python3
"""Build the native macOS TabX.app package with PyInstaller."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST_APP = ROOT / "dist" / "TabX.app"
TARGET_APP = ROOT / "TabX.app"


def main() -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "TabX.spec",
        ],
        cwd=ROOT,
        check=True,
    )

    if not DIST_APP.exists():
        raise FileNotFoundError(f"PyInstaller did not create {DIST_APP}")

    if TARGET_APP.exists():
        shutil.rmtree(TARGET_APP)

    shutil.copytree(DIST_APP, TARGET_APP, symlinks=True)
    print(f"Built {TARGET_APP}")


if __name__ == "__main__":
    main()
