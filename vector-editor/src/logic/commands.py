from PySide6.QtGui import QUndoCommand, QColor
from PySide6.QtCore import QPointF

from src.logic.shapes import GroupShape


class AddShapeCommand(QUndoCommand):
    def __init__(self, scene, item, text="Add", parent=None):
        super().__init__(text, parent)
        self.scene = scene
        self.item = item

    def redo(self):
        self.scene.clearSelection()
        self.scene.addItem(self.item)
        try:
            self.item.setSelected(False)
        except Exception:
            pass

    def undo(self):
        self.scene.removeItem(self.item)


class DeleteShapeCommand(QUndoCommand):
    def __init__(self, scene, item, text="Delete", parent=None):
        super().__init__(text, parent)
        self.scene = scene
        self.item = item

    def redo(self):
        self.scene.removeItem(self.item)

    def undo(self):
        self.scene.addItem(self.item)


class MoveCommand(QUndoCommand):
    def __init__(self, item, old_pos, new_pos, text="Move", parent=None):
        super().__init__(text, parent)
        self.item = item
        self.old_pos = QPointF(old_pos)
        self.new_pos = QPointF(new_pos)

    def redo(self):
        self.item.setPos(self.new_pos)

    def undo(self):
        self.item.setPos(self.old_pos)

    def id(self):
        return 1001

    def mergeWith(self, other):
        if not isinstance(other, MoveCommand):
            return False
        if other.item is not self.item:
            return False
        self.new_pos = QPointF(other.new_pos)
        return True


class ChangeStrokeColorCommand(QUndoCommand):
    def __init__(self, item, old_color, new_color, text="Stroke", parent=None):
        super().__init__(text, parent)
        self.item = item
        self.old = QColor(old_color)
        self.new = QColor(new_color)

    def redo(self):
        self.item.set_stroke_color(self.new)

    def undo(self):
        self.item.set_stroke_color(self.old)


class ChangeFillColorCommand(QUndoCommand):
    def __init__(self, item, old_color, new_color, text="Fill", parent=None):
        super().__init__(text, parent)
        self.item = item
        self.old = QColor(old_color)
        self.new = QColor(new_color)

    def redo(self):
        self.item.set_fill_color(self.new)

    def undo(self):
        self.item.set_fill_color(self.old)


class ChangeStrokeWidthCommand(QUndoCommand):
    def __init__(self, item, old_w, new_w, text="Width", parent=None):
        super().__init__(text, parent)
        self.item = item
        self.old = int(old_w)
        self.new = int(new_w)

    def redo(self):
        self.item.set_stroke_width(self.new)

    def undo(self):
        self.item.set_stroke_width(self.old)

    def id(self):
        return 1002

    def mergeWith(self, other):
        if not isinstance(other, ChangeStrokeWidthCommand):
            return False
        if other.item is not self.item:
            return False
        self.new = int(other.new)
        return True


class GroupCommand(QUndoCommand):
    def __init__(self, scene, items, text="Group", parent=None):
        super().__init__(text, parent)
        self.scene = scene
        self.items = list(items)
        self.group = GroupShape()

    def redo(self):
        self.scene.clearSelection()
        self.scene.addItem(self.group)
        for it in self.items:
            self.group.addToGroup(it)
        self.group.setSelected(False)

    def undo(self):
        for it in self.items:
            try:
                self.group.removeFromGroup(it)
            except Exception:
                pass
            if it.scene() is None:
                self.scene.addItem(it)
        self.scene.removeItem(self.group)


class UngroupCommand(QUndoCommand):
    def __init__(self, scene, group, text="Ungroup", parent=None):
        super().__init__(text, parent)
        self.scene = scene
        self.group = group
        self.items = []

    def redo(self):
        if not isinstance(self.group, GroupShape):
            return
        self.scene.clearSelection()
        self.items = list(self.group.childItems())
        for it in self.items:
            self.group.removeFromGroup(it)
            if it.scene() is None:
                self.scene.addItem(it)
        self.scene.removeItem(self.group)

    def undo(self):
        if not isinstance(self.group, GroupShape):
            return
        self.scene.clearSelection()
        self.scene.addItem(self.group)
        for it in self.items:
            self.group.addToGroup(it)