from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QToolBar, QToolButton,
    QStatusBar, QFileDialog, QMessageBox, QSplitter
)
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Qt

from src.constants import ToolType, FILE_EXTENSION
from src.widgets.canvas import EditorCanvas
from src.widgets.properties import PropertiesPanel
from src.logic.strategies import DocumentManager
from src.logic.commands import GroupCommand, UngroupCommand
from src.logic.shapes import GroupShape


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self._file = None

        self.setWindowTitle("Vector Editor")
        self.resize(1200, 800)

        self._central = QWidget()
        self.setCentralWidget(self._central)

        self.canvas = EditorCanvas()
        self.props = PropertiesPanel()
        self.props.set_undo_stack(self.canvas.undo_stack)

        self.doc = DocumentManager(self.canvas.scene())

        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage("Готово")

        self._actions()
        self._menu()
        self._toolbar()
        self._layout()
        self._connect()

        self._update_title()

    def _actions(self):
        self.act_new = QAction("Новый", self)
        self.act_new.setShortcut(QKeySequence.StandardKey.New)
        self.act_new.triggered.connect(self.on_new)

        self.act_open = QAction("Открыть...", self)
        self.act_open.setShortcut(QKeySequence.StandardKey.Open)
        self.act_open.triggered.connect(self.on_open)

        self.act_save = QAction("Сохранить", self)
        self.act_save.setShortcut(QKeySequence.StandardKey.Save)
        self.act_save.triggered.connect(self.on_save)

        self.act_save_as = QAction("Сохранить как...", self)
        self.act_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.act_save_as.triggered.connect(self.on_save_as)

        self.act_export = QAction("Экспорт...", self)
        self.act_export.setShortcut("Ctrl+E")
        self.act_export.triggered.connect(self.on_export)

        self.act_exit = QAction("Выход", self)
        self.act_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self.act_exit.triggered.connect(self.close)

        self.act_undo = self.canvas.undo_stack.createUndoAction(self, "Отменить")
        self.act_undo.setShortcut(QKeySequence.StandardKey.Undo)

        self.act_redo = self.canvas.undo_stack.createRedoAction(self, "Повторить")
        self.act_redo.setShortcut(QKeySequence.StandardKey.Redo)

        self.act_delete = QAction("Удалить", self)
        self.act_delete.setShortcut(QKeySequence.StandardKey.Delete)
        self.act_delete.triggered.connect(self.canvas.delete_selected)

        self.act_group = QAction("Группировать", self)
        self.act_group.setShortcut("Ctrl+G")
        self.act_group.triggered.connect(self.on_group)

        self.act_ungroup = QAction("Разгруппировать", self)
        self.act_ungroup.setShortcut("Ctrl+U")
        self.act_ungroup.triggered.connect(self.on_ungroup)

    def _menu(self):
        mb = self.menuBar()

        m_file = mb.addMenu("Файл")
        m_file.addAction(self.act_new)
        m_file.addAction(self.act_open)
        m_file.addSeparator()
        m_file.addAction(self.act_save)
        m_file.addAction(self.act_save_as)
        m_file.addSeparator()
        m_file.addAction(self.act_export)
        m_file.addSeparator()
        m_file.addAction(self.act_exit)

        m_edit = mb.addMenu("Правка")
        m_edit.addAction(self.act_undo)
        m_edit.addAction(self.act_redo)
        m_edit.addSeparator()
        m_edit.addAction(self.act_delete)
        m_edit.addSeparator()
        m_edit.addAction(self.act_group)
        m_edit.addAction(self.act_ungroup)

    def _toolbar(self):
        tb = QToolBar("Tools")
        tb.setMovable(False)
        tb.setOrientation(Qt.Orientation.Vertical)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, tb)

        self.btn_sel = QToolButton()
        self.btn_sel.setText("↖")
        self.btn_sel.setCheckable(True)
        self.btn_sel.setChecked(True)

        self.btn_rect = QToolButton()
        self.btn_rect.setText("▢")
        self.btn_rect.setCheckable(True)

        self.btn_ell = QToolButton()
        self.btn_ell.setText("◯")
        self.btn_ell.setCheckable(True)

        self.btn_line = QToolButton()
        self.btn_line.setText("╱")
        self.btn_line.setCheckable(True)

        for b in [self.btn_sel, self.btn_rect, self.btn_ell, self.btn_line]:
            tb.addWidget(b)
            b.setFixedSize(40, 40)

    def _layout(self):
        sp = QSplitter(Qt.Orientation.Horizontal)
        sp.addWidget(self.canvas)
        sp.addWidget(self.props)
        sp.setStretchFactor(0, 4)
        sp.setStretchFactor(1, 1)

        lay = QHBoxLayout(self._central)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(sp)

    def _connect(self):
        self.canvas.scene().selectionChanged.connect(self.props.on_selection_changed)
        self.canvas.undo_stack.cleanChanged.connect(lambda _: self._update_title())

        def set_checked(btn):
            for b in [self.btn_sel, self.btn_rect, self.btn_ell, self.btn_line]:
                b.blockSignals(True)
                b.setChecked(b is btn)
                b.blockSignals(False)

        self.btn_sel.clicked.connect(lambda: (set_checked(self.btn_sel), self.canvas.set_tool(ToolType.SELECTION)))
        self.btn_rect.clicked.connect(lambda: (set_checked(self.btn_rect), self.canvas.set_tool(ToolType.RECTANGLE)))
        self.btn_ell.clicked.connect(lambda: (set_checked(self.btn_ell), self.canvas.set_tool(ToolType.ELLIPSE)))
        self.btn_line.clicked.connect(lambda: (set_checked(self.btn_line), self.canvas.set_tool(ToolType.LINE)))

    def _update_title(self):
        name = "Новый"
        if self._file:
            name = self._file.name
        if not self.canvas.undo_stack.isClean():
            name = "*" + name
        self.setWindowTitle(f"{name} - Vector Editor")

    def _maybe_save(self):
        if self.canvas.undo_stack.isClean():
            return True

        r = QMessageBox.question(
            self,
            "Сохранить?",
            "Есть изменения. Сохранить?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )

        if r == QMessageBox.StandardButton.Save:
            self.on_save()
            return self.canvas.undo_stack.isClean()
        if r == QMessageBox.StandardButton.Discard:
            return True
        return False

    def on_new(self):
        if not self._maybe_save():
            return
        self.canvas.clear_all()
        self._file = None
        self._update_title()

    def on_open(self):
        if not self._maybe_save():
            return

        fp, _ = QFileDialog.getOpenFileName(self, "Открыть", "", self.doc.save_filter())
        if not fp:
            return

        ok = self.doc.load_json(fp)
        if not ok:
            QMessageBox.critical(self, "Ошибка", "Не получилось открыть файл")
            return

        self.canvas.undo_stack.clear()
        self.canvas.undo_stack.setClean()
        self._file = Path(fp)
        self._update_title()

    def on_save(self):
        if self._file is None:
            self.on_save_as()
            return
        if self.doc.save_json(str(self._file)):
            self.canvas.undo_stack.setClean()
            self._update_title()
        else:
            QMessageBox.critical(self, "Ошибка", "Не получилось сохранить")

    def on_save_as(self):
        fp, _ = QFileDialog.getSaveFileName(self, "Сохранить как", "", self.doc.save_filter())
        if not fp:
            return

        p = Path(fp)
        if p.suffix == "":
            p = p.with_suffix(FILE_EXTENSION)

        if self.doc.save_json(str(p)):
            self._file = p
            self.canvas.undo_stack.setClean()
            self._update_title()
        else:
            QMessageBox.critical(self, "Ошибка", "Не получилось сохранить")

    def on_export(self):
        fp, _ = QFileDialog.getSaveFileName(self, "Экспорт", "", self.doc.export_filter())
        if not fp:
            return

        p = Path(fp)
        if p.suffix == "":
            p = p.with_suffix(".png")

        if not self.doc.export_image(str(p)):
            QMessageBox.critical(self, "Ошибка", "Не получилось экспортировать")

    def on_group(self):
        sel = self.canvas.scene().selectedItems()
        if len(sel) < 2:
            return
        self.canvas.undo_stack.push(GroupCommand(self.canvas.scene(), sel))
        self.canvas.scene().clearSelection()

    def on_ungroup(self):
        sel = self.canvas.scene().selectedItems()
        groups = [it for it in sel if isinstance(it, GroupShape)]
        if not groups:
            return

        if len(groups) > 1:
            self.canvas.undo_stack.beginMacro("Ungroup")
        for g in groups:
            self.canvas.undo_stack.push(UngroupCommand(self.canvas.scene(), g))
        if len(groups) > 1:
            self.canvas.undo_stack.endMacro()

        self.canvas.scene().clearSelection()

    def closeEvent(self, event):
        if self._maybe_save():
            event.accept()
        else:
            event.ignore()