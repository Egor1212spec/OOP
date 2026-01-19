from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QFrame
from PySide6.QtGui import QPainter, QUndoStack
from PySide6.QtCore import Qt

from src.constants import CANVAS_WIDTH, CANVAS_HEIGHT, DEFAULT_BACKGROUND_COLOR, ToolType
from src.logic.tools import ToolManager
from src.logic.commands import DeleteShapeCommand


class EditorScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)
        self.setBackgroundBrush(DEFAULT_BACKGROUND_COLOR)


class EditorCanvas(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._scene = EditorScene(self)
        self.setScene(self._scene)

        self._undo_stack = QUndoStack(self)

        self._tool_type = ToolType.SELECTION
        self._tool_manager = ToolManager(self)
        self._tool_manager.set_tool(ToolType.SELECTION)

        self._setup()

    def _setup(self):
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("QGraphicsView { border: none; } QGraphicsView:focus { outline: none; }")

    @property
    def undo_stack(self):
        return self._undo_stack

    def set_tool(self, tool_type):
        self._tool_type = tool_type
        self._tool_manager.set_tool(tool_type)
        if tool_type != ToolType.SELECTION:
            self._scene.clearSelection()

    def mousePressEvent(self, event):
        if self._tool_type == ToolType.SELECTION:
            super().mousePressEvent(event)
            self._tool_manager.mouse_press(event)
        else:
            self._tool_manager.mouse_press(event)
            event.accept()

    def mouseMoveEvent(self, event):
        if self._tool_type == ToolType.SELECTION:
            super().mouseMoveEvent(event)
            self._tool_manager.mouse_move(event)
        else:
            self._tool_manager.mouse_move(event)
            event.accept()

    def mouseReleaseEvent(self, event):
        if self._tool_type == ToolType.SELECTION:
            super().mouseReleaseEvent(event)
            self._tool_manager.mouse_release(event)
        else:
            self._tool_manager.mouse_release(event)
            event.accept()

        self.viewport().update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selected()
            event.accept()
            return
        super().keyPressEvent(event)

    def delete_selected(self):
        items = self._scene.selectedItems()
        if not items:
            return

        self._undo_stack.beginMacro("Delete selected")
        for it in items:
            self._undo_stack.push(DeleteShapeCommand(self._scene, it))
        self._undo_stack.endMacro()

    def clear_all(self):
        self._scene.clear()
        self._undo_stack.clear()