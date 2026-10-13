"""Shared, DPI-aware components for the dark desktop interface."""

from PySide6.QtCore import QPoint, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from desktop.icons import icon

THEME = """
QFrame#TopBar { background: #0b1319; border-bottom: 1px solid #24323c; }
QMainWindow#VisualWorkspace { background: #0c151c; }
QFrame#MapViewport { background: #111f26; border: 1px solid #293b43; }
QLabel#MapTitle { font-size: 22pt; color: #526e79; font-weight: 600; }
QLabel#PanelHeading { font-weight: 600; color: #cad8df; }
QLabel#Unavailable { color: #87a99a; font-size: 8pt; }
QDockWidget { color: #d9e4e9; border: 1px solid #293841; }
QDockWidget::title { background: #101c24; padding: 7px 10px;
    border-bottom: 1px solid #283740; text-align: left; }
QDockWidget > QWidget { background: #0e1921; }
QMainWindow::separator { background: #26363e; width: 5px; height: 5px; }
QMainWindow::separator:hover { background: #2e9569; }
QTabWidget#ParameterTabs QTabBar::tab { font-size: 8pt; padding: 6px 7px; }
QToolButton { color: #d4e1e7; background: transparent; border: 1px solid transparent;
    border-radius: 3px; padding: 5px; }
QToolButton:hover { background: #1b3039; border-color: #344954; }
QToolButton:checked { background: #224b39; border-color: #2b9364; }
QToolButton:disabled { color: #596d78; }

QMainWindow, QWidget#Shell, QWidget#Page { background: #0c151c; }
QWidget { color: #e2eaf0; }
QLabel { background: transparent; border: none; }
QLabel#PageTitle { font-size: 17pt; font-weight: 600; }
QLabel#CardTitle { font-size: 11pt; font-weight: 600; }
QLabel#Description, QLabel#Hint { color: #92a6b5; }
QLabel#Hint { font-size: 8pt; }
QLabel#FieldError { color: #ff969b; font-size: 8pt; }
QLabel#Brand { font-size: 14pt; font-weight: 600; color: #e2eaf0; }
QLabel#SectionLabel { color: #8297a7; font-size: 8pt; }
QFrame#Card { background: #101c24; border: 1px solid #2a3a47; border-radius: 8px; }
QFrame#Sidebar { background: #0e171e; border-right: 1px solid #293944; }
QPlainTextEdit { background: #101d27; border: 1px solid #354754; border-radius: 5px; }
QLineEdit, QComboBox { background: #101d27; border: 1px solid #354754;
    border-radius: 5px; padding: 4px 8px; min-height: 19px; }
QLineEdit:focus, QComboBox:focus { border-color: #5dc58a; }
QLineEdit[invalid="true"] { border-color: #e77f89; }
QLineEdit:read-only { color: #a8bcc9; background: #1a2933; }
QComboBox::drop-down { width: 22px; border: none; }
QComboBox QAbstractItemView { background: #192b36; selection-background-color: #28593f; }
QPushButton { background: #22343f; border: 1px solid #3a4e5a; border-radius: 5px;
    padding: 5px 10px; min-height: 18px; }
QPushButton:hover { background: #2a4250; border-color: #597786; }
QPushButton:pressed { background: #182c36; }
QPushButton[variant="primary"] { background: #23885a; border-color: #2a9d68; color: #f3fff7; }
QPushButton[variant="primary"]:hover { background: #318557; }
QPushButton[variant="danger"] { color: #ffb0b4; background: #35272e; border-color: #66434b; }
QPushButton:disabled, QComboBox:disabled { color: #6f8492; background: #1b2a34;
    border-color: #2d3d49; }
QListWidget#Navigation { background: transparent; border: none; outline: 0; }
QListWidget#Navigation::item { height: 27px; padding: 2px 6px; margin: 1px 3px;
    border-radius: 5px; border-left: 3px solid transparent; }
QListWidget#Navigation::item:hover { background: #20323c; }
QListWidget#Navigation::item:selected { background: #203c30; color: #9ee8b9;
    border-left: 3px solid #63ce91; }
QTableWidget { background: #14222c; alternate-background-color: #192933; border: 1px solid #2d3e49;
    border-radius: 5px; gridline-color: #293b47; selection-background-color: #244735;
    selection-color: #eefbf2; outline: 0; }
QTableWidget::item { padding: 3px 8px; border: none; }
QTableWidget::item:selected { background: #244735; }
QHeaderView::section { background: #20313c; color: #adc0cb; padding: 5px 8px;
    border: none; border-bottom: 1px solid #364a56; font-weight: 600; }
QListWidget { background: #14222c; border: 1px solid #354754; border-radius: 5px; outline: 0; }
QListWidget::item { padding: 5px 8px; }
QListWidget::item:selected { background: #244735; }
QTabWidget::pane { border: none; }
QTabBar::tab { background: transparent; padding: 7px 12px; color: #91a7b5;
    border-bottom: 2px solid transparent; }
QTabBar::tab:selected { color: #a2e9bc; border-bottom: 2px solid #65ce91; }
QScrollArea { background: transparent; border: none; }
QScrollBar:vertical { background: transparent; width: 8px; margin: 2px; }
QScrollBar::handle:vertical { background: #3b5361; border-radius: 3px; min-height: 28px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: transparent; height: 8px; }
QScrollBar::handle:horizontal { background: #3b5361; border-radius: 3px; min-width: 28px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QFrame#Footer { background: #0e171e; border-top: 1px solid #293944; }
QLabel#Notice { color: #b6c8d2; font-size: 8pt; }
QLabel#Step { color: #8097a6; padding: 5px 3px; border-bottom: 2px solid #2c3e49; }
QLabel#Step[active="true"] { color: #a3eaba; border-color: #64cb8e; }
QLabel#Review { background: #14222c; padding: 12px; border: 1px solid #344953; border-radius: 6px; }
"""


