from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton,
    QGroupBox, QFormLayout, QColorDialog, QFrame
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, Slot

from src.constants import MIN_STROKE_WIDTH, MAX_STROKE_WIDTH
from src.logic.shapes import Shape
from src.logic.commands import (
    ChangeStrokeColorCommand,
    ChangeFillColorCommand,
    ChangeStrokeWidthCommand,
)


class ColorButton(QPushButton):
    def __init__(self, color=None, parent=None):
        super().__init__(parent)
        if color is None:
            color = QColor(0, 0, 0)
        self._color = QColor(color)
        self.setFixedSize(60, 28)
        self._sync()

    def _sync(self):
        self.setStyleSheet(
            f"background-color: {self._color.name()}; border: 1px solid #777; border-radius: 3px;"
        )

    @property
    def color(self):
        return QColor(self._color)

    @color.setter
    def color(self, c):
        self._color = QColor(c)
        self._sync()


class PropertiesPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.undo_stack = None
        self.items = []
        self._updating = False

        self._ui()
        self._connect()
        self._enable(False)

    def set_undo_stack(self, stack):
        self.undo_stack = stack

    def _ui(self):
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("Свойства")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        lay.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        lay.addWidget(line)

        gstroke = QGroupBox("Обводка")
        fstroke = QFormLayout(gstroke)

        self.w_spin = QSpinBox()
        self.w_spin.setRange(MIN_STROKE_WIDTH, MAX_STROKE_WIDTH)
        fstroke.addRow("Толщина:", self.w_spin)

        hb1 = QHBoxLayout()
        self.stroke_btn = ColorButton()
        hb1.addWidget(self.stroke_btn)
        hb1.addStretch()
        fstroke.addRow("Цвет:", hb1)

        lay.addWidget(gstroke)

        gfill = QGroupBox("Заливка")
        ffill = QFormLayout(gfill)

        hb2 = QHBoxLayout()
        self.fill_btn = ColorButton()
        hb2.addWidget(self.fill_btn)
        hb2.addStretch()
        ffill.addRow("Цвет:", hb2)

        lay.addWidget(gfill)

        self.info = QLabel("Выделено: 0")
        self.info.setStyleSheet("color: #666;")
        lay.addWidget(self.info)

        lay.addStretch()
        self.setMinimumWidth(220)

    def _connect(self):
        self.w_spin.valueChanged.connect(self._on_width)
        self.stroke_btn.clicked.connect(self._on_stroke_color)
        self.fill_btn.clicked.connect(self._on_fill_color)

    def _enable(self, ok):
        self.w_spin.setEnabled(ok)
        self.stroke_btn.setEnabled(ok)
        self.fill_btn.setEnabled(ok)

    @Slot()
    def on_selection_changed(self):
        from PySide6.QtWidgets import QGraphicsScene

        sc = self.sender()
        if not isinstance(sc, QGraphicsScene):
            return

        sel = sc.selectedItems()
        self.items = [it for it in sel if isinstance(it, Shape)]
        self.info.setText(f"Выделено: {len(self.items)}")

        if not self.items:
            self._enable(False)
            return

        self._enable(True)
        self._refresh()

    def _refresh(self):
        if not self.items:
            return

        self._updating = True
        first = self.items[0]
        self.w_spin.setValue(int(first.get_stroke_width()))
        self.stroke_btn.color = first.get_stroke_color()
        self.fill_btn.color = first.get_fill_color()
        self._updating = False

    def _on_width(self, v):
        if self._updating or not self.items or self.undo_stack is None:
            return

        self.undo_stack.beginMacro("Change width")
        for it in self.items:
            old = it.get_stroke_width()
            if int(old) != int(v):
                self.undo_stack.push(ChangeStrokeWidthCommand(it, old, v))
        self.undo_stack.endMacro()

    def _on_stroke_color(self):
        if not self.items or self.undo_stack is None:
            return

        c0 = self.stroke_btn.color
        c = QColorDialog.getColor(c0, self, "Цвет обводки", QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if not c.isValid():
            return

        self.stroke_btn.color = c

        self.undo_stack.beginMacro("Stroke color")
        for it in self.items:
            self.undo_stack.push(ChangeStrokeColorCommand(it, it.get_stroke_color(), c))
        self.undo_stack.endMacro()

    def _on_fill_color(self):
        if not self.items or self.undo_stack is None:
            return

        c0 = self.fill_btn.color
        c = QColorDialog.getColor(c0, self, "Цвет заливки", QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if not c.isValid():
            return

        self.fill_btn.color = c

        self.undo_stack.beginMacro("Fill color")
        for it in self.items:
            self.undo_stack.push(ChangeFillColorCommand(it, it.get_fill_color(), c))
        self.undo_stack.endMacro()