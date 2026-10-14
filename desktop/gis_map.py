"""Leaflet in Qt WebEngine: rendering only, never API/session tokens in JavaScript."""

import html
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

from pyproj import CRS
from PySide6.QtCore import QObject, Qt, QUrl, Signal, Slot
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import (
    QWebEnginePage,
    QWebEngineProfile,
    QWebEngineSettings,
    QWebEngineUrlRequestInterceptor,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from core.geography import exact_transform
from desktop.ui import action, label

ASSETS = Path(__file__).parent / "map_assets"


def imagery_configuration():
    if os.getenv("AGROLINES_TILE_AUTHORIZED") != "1":
        return None
    url = os.getenv("AGROLINES_TILE_URL", "")
    credit = os.getenv("AGROLINES_TILE_ATTRIBUTION", "")
    license_url = os.getenv("AGROLINES_TILE_LICENSE_URL", "")
    parsed, license_parsed = urlsplit(url), urlsplit(license_url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or not all(token in url for token in ("{z}", "{x}", "{y}"))
        or not credit
        or license_parsed.scheme != "https"
        or not license_parsed.hostname
    ):
        raise ValueError(
            "Provedor de imagens exige URL HTTPS, atribuição, licença e autorização explícita."
        )
    return {
        "url": url,
        "attribution": html.escape(credit)
        + ' · <a href="'
        + html.escape(license_url, quote=True)
        + '">Licença</a>',
    }


class Requests(QWebEngineUrlRequestInterceptor):
    def __init__(self, config, parent):
        super().__init__(parent)
        self.host = urlsplit(config["url"]).hostname if config else None
        self.online = False

    def interceptRequest(self, info):
        url = info.requestUrl()
        if url.scheme() == "file":
            path = Path(url.toLocalFile()).resolve()
            info.block(not path.is_relative_to(ASSETS.resolve()))
        elif url.scheme() in ("qrc", "data", "about"):
            return
        else:
            info.block(
                not (
                    self.online
                    and self.host
                    and url.scheme() == "https"
                    and url.host() == self.host
                )
            )


class LocalPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, kind, is_main_frame):
        return (
            url.scheme() == "file"
            and Path(url.toLocalFile()).resolve() == (ASSETS / "map.html").resolve()
        )


class Bridge(QObject):
    loaded = Signal()
    selection = Signal(str)
    position = Signal(float, float)

    @Slot(float, float)
    def cursor(self, longitude, latitude):
        self.position.emit(longitude, latitude)

    @Slot()
    def ready(self):
        self.loaded.emit()

    @Slot(str)
    def selected(self, identifier):
        self.selection.emit(identifier)


class WebMap(QWidget):
    featureSelected = Signal(dict)
    readyChanged = Signal()

    def __init__(self):
        super().__init__()
        self.is_ready = False
        self.collection = {"type": "FeatureCollection", "features": []}
        self.fit_pending = False
        self.current_id = None
        self.set_work_crs("EPSG:32723")
        self.imagery = imagery_configuration()
        body = QVBoxLayout(self)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        tools = QHBoxLayout()
        tools.setContentsMargins(8, 5, 8, 5)
        action("Extensão", lambda: self.run("fit", None), tools, "frame")
        action("+", lambda: self.run("zoom", 1), tools)
        action("−", lambda: self.run("zoom", -1), tools)
        tools.addWidget(label("Selecionar e identificar · arraste para deslocar", "Hint"), 1)
        body.addLayout(tools)
        self.view = QWebEngineView()
        self.profile = QWebEngineProfile()  # Off-the-record; no persistent third-party cache.
        self.profile.setHttpCacheType(QWebEngineProfile.NoCache)
        self.interceptor = Requests(self.imagery, self.profile)
        self.profile.setUrlRequestInterceptor(self.interceptor)
        self.page = LocalPage(self.profile, self.view)
        self.page.settings().setAttribute(
            QWebEngineSettings.LocalContentCanAccessRemoteUrls, bool(self.imagery)
        )
        self.page.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self.page.settings().setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, False)
        self.page.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, False)
        self.view.setPage(self.page)
        self.page.destroyed.connect(self.profile.deleteLater)
        self.channel = QWebChannel(self.page)
        self.bridge = Bridge(self.channel)
        self.channel.registerObject("bridge", self.bridge)
        self.page.setWebChannel(self.channel)
        self.bridge.loaded.connect(self.loaded)
        self.bridge.selection.connect(self.selected)
        self.bridge.position.connect(self.cursor)
        body.addWidget(self.view, 1)
        self.state_label = QLabel("Carregando renderizador cartográfico local…")
        self.state_label.setTextFormat(Qt.PlainText)
        self.state_label.setObjectName("Hint")
        body.addWidget(self.state_label)
        self.view.load(QUrl.fromLocalFile(str(ASSETS / "map.html")))

    def set_work_crs(self, value):
        self.work_crs = value
        self.cursor_transform = exact_transform(CRS.from_epsg(4326), CRS.from_user_input(value))

    def cursor(self, longitude, latitude):
        try:
            east, north = self.cursor_transform.transform(longitude, latitude, errcheck=True)
            self.state_label.setText(
                f"Lat {latitude:.7f}° · Lon {longitude:.7f}° | "
                f"E {east:.3f} m · N {north:.3f} m · {self.work_crs} · cursor visual"
            )
        except Exception:
            self.state_label.setText("Coordenadas do cursor fora do domínio do SRC.")

    def loaded(self):
        self.is_ready = True
        self.run("collection", self.collection, self.fit_pending)
        self.run("imagery", self.imagery)
        self.run("online", self.interceptor.online)
        self.state_label.setText(
            "Leaflet · imagens autorizadas, somente online"
            if self.imagery
            else "Mapa vetorial · escala visual aproximada · medições no painel Objeto"
        )
        self.readyChanged.emit()

    def run(self, method, *args):
        if self.is_ready:
            if method == "collection":
                collection = args[0]
                presentation = {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "id": f["id"],
                            "geometry": f["geometry"],
                            "properties": {
                                "name": f["properties"]["name"],
                                "preview": bool(f["properties"].get("preview")),
                            },
                        }
                        for f in collection["features"]
                    ],
                }
                args = (presentation, *args[1:])
            encoded = ",".join(
                json.dumps(value, ensure_ascii=True, allow_nan=False) for value in args
            )
            self.page.runJavaScript(f"window.agro.{method}({encoded});")

    def set_collection(self, collection, fit=False):
        self.collection = collection
        self.fit_pending = fit
        self.current_id = None
        self.run("collection", collection, fit)

    def selected(self, identifier):
        feature = next((f for f in self.collection["features"] if str(f["id"]) == identifier), None)
        if feature:
            self.current_id = identifier
            self.featureSelected.emit(feature)

    def set_online(self, online):
        self.interceptor.online = bool(online)
        self.run("online", bool(online))

    def clear(self):
        self.set_collection({"type": "FeatureCollection", "features": []})

    def dispose(self):
        self.is_ready = False
        self.view.hide()
        self.page.deleteLater()
