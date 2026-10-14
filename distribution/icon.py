"""Generate a Windows ICO from the project's SVG; Qt is a build-time dependency."""

import struct
from pathlib import Path


def generate(source, target):
    from PySide6.QtCore import QBuffer, QByteArray, QIODevice
    from PySide6.QtGui import QImage, QPainter
    from PySide6.QtSvg import QSvgRenderer

    renderer = QSvgRenderer(str(source))
    if not renderer.isValid():
        raise ValueError("Invalid brand SVG")
    images = []
    for size in [16, 32, 48, 64, 128, 256]:
        image = QImage(size, size, QImage.Format_ARGB32)
        image.fill(0)
        painter = QPainter(image)
        renderer.render(painter)
        painter.end()
        data = QByteArray()
        buffer = QBuffer(data)
        buffer.open(QIODevice.WriteOnly)
        if not image.save(buffer, "PNG"):
            raise ValueError("Icon rendering failed")
        images.append((size, bytes(data)))
    offset = 6 + 16 * len(images)
    header = struct.pack("<HHH", 0, 1, len(images))
    for size, content in images:
        header += struct.pack(
            "<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(content), offset
        )
        offset += len(content)
    Path(target).write_bytes(header + b"".join(content for _, content in images))
