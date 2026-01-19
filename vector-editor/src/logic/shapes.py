from PySide6.QtWidgets import (
    QGraphicsPathItem,
    QGraphicsItemGroup,
    QGraphicsItem,
    QStyleOptionGraphicsItem,
    QStyle,
)
from PySide6.QtGui import QPainterPath, QPen, QBrush, QColor
from PySide6.QtCore import QPointF, QRectF, Qt

from src.constants import (
    ShapeType,
    DEFAULT_FILL_COLOR,
    DEFAULT_STROKE_COLOR,
    DEFAULT_STROKE_WIDTH,
)


class Shape:
    @property
    def type_name(self):
        raise NotImplementedError

    def to_dict(self):
        raise NotImplementedError

    def set_geometry(self, start, end):
        raise NotImplementedError

    def set_stroke_color(self, color):
        raise NotImplementedError

    def get_stroke_color(self):
        raise NotImplementedError

    def set_fill_color(self, color):
        raise NotImplementedError

    def get_fill_color(self):
        raise NotImplementedError

    def set_stroke_width(self, width):
        raise NotImplementedError

    def get_stroke_width(self):
        raise NotImplementedError


class BaseShape(QGraphicsPathItem, Shape):
    def __init__(self, stroke_color=None, fill_color=None, stroke_width=None, parent=None):
        QGraphicsPathItem.__init__(self, parent)

        if stroke_color is None:
            stroke_color = DEFAULT_STROKE_COLOR
        if fill_color is None:
            fill_color = DEFAULT_FILL_COLOR
        if stroke_width is None:
            stroke_width = DEFAULT_STROKE_WIDTH

        self._stroke_color = QColor(stroke_color)
        self._fill_color = QColor(fill_color)
        self._stroke_width = int(stroke_width)

        self._start = QPointF()
        self._end = QPointF()

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self._sync()

    def paint(self, painter, option, widget=None):
        opt = QStyleOptionGraphicsItem(option)
        opt.state &= ~QStyle.StateFlag.State_Selected
        opt.state &= ~QStyle.StateFlag.State_HasFocus
        QGraphicsPathItem.paint(self, painter, opt, widget)

    def _sync(self):
        pen = QPen(self._stroke_color)
        pen.setWidth(self._stroke_width)
        self.setPen(pen)
        self.setBrush(QBrush(self._fill_color))

    def _create_path(self):
        raise NotImplementedError

    def set_geometry(self, start, end):
        self._start = QPointF(start)
        self._end = QPointF(end)
        self.setPath(self._create_path())

    def set_stroke_color(self, color):
        self._stroke_color = QColor(color)
        self._sync()

    def get_stroke_color(self):
        return QColor(self._stroke_color)

    def set_fill_color(self, color):
        self._fill_color = QColor(color)
        self._sync()

    def get_fill_color(self):
        return QColor(self._fill_color)

    def set_stroke_width(self, width):
        self._stroke_width = int(width)
        self._sync()

    def get_stroke_width(self):
        return int(self._stroke_width)

    def _base_dict(self):
        p = self.pos()
        return {
            "type": self.type_name.name,
            "x": float(p.x()),
            "y": float(p.y()),
            "start_x": float(self._start.x()),
            "start_y": float(self._start.y()),
            "end_x": float(self._end.x()),
            "end_y": float(self._end.y()),
            "stroke_color": self._stroke_color.name(QColor.NameFormat.HexArgb),
            "fill_color": self._fill_color.name(QColor.NameFormat.HexArgb),
            "stroke_width": int(self._stroke_width),
        }


class RectangleShape(BaseShape):
    @property
    def type_name(self):
        return ShapeType.RECTANGLE

    def _create_path(self):
        path = QPainterPath()
        r = QRectF(self._start, self._end).normalized()
        path.addRect(r)
        return path

    def to_dict(self):
        return self._base_dict()


class EllipseShape(BaseShape):
    @property
    def type_name(self):
        return ShapeType.ELLIPSE

    def _create_path(self):
        path = QPainterPath()
        r = QRectF(self._start, self._end).normalized()
        path.addEllipse(r)
        return path

    def to_dict(self):
        return self._base_dict()


class LineShape(BaseShape):
    def __init__(self, stroke_color=None, fill_color=None, stroke_width=None, parent=None):
        BaseShape.__init__(self, stroke_color, QColor(Qt.GlobalColor.transparent), stroke_width, parent)

    @property
    def type_name(self):
        return ShapeType.LINE

    def _create_path(self):
        path = QPainterPath()
        path.moveTo(self._start)
        path.lineTo(self._end)
        return path

    def set_fill_color(self, color):
        return

    def get_fill_color(self):
        return QColor(Qt.GlobalColor.transparent)

    def to_dict(self):
        d = self._base_dict()
        d["fill_color"] = QColor(Qt.GlobalColor.transparent).name(QColor.NameFormat.HexArgb)
        return d


class GroupShape(QGraphicsItemGroup, Shape):
    def __init__(self, parent=None):
        QGraphicsItemGroup.__init__(self, parent)
        self.setHandlesChildEvents(True)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

    def paint(self, painter, option, widget=None):
        opt = QStyleOptionGraphicsItem(option)
        opt.state &= ~QStyle.StateFlag.State_Selected
        opt.state &= ~QStyle.StateFlag.State_HasFocus
        QGraphicsItemGroup.paint(self, painter, opt, widget)

    @property
    def type_name(self):
        return ShapeType.GROUP

    def children_shapes(self):
        res = []
        for it in self.childItems():
            if isinstance(it, Shape):
                res.append(it)
        return res

    def set_geometry(self, start, end):
        return

    def set_stroke_color(self, color):
        for c in self.children_shapes():
            c.set_stroke_color(color)

    def get_stroke_color(self):
        kids = self.children_shapes()
        if kids:
            return kids[0].get_stroke_color()
        return QColor(DEFAULT_STROKE_COLOR)

    def set_fill_color(self, color):
        for c in self.children_shapes():
            c.set_fill_color(color)

    def get_fill_color(self):
        kids = self.children_shapes()
        if kids:
            return kids[0].get_fill_color()
        return QColor(DEFAULT_FILL_COLOR)

    def set_stroke_width(self, width):
        for c in self.children_shapes():
            c.set_stroke_width(width)

    def get_stroke_width(self):
        kids = self.children_shapes()
        if kids:
            return kids[0].get_stroke_width()
        return int(DEFAULT_STROKE_WIDTH)

    def to_dict(self):
        p = self.pos()
        return {
            "type": self.type_name.name,
            "x": float(p.x()),
            "y": float(p.y()),
            "children": [c.to_dict() for c in self.children_shapes()],
        }