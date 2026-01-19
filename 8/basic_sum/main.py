import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QLineEdit, QPushButton, QLabel, QMessageBox
)
from PySide6.QtCore import Qt

class CalculatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Настройка основного окна
        self.setWindowTitle("Сумматор")
        self.setMinimumSize(250, 200)

        # Инициализация интерфейса
        self._init_ui()
        
        # Подключение сигналов
        self.calc_button.clicked.connect(self._calculate_result)

    def _init_ui(self):
        """Создание и размещение виджетов вручную (без .ui файла)"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Используем вертикальный слой для автоматического выравнивания
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Поля ввода
        self.first_input = QLineEdit()
        self.first_input.setPlaceholderText("Введите первое число")
        
        self.second_input = QLineEdit()
        self.second_input.setPlaceholderText("Введите второе число")

        # Кнопка
        self.calc_button = QPushButton("Посчитать")
        self.calc_button.setCursor(Qt.CursorShape.PointingHandCursor)

        # Метка результата
        self.result_label = QLabel("Ожидание ввода...")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Немного стилизации CSS для наглядности
        self.result_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")

        # Добавляем всё в слой
        layout.addWidget(self.first_input)
        layout.addWidget(self.second_input)
        layout.addWidget(self.calc_button)
        layout.addSpacing(10)
        layout.addWidget(self.result_label)
        
        # Добавляем "пружину", чтобы прижать элементы вверх (опционально)
        layout.addStretch()

        self.central_widget.setLayout(layout)

    def _calculate_result(self):
        """Логика вычислений"""
        val1_text = self.first_input.text().replace(',', '.')
        val2_text = self.second_input.text().replace(',', '.')

        if not val1_text or not val2_text:
            self.result_label.setText("Заполните оба поля")
            self.result_label.setStyleSheet("color: orange;")
            return

        try:
            num1 = float(val1_text)
            num2 = float(val2_text)
            result = num1 + num2
            
            # Форматируем: если число целое, не показываем .0
            display_result = int(result) if result.is_integer() else result
            
            self.result_label.setText(f"Результат: {display_result}")
            self.result_label.setStyleSheet("color: green; font-weight: bold;")
            
        except ValueError:
            self.result_label.setText("Ошибка: введите числа")
            self.result_label.setStyleSheet("color: red;")

def main():
    app = QApplication(sys.argv)
    window = CalculatorApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()