def apply_theme():
    app = QApplication.instance()
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 9))
    palette = QPalette()
    for role, value in (
        (QPalette.Window, "#0c151c"),
        (QPalette.Base, "#14222c"),
        (QPalette.AlternateBase, "#192933"),
        (QPalette.Button, "#22343f"),
        (QPalette.WindowText, "#e2eaf0"),
        (QPalette.Text, "#e2eaf0"),
        (QPalette.ButtonText, "#e2eaf0"),
        (QPalette.Highlight, "#28593f"),
        (QPalette.HighlightedText, "#f3fff7"),
        (QPalette.ToolTipBase, "#20313c"),
        (QPalette.ToolTipText, "#e2eaf0"),
    ):
        palette.setColor(role, QColor(value))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#748992"))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#748992"))
    app.setPalette(palette)


def label(text="", name=None):
    widget = QLabel(text)
    widget.setTextFormat(Qt.PlainText)
    if name:
        widget.setObjectName(name)
    widget.setWordWrap(True)
    return widget


def action(text, callback, layout=None, image=None, variant=None):
    widget = QPushButton(text)
    if image:
        widget.setIcon(icon(image))
    if variant:
        widget.setProperty("variant", variant)
    widget.clicked.connect(callback)
    if layout:
        layout.addWidget(widget)
    return widget


def error_for(widget, message=""):
    widget.setProperty("invalid", bool(message))
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    if hasattr(widget, "validation_label"):
        widget.validation_label.setText(message)
        widget.validation_label.setVisible(bool(message))
    if message:
        widget.setFocus()
    return not message


def input_field(placeholder="", secret=False):
    widget = QLineEdit()
    widget.setPlaceholderText(placeholder)
    if secret:
        widget.setEchoMode(QLineEdit.Password)
    widget.validation_label = label("", "FieldError")
    widget.validation_label.hide()
    widget.textEdited.connect(lambda _: error_for(widget))
    return widget


def field(form, title, placeholder="", secret=False):
    widget = input_field(placeholder, secret)
    wrapper = QWidget()
    body = QVBoxLayout(wrapper)
    body.setContentsMargins(0, 0, 0, 0)
    body.setSpacing(3)
    body.addWidget(widget)
    body.addWidget(widget.validation_label)
    caption = label(title)
    caption.setBuddy(widget)
    form.addRow(caption, wrapper)
    return widget


def inline_input(layout, placeholder):
    wrapper = QWidget()
    body = QVBoxLayout(wrapper)
    body.setContentsMargins(0, 0, 0, 0)
    body.setSpacing(3)
    widget = input_field(placeholder)
    body.addWidget(widget)
    body.addWidget(widget.validation_label)
    layout.addWidget(wrapper, 1)
    return widget


