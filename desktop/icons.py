"""Small original vector icons; no external font or image service."""

from functools import lru_cache

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

PATHS = {
    "home": "M3 10 12 3 21 10 M5 9v12h14V9 M9 21v-8h6v8",
    "farm": "M3 11 12 5 21 11 M5 10v8h14v-8 M3 21h18 M9 14h6 M12 14v4",
    "user": "M16 7a4 4 0 1 1-8 0a4 4 0 1 1 8 0 M4 21v-2a8 8 0 0 1 16 0v2",
    "users": (
        "M10 8a3 3 0 1 1-6 0a3 3 0 1 1 6 0 M2 20v-2a5 5 0 0 "
        "1 10 0v2 M18 10a3 3 0 1 1-6 0a3 3 0 1 1 6 0 M14 16a5 5 0 0 1 8 4"
    ),
    "share": (
        "M20 5a2 2 0 1 1-4 0a2 2 0 1 1 4 0 M7 12a2 2 0 1 "
        "1-4 0a2 2 0 1 1 4 0 M20 19a2 2 0 1 1-4 0a2 2 0 1 1 4 0 M7 11l9-5 M7 13l9 5"
    ),
    "mail": "M3 5h18v14H3z M3 5l9 7 9-7",
    "lock": "M5 10h14v11H5z M8 10V6a4 4 0 0 1 8 0v4 M12 15v2",
    "layers": "M3 8l9-5 9 5-9 5z M3 12l9 5 9-5 M3 16l9 5 9-5",
    "calendar": "M4 5h16v16H4z M8 3v4 M16 3v4 M4 10h16 M8 14h2 M14 14h2",
    "lines": "M4 5h16 M4 12h16 M4 19h16 M7 3v4 M17 10v4 M10 17v4",
    "settings": (
        "M12 8a4 4 0 1 1 0 8a4 4 0 1 1 0-8 M12 2v3 M12 "
        "19v3 M2 12h3 M19 12h3 M5 5l2 2 M17 17l2 2 M19 5l-2 2 M7 17l-2 2"
    ),
    "plus": "M12 5v14 M5 12h14",
    "refresh": "M20 10a8 8 0 0 0-14-4L3 9 M3 4v5h5 M4 14a8 8 0 0 0 14 4l3-3 M21 20v-5h-5",
    "edit": "M4 16 16 4l4 4L8 20H4z M13 7l4 4",
    "close": "M6 6l12 12 M18 6 6 18",
    "check": "M4 12l5 5 11-11",
    "logout": "M10 3H4v18h6 M10 12h11 M17 8l4 4-4 4",
    "transfer": "M3 7h17 M16 3l4 4-4 4 M21 17H4 M8 13l-4 4 4 4",
}


@lru_cache(maxsize=96)
def icon(name: str, color="#91a6b2") -> QIcon:
    path = PATHS.get(name, PATHS["layers"])
    svg = QByteArray(
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            f'<path d="{path}" fill="none" stroke="{color}" stroke-width="1.7" '
            'stroke-linecap="round" stroke-linejoin="round"/></svg>'
        ).encode()
    )
    renderer = QSvgRenderer(svg)
    result = QIcon()
    for size in (16, 20, 24, 32, 40, 48, 64):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        result.addPixmap(pixmap)
    return result
