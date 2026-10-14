import json

import pytest
from PySide6.QtGui import QImage

from distribution import branding
from distribution.icon import generate, render


def test_approved_artwork_and_all_ico_frames(tmp_path):
    source = branding.approved_source()
    original = QImage(str(source))
    assert original.size().width() == original.size().height() == 1080
    # The supplied art is opaque; white borders must not be erased.
    assert original.pixelColor(0, 0).alpha() == 255
    icon = tmp_path / "app.ico"
    generate(source, icon)
    frames = branding.ico_frames(icon)
    for size, frame in zip((16, 32, 48, 64, 128, 256), frames, strict=True):
        image = QImage.fromData(frame)
        assert image.width() == image.height() == size
        assert image.pixelColor(0, 0).alpha() == 255


def test_resizing_preserves_proportion_and_alpha(tmp_path):
    source = tmp_path / "transparent.png"
    image = QImage(100, 50, QImage.Format_ARGB32)
    image.fill(0x8080FF00)
    image.save(str(source))
    result = render(source, 100)
    assert result.pixelColor(50, 10).alpha() == 0
    assert result.pixelColor(50, 24).alpha() == 0
    assert result.pixelColor(50, 25).alpha() == 128
    assert result.pixelColor(50, 74).alpha() == 128
    assert result.pixelColor(50, 75).alpha() == 0
    assert result.pixelColor(50, 50).green() == 255


def test_original_tampering_fails_closed(tmp_path, monkeypatch):
    source = branding.approved_source()
    (tmp_path / source.name).write_bytes(source.read_bytes() + b"changed")
    (tmp_path / "originals.json").write_text(
        json.dumps(
            {
                "files": [{"name": source.name, "sha256": branding.digest(source)}],
            }
        )
    )
    monkeypatch.setattr(branding, "BRANDING", tmp_path)
    with pytest.raises(ValueError, match="Approved original"):
        branding.approved_source()