def form_layout(parent):
    form = QFormLayout(parent)
    form.setRowWrapPolicy(QFormLayout.WrapLongRows)
    form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
    form.setHorizontalSpacing(14)
    form.setVerticalSpacing(10)
    return form


class Page(QWidget):
    def __init__(self, title, description):
        super().__init__()
        self.setObjectName("Page")
        self.body = QVBoxLayout(self)
        self.body.setContentsMargins(18, 16, 18, 16)
        self.body.setSpacing(12)
        self.body.addWidget(label(title, "PageTitle"))
        self.body.addWidget(label(description, "Description"))


class Card(QFrame):
    def __init__(self, title=None, description=None):
        super().__init__()
        self.setObjectName("Card")
        self.body = QVBoxLayout(self)
        self.body.setContentsMargins(14, 12, 14, 12)
        self.body.setSpacing(10)
        if title:
            self.body.addWidget(label(title, "CardTitle"))
        if description:
            self.body.addWidget(label(description, "Description"))


class RecordTable(QTableWidget):
    """Read-only compact rows with records bound to IDs, never displayed text."""

    currentRowChanged = Signal(int)

    def __init__(self, columns):
        super().__init__(0, len(columns))
        self.setHorizontalHeaderLabels(columns)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.verticalHeader().hide()
        self.verticalHeader().setDefaultSectionSize(28)
        self.horizontalHeader().setMinimumSectionSize(70)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.currentCellChanged.connect(
            lambda row, col, old, old_col: self.currentRowChanged.emit(row) if row != old else None
        )

    def replace(self, rows):
        previous = self.currentItem().data(Qt.UserRole) if self.currentItem() else None
        previous_id = previous.get("id") if isinstance(previous, dict) else previous
        self.blockSignals(True)
        self.setRowCount(0)
        for record, values in rows:
            row = self.rowCount()
            self.insertRow(row)
            for column, value in enumerate(values):
                cell = QTableWidgetItem(str(value))
                cell.setToolTip(str(value))
                cell.setData(Qt.UserRole, record)
                self.setItem(row, column, cell)
        selected = next(
            (
                row
                for row in range(self.rowCount())
                if (
                    self.item(row).data(Qt.UserRole).get("id")
                    if isinstance(self.item(row).data(Qt.UserRole), dict)
                    else self.item(row).data(Qt.UserRole)
                )
                == previous_id
            ),
            -1,
        )
        if selected >= 0:
            self.setCurrentRow(selected)
        self.blockSignals(False)

    def count(self):
        return self.rowCount()

    def clear(self):
        self.setRowCount(0)

    def item(self, row, column=0):
        return super().item(row, column)

    def currentItem(self):
        return self.item(self.currentRow()) if self.currentRow() >= 0 else None

    def setCurrentRow(self, row):
        self.setCurrentCell(row, 0)
        self.selectRow(row)


def toolbar(*widgets):
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(7)
    for widget in widgets:
        row.addWidget(widget)
    return row


class FlowLayout(QLayout):
    """Wrap contextual actions instead of forcing horizontal overflow."""

    def __init__(self):
        super().__init__()
        self.items = []
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(7)

    def addItem(self, item):
        self.items.append(item)

    def count(self):
        return len(self.items)

    def itemAt(self, index):
        return self.items[index] if index < len(self.items) else None

    def takeAt(self, index):
        return self.items.pop(index) if index < len(self.items) else None

    def addStretch(self, stretch=0):
        pass

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.arrange(QRect(0, 0, width, 0), False)

    def minimumSize(self):
        size = QSize()
        for item in self.items:
            size = size.expandedTo(item.minimumSize())
        return size

    def sizeHint(self):
        return self.minimumSize()

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.arrange(rect, True)

    def arrange(self, rect, apply):
        x, y, height = rect.x(), rect.y(), 0
        for item in self.items:
            size = item.sizeHint()
            if x + size.width() > rect.right() + 1 and height:
                x = rect.x()
                y += height + self.spacing()
                height = 0
            if apply:
                item.setGeometry(QRect(QPoint(x, y), size))
            x += size.width() + self.spacing()
            height = max(height, size.height())
        return y + height - rect.y()
