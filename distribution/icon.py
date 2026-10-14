"""Resize original artwork without cropping/recolouring; Qt is a build dependency."""

import struct
from pathlib import Path


def render(source, size):
    from PySide6.QtCore import QRectF, Qt
    from PySide6.QtGui import QImage, QPainter
    from PySide6.QtSvg import QSvgRenderer

    image = QImage(size, size, QImage.Format_ARGB32)
    image.fill(0)
    if Path(source).suffix.lower() == ".svg":
        renderer = QSvgRenderer(str(source))
        if not renderer.isValid():
            raise ValueError("Invalid brand SVG")
        dimensions = renderer.defaultSize()
        dimensions.scale(size, size, Qt.KeepAspectRatio)
        painter = QPainter(image)
        renderer.render(
            painter,
            QRectF(
                (size - dimensions.width()) / 2,
                (size - dimensions.height()) / 2,
                dimensions.width(),
                dimensions.height(),
            ),
        )
    else:
        original = QImage(str(source))
        if original.isNull():
            raise ValueError("Invalid original brand image")
        scaled = original.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter = QPainter(image)
        painter.drawImage((size - scaled.width()) // 2, (size - scaled.height()) // 2, scaled)
    painter.end()
    return image


def generate(source, target):
    from PySide6.QtCore import QBuffer, QByteArray, QIODevice

    images = []
    for size in [16, 32, 48, 64, 128, 256]:
        image = render(source, size)
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
