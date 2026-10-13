import os
import sys

from PySide6.QtCore import QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from desktop.health import check_health

SECTIONS = (
    "Painel",
    "Produtores",
    "Fazendas",
    "Talhões",
    "Safras",
    "Operações",
    "Máquinas",
    "Implementos",
    "Planejamentos",
    "Exportações",
    "Configurações",
)


class HealthWorker(QThread):
    checked = Signal(bool)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        self.checked.emit(check_health(self.url))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AgroLines")
        self.resize(1000, 650)
        self.connection = QLabel("Verificando servidor…")
        self.pages = QStackedWidget()
        navigation = QListWidget()
        for section in SECTIONS:
            navigation.addItem(section)
            page = QLabel(f"{section} — Em desenvolvimento")
            page.setMargin(24)
            self.pages.addWidget(page)
        navigation.currentRowChanged.connect(self.pages.setCurrentIndex)
        navigation.setCurrentRow(0)
        row = QHBoxLayout()
        row.addWidget(navigation, 1)
        row.addWidget(self.pages, 4)
        layout = QVBoxLayout()
        layout.addWidget(self.connection)
        layout.addLayout(row)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.worker = HealthWorker(os.getenv("AGROLINES_API_URL", "http://127.0.0.1:8000"), self)
        self.worker.checked.connect(self.show_health)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(10000)
        self.refresh()

    def refresh(self):
        if not self.worker.isRunning():
            self.worker.start()

    def show_health(self, online: bool):
        self.connection.setText(
            "Servidor online — sincronização não implementada"
            if online
            else "Servidor offline — sincronização não implementada"
        )

    def closeEvent(self, event):
        self.timer.stop()
        self.worker.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
