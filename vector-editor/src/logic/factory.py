from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsItem

from src.constants import ShapeType, DEFAULT_STROKE_COLOR, DEFAULT_FILL_COLOR, DEFAULT_STROKE_WIDTH
from src.logic.shapes import RectangleShape, EllipseShape, LineShape, GroupShape


class ShapeFactory:
    @staticmethod
    def create(shape_type, stroke_color=DEFAULT_STROKE_COLOR, fill_color=DEFAULT_FILL_COLOR, stroke_width=DEFAULT_STROKE_WIDTH):
        if shape_type == ShapeType.RECTANGLE:
            return RectangleShape(stroke_color, fill_color, stroke_width)
        if shape_type == ShapeType.ELLIPSE:
            return EllipseShape(stroke_color, fill_color, stroke_width)
        if shape_type == ShapeType.LINE:
            return LineShape(stroke_color, fill_color, stroke_width)
        return None

    @staticmethod
    def from_dict(d):
        try:
            t = ShapeType[d.get("type", "")]
        except Exception:
            return None

        if t == ShapeType.GROUP:
            return ShapeFactory._group_from_dict(d)

        stroke_color = QColor(d.get("stroke_color", DEFAULT_STROKE_COLOR.name()))
        fill_color = QColor(d.get("fill_color", DEFAULT_FILL_COLOR.name()))
        stroke_width = int(d.get("stroke_width", DEFAULT_STROKE_WIDTH))

        sh = ShapeFactory.create(t, stroke_color, fill_color, stroke_width)
        if sh is None:
            return None

        start = QPointF(float(d.get("start_x", 0)), float(d.get("start_y", 0)))
        end = QPointF(float(d.get("end_x", 0)), float(d.get("end_y", 0)))
        sh.set_geometry(start, end)

        if isinstance(sh, QGraphicsItem):
            sh.setPos(float(d.get("x", 0)), float(d.get("y", 0)))

        return sh

    @staticmethod
    def _group_from_dict(d):
        g = GroupShape()
        g.setPos(float(d.get("x", 0)), float(d.get("y", 0)))

        for cd in d.get("children", []):
            ch = ShapeFactory.from_dict(cd)
            if ch is not None and isinstance(ch, QGraphicsItem):
                g.addToGroup(ch)

        return g