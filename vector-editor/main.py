import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.app import MainWindow


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    w = MainWindow()
    w.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())