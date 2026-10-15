"""Local bounded diagnostics: no credentials, project contents or automatic upload."""

import logging
import sys
import traceback
from logging.handlers import RotatingFileHandler

from desktop.storage import data_directory


def initialize(directory=None):
    root = directory or data_directory() / "Diagnostics"
    root.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("agrolines.desktop")
    if not logger.handlers:
        handler = RotatingFileHandler(
            root / "desktop.log", maxBytes=1024 * 1024, backupCount=2, encoding="utf-8"
        )
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def record_failure(logger, kind, value, tb):
    # Deliberately omit exception messages, paths, local variables and request data.
    frames = [(row.name, row.lineno) for row in traceback.extract_tb(tb)]
    logger.error("Unhandled %s; frames=%s", kind.__name__, frames)


def run(entry):
    try:
        logger = initialize()
    except OSError:
        logger = logging.getLogger("agrolines.desktop")
        logger.addHandler(logging.NullHandler())
    logger.info("Desktop started")

    def failed(kind, value, tb):
        record_failure(logger, kind, value, tb)
        from PySide6.QtWidgets import QApplication, QMessageBox

        if QApplication.instance():
            QMessageBox.critical(
                None,
                "AgroLines · diagnóstico",
                "Não foi possível concluir a operação. Preserve seu projeto e consulte o suporte. "
                "O diagnóstico local não é enviado automaticamente. "
                "Não desative proteções do Windows.",
            )

    sys.excepthook = failed
    try:
        result = entry()
        logger.info("Desktop stopped")
        return result
    except Exception:
        failed(*sys.exc_info())
        return 1
