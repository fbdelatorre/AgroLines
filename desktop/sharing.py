"""Five-step sharing flow, with an explicit review before submitting."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QStackedWidget, QVBoxLayout, QWidget

from desktop.ui import action, label


class SharingFlow(QWidget):
    def __init__(self, pages, validate, entered, submit):
        super().__init__()
        self.validate = validate
        self.entered = entered
        self.stack = QStackedWidget()
        self.steps = []
        body = QVBoxLayout(self)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(16)
        heading = QHBoxLayout()
        for number, title in enumerate(
            ("Propriedade", "Destinatário", "Perfil", "Escopo", "Confirmar")
        ):
            step = label(f"{number + 1}  {title}", "Step")
            step.setAlignment(Qt.AlignCenter)
            heading.addWidget(step, 1)
            self.steps.append(step)
        body.addLayout(heading)
        for page in pages:
            self.stack.addWidget(page)
        body.addWidget(self.stack)
        controls = QHBoxLayout()
        self.back_button = action("Voltar", self.back, controls)
        controls.addStretch()
        self.next_button = action("Continuar", self.next, controls, variant="primary")
        self.submit_button = action("Enviar convite", submit, controls, "mail", "primary")
        body.addLayout(controls)
        self.show_step(0)

    def currentIndex(self):
        return self.stack.currentIndex()

    def show_step(self, index):
        self.stack.setCurrentIndex(index)
        for number, step in enumerate(self.steps):
            step.setProperty("active", number == index)
            step.style().unpolish(step)
            step.style().polish(step)
        self.back_button.setEnabled(index > 0)
        self.next_button.setVisible(index < 4)
        self.submit_button.setVisible(index == 4)
        self.entered(index)

    def next(self):
        index = self.currentIndex()
        if index < 4 and self.validate(index):
            self.show_step(index + 1)

    def back(self):
        self.show_step(max(0, self.currentIndex() - 1))
