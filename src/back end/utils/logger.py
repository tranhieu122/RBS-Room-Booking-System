"""Centralised logging configuration for the application.

Usage (in any module):
    from utils.logger import get_logger
    log = get_logger(__name__)
    log.info("something happened")
    log.error("oh no", exc_info=True)   # include traceback

Log file: <project>/src/back end/logs/app.log  (rotates at 2 MB, keeps 3 backups)
Console:  WARNING and above only (to avoid cluttering the Tkinter window).
"""
from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

_LOG_DIR  = Path(__file__).resolve().parents[1] / "logs"
_LOG_FILE = _LOG_DIR / "app.log"

_configured = False


def _configure() -> None:
    global _configured
    if _configured:
        return

    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # ── Rotating file handler (DEBUG+) ────────────────────────────────────────
    fh = logging.handlers.RotatingFileHandler(
        _LOG_FILE,
        maxBytes=2 * 1024 * 1024,   # 2 MB
        backupCount=3,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))

    # ── Console handler (WARNING+) ────────────────────────────────────────────
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    root.addHandler(fh)
    root.addHandler(ch)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger; configures the root logger on first call."""
    _configure()
    return logging.getLogger(name)
