import json
from pathlib import Path

from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QImage, QPainter
from PySide6.QtCore import QRectF

from src.constants import FILE_FORMAT_VERSION, CANVAS_WIDTH, CANVAS_HEIGHT, DEFAULT_BACKGROUND_COLOR
from src.logic.factory import ShapeFactory
from src.logic.shapes import Shape


class DocumentManager:
    def __init__(self, scene):
        self.scene = scene

    def save_filter(self):
        return "PyVectorEditor (*.pyvec);;JSON (*.json);;All (*.*)"

    def export_filter(self):
        return "PNG (*.png);;JPG (*.jpg *.jpeg);;BMP (*.bmp)"

    def save_json(self, file_path):
        try:
            shapes = []
            for it in self.scene.items():
                if isinstance(it, Shape) and it.parentItem() is None:
                    shapes.append(it.to_dict())

            doc = {
                "version": FILE_FORMAT_VERSION,
                "canvas": {"width": CANVAS_WIDTH, "height": CANVAS_HEIGHT},
                "shapes": shapes,
            }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(doc, f, indent=2, ensure_ascii=False)

            return True
        except Exception:
            return False

    def load_json(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return False

        if not data.get("version"):
            return False

        self.scene.clear()

        for d in data.get("shapes", []):
            it = ShapeFactory.from_dict(d)
            if it is not None and isinstance(it, QGraphicsItem):
                self.scene.addItem(it)

        return True

    def export_image(self, file_path):
        try:
            img = QImage(CANVAS_WIDTH, CANVAS_HEIGHT, QImage.Format.Format_ARGB32)
            img.fill(DEFAULT_BACKGROUND_COLOR)

            p = QPainter(img)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)

            r = QRectF(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)
            self.scene.render(p, r, r)
            p.end()

            suf = Path(file_path).suffix.lower()
            fmt = "PNG"
            if suf in [".jpg", ".jpeg"]:
                fmt = "JPEG"
            if suf == ".bmp":
                fmt = "BMP"

            return img.save(str(file_path), fmt)
        except Exception:
            return False