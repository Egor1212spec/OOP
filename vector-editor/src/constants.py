from enum import Enum, auto
from PySide6.QtGui import QColor


class ShapeType(Enum):
    RECTANGLE = auto()
    ELLIPSE = auto()
    LINE = auto()
    GROUP = auto()


class ToolType(Enum):
    SELECTION = auto()
    RECTANGLE = auto()
    ELLIPSE = auto()
    LINE = auto()


CANVAS_WIDTH = 900
CANVAS_HEIGHT = 650

MIN_SHAPE_SIZE = 5

DEFAULT_FILL_COLOR = QColor(120, 170, 220, 160)
DEFAULT_STROKE_COLOR = QColor(0, 0, 0)
DEFAULT_STROKE_WIDTH = 2
DEFAULT_BACKGROUND_COLOR = QColor(255, 255, 255)

MIN_STROKE_WIDTH = 1
MAX_STROKE_WIDTH = 50

FILE_EXTENSION = ".pyvec"
FILE_FORMAT_VERSION = "1.0"