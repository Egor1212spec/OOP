from PySide6.QtWidgets import QGraphicsView, QGraphicsItem
from PySide6.QtCore import QPointF, Qt

from src.constants import ShapeType, ToolType, MIN_SHAPE_SIZE
from src.constants import DEFAULT_STROKE_COLOR, DEFAULT_FILL_COLOR, DEFAULT_STROKE_WIDTH
from src.logic.factory import ShapeFactory
from src.logic.commands import AddShapeCommand, MoveCommand


class Tool:
    def __init__(self, canvas):
        self.canvas = canvas

    @property
    def scene(self):
        return self.canvas.scene()

    def activate(self):
        pass

    def deactivate(self):
        pass

    def mouse_press(self, event):
        pass

    def mouse_move(self, event):
        pass

    def mouse_release(self, event):
        pass


class SelectionTool(Tool):
    def __init__(self, canvas):
        super().__init__(canvas)
        self._moving = False
        self._start_pos = {}

    def activate(self):
        self.canvas.setCursor(Qt.CursorShape.ArrowCursor)
        self.canvas.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

    def deactivate(self):
        self.canvas.setDragMode(QGraphicsView.DragMode.NoDrag)
        self._moving = False
        self._start_pos.clear()

    def mouse_press(self, event):
        self._start_pos = {}
        for it in self.scene.selectedItems():
            self._start_pos[it] = QPointF(it.pos())
        self._moving = True

    def mouse_release(self, event):
        if not self._moving or not self._start_pos:
            return

        moved = []
        for it, old in self._start_pos.items():
            new = QPointF(it.pos())
            if new != old:
                moved.append((it, old, new))

        if moved:
            if len(moved) > 1:
                self.canvas.undo_stack.beginMacro("Move selected")
            for it, old, new in moved:
                self.canvas.undo_stack.push(MoveCommand(it, old, new))
            if len(moved) > 1:
                self.canvas.undo_stack.endMacro()

        self._moving = False
        self._start_pos.clear()


class CreationTool(Tool):
    def __init__(self, canvas, shape_type):
        super().__init__(canvas)
        self.shape_type = shape_type
        self._tmp = None
        self._start = None
        self._drawing = False

    def activate(self):
        self.canvas.setCursor(Qt.CursorShape.CrossCursor)
        self.canvas.setDragMode(QGraphicsView.DragMode.NoDrag)

    def deactivate(self):
        if self._tmp is not None and self._drawing:
            try:
                self.scene.removeItem(self._tmp)
            except Exception:
                pass
        self._tmp = None
        self._start = None
        self._drawing = False

    def mouse_press(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        self.scene.clearSelection()

        self._start = self.canvas.mapToScene(event.pos())
        self._tmp = ShapeFactory.create(
            self.shape_type,
            DEFAULT_STROKE_COLOR,
            DEFAULT_FILL_COLOR,
            DEFAULT_STROKE_WIDTH,
        )
        if self._tmp is None:
            return

        if isinstance(self._tmp, QGraphicsItem):
            self._tmp.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
            self._tmp.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
            self._tmp.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
            self.scene.addItem(self._tmp)

        self._drawing = True

    def mouse_move(self, event):
        if not self._drawing or self._tmp is None:
            return
        p = self.canvas.mapToScene(event.pos())
        self._tmp.set_geometry(self._start, p)

    def mouse_release(self, event):
        if not self._drawing or self._tmp is None:
            return

        end = self.canvas.mapToScene(event.pos())
        dx = abs(end.x() - self._start.x())
        dy = abs(end.y() - self._start.y())

        if isinstance(self._tmp, QGraphicsItem):
            self.scene.removeItem(self._tmp)

        if dx >= MIN_SHAPE_SIZE or dy >= MIN_SHAPE_SIZE:
            if isinstance(self._tmp, QGraphicsItem):
                self._tmp.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
                self._tmp.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
                self._tmp.setAcceptedMouseButtons(Qt.MouseButton.AllButtons)

            self.canvas.undo_stack.push(AddShapeCommand(self.scene, self._tmp))

        self.scene.clearSelection()

        self._tmp = None
        self._start = None
        self._drawing = False


class ToolManager:
    def __init__(self, canvas):
        self.canvas = canvas
        self.current = None
        self.tools = {
            ToolType.SELECTION: SelectionTool(canvas),
            ToolType.RECTANGLE: CreationTool(canvas, ShapeType.RECTANGLE),
            ToolType.ELLIPSE: CreationTool(canvas, ShapeType.ELLIPSE),
            ToolType.LINE: CreationTool(canvas, ShapeType.LINE),
        }

    def set_tool(self, tool_type):
        if self.current is not None:
            self.current.deactivate()
        self.current = self.tools.get(tool_type)
        if self.current is not None:
            self.current.activate()

    def mouse_press(self, event):
        if self.current is not None:
            self.current.mouse_press(event)

    def mouse_move(self, event):
        if self.current is not None:
            self.current.mouse_move(event)

    def mouse_release(self, event):
        if self.current is not None:
            self.current.mouse_release(event)