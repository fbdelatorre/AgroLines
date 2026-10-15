"""Local bounded diagnostics: no credentials, project contents or automatic upload."""

import json
import logging
import re
import sys
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile

from desktop.storage import data_directory


class EventFormatter(logging.Formatter):
    def format(self, record):
        value = {
            "time": self.formatTime(record),
            "event_id": getattr(record, "event_id", str(uuid4())),
            "event": getattr(record, "event", "lifecycle"),
            "phase": getattr(record, "phase", "application"),
        }
        if getattr(record, "error_type", None):
            value["error_type"] = record.error_type
            value["frames"] = record.frames
        return json.dumps(value, ensure_ascii=True)


def initialize(directory=None):
    root = directory or data_directory() / "Diagnostics"
    root.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("agrolines.desktop")
    if not logger.handlers:
        handler = RotatingFileHandler(
            root / "desktop.log", maxBytes=1024 * 1024, backupCount=2, encoding="utf-8"
        )
        handler.setFormatter(EventFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def record_failure(logger, kind, value, tb):
    # Deliberately omit exception messages, paths, local variables and request data.
    frames = [
        {"function": row.name, "line": row.lineno, "module": Path(row.filename).stem}
        for row in traceback.extract_tb(tb)[-12:]
    ]
    identifier = str(uuid4())
    logger.error(
        "Unhandled failure",
        extra={
            "event_id": identifier,
            "event": "unhandled_failure",
            "phase": "application",
            "error_type": kind.__name__,
            "frames": frames,
        },
    )
    return identifier


def build_identity():
    try:
        root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
        value = json.loads((root / "distribution/windows/metadata.json").read_text())
    except (OSError, ValueError):
        value = {}
    return {
        key: value[key]
        for key, pattern in (("version", r"\d+\.\d+\.\d+\.\d+"), ("source_commit", r"[a-f0-9]{40}"))
        if isinstance(value.get(key), str) and re.fullmatch(pattern, value[key])
    }


def native_modules():
    """Current process only; paths outside the runtime/system are never disclosed."""
    if sys.platform != "win32":
        return {"status": "not_windows", "modules": []}
    import ctypes
    from ctypes import wintypes

    try:
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.EnumProcessModules.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(wintypes.HMODULE),
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
        ]
        psapi.EnumProcessModules.restype = wintypes.BOOL
        kernel.GetModuleFileNameW.argtypes = [wintypes.HMODULE, wintypes.LPWSTR, wintypes.DWORD]
        kernel.GetModuleFileNameW.restype = wintypes.DWORD
        handles, needed = (wintypes.HMODULE * 2048)(), wintypes.DWORD()
        if not psapi.EnumProcessModules(
            kernel.GetCurrentProcess(), handles, ctypes.sizeof(handles), ctypes.byref(needed)
        ):
            raise OSError("Module observation unavailable")
        root = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent)).resolve()
        import os

        system = Path(os.environ["WINDIR"]).resolve()
        result = set()
        for handle in handles[: min(needed.value // ctypes.sizeof(wintypes.HMODULE), len(handles))]:
            buffer = ctypes.create_unicode_buffer(32768)
            if not kernel.GetModuleFileNameW(handle, buffer, len(buffer)):
                continue
            path = Path(buffer.value).resolve()
            if path.is_relative_to(root):
                result.add(path.relative_to(root).as_posix())
            elif path.is_relative_to(system):
                result.add("windows-system/" + path.name)
            else:
                result.add("external-path-redacted")
        return {"status": "sampled_current_process_only", "modules": sorted(result)}
    except (OSError, KeyError):
        return {"status": "unavailable", "modules": []}


def snapshot(directory=None, *, include_events=True, include_modules=False):
    root = directory or data_directory() / "Diagnostics"
    events = []
    if include_events:
        for file in (root / "desktop.log.2", root / "desktop.log.1", root / "desktop.log"):
            if not file.is_file() or file.is_symlink() or file.stat().st_size > 2 * 1024 * 1024:
                continue
            for line in file.read_text(encoding="utf-8", errors="replace").splitlines()[-128:]:
                try:
                    event = json.loads(line)
                    # Only our structured events, never legacy/raw messages or exception text.
                    if event.get("event") not in ("lifecycle", "unhandled_failure"):
                        continue
                    allowed = {"time", "event_id", "event", "phase", "error_type", "frames"}
                    if set(event) - allowed:
                        continue
                    events.append(event)
                except (ValueError, AttributeError, TypeError):
                    continue
    windows = sys.getwindowsversion() if sys.platform == "win32" else None
    return {
        "format": 1,
        "correlation_id": str(uuid4()),
        "build": build_identity(),
        "windows": {"major": windows.major, "minor": windows.minor, "build": windows.build}
        if windows
        else None,
        "frozen": bool(getattr(sys, "frozen", False)),
        "events": events[-128:],
        "native_modules": native_modules()
        if include_modules
        else {"status": "not_requested", "modules": []},
        "automatic_transmission": False,
    }


def export_zip(destination, value):
    from core.offline_policy import require_local_path

    require_local_path(destination)
    # Write exactly the JSON shown in the review dialog; no hidden/raw attachments.
    with ZipFile(destination, "x", compression=ZIP_DEFLATED) as archive:
        archive.writestr("diagnostico.json", json.dumps(value, ensure_ascii=False, indent=2))
        archive.writestr(
            "LEIA-ME.txt", "Diagnóstico local revisado pelo usuário. Nenhum envio automático.\n"
        )


def review_export(parent):
    from PySide6.QtWidgets import (
        QCheckBox,
        QDialog,
        QDialogButtonBox,
        QFileDialog,
        QLabel,
        QPlainTextEdit,
        QVBoxLayout,
    )

    dialog = QDialog(parent)
    dialog.setWindowTitle("Revisar diagnóstico local")
    dialog.resize(720, 560)
    layout = QVBoxLayout(dialog)
    layout.addWidget(
        QLabel("Revise o conteúdo antes de salvar. O AgroLines não envia este ZIP automaticamente.")
    )
    events, modules = (
        QCheckBox("Incluir eventos locais sanitizados"),
        QCheckBox("Incluir módulos nativos deste processo"),
    )
    events.setChecked(True)
    layout.addWidget(events)
    layout.addWidget(modules)
    preview = QPlainTextEdit()
    preview.setReadOnly(True)
    layout.addWidget(preview)
    current = {}

    def refresh():
        current.clear()
        current.update(
            snapshot(include_events=events.isChecked(), include_modules=modules.isChecked())
        )
        preview.setPlainText(json.dumps(current, ensure_ascii=False, indent=2))

    events.toggled.connect(refresh)
    modules.toggled.connect(refresh)
    buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
    buttons.button(QDialogButtonBox.Save).setText("Salvar ZIP revisado…")
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)
    refresh()
    if dialog.exec() != QDialog.Accepted:
        return
    destination, _ = QFileDialog.getSaveFileName(parent, "Salvar diagnóstico", "", "ZIP (*.zip)")
    if destination:
        parent.run(lambda: export_zip(destination, current))


def run(entry):
    try:
        logger = initialize()
    except OSError:
        logger = logging.getLogger("agrolines.desktop")
        logger.addHandler(logging.NullHandler())
    logger.info("Desktop started")

    def failed(kind, value, tb):
        identifier = record_failure(logger, kind, value, tb)
        from PySide6.QtWidgets import QApplication, QMessageBox

        if QApplication.instance():
            QMessageBox.critical(
                None,
                "AgroLines · diagnóstico",
                "Não foi possível concluir a operação. Preserve seu projeto e consulte o suporte. "
                "O diagnóstico local não é enviado automaticamente. "
                "Não desative proteções do Windows. Código do evento: " + identifier,
            )

    sys.excepthook = failed
    try:
        result = entry()
        logger.info("Desktop stopped")
        return result
    except Exception:
        failed(*sys.exc_info())
        return 1
