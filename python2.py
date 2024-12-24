import sys
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
    QDesktopWidget, QMessageBox
)
from PyQt5.QtGui import QFont, QPalette, QColor
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class DielectricFieldSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Преломление электрического поля")
        self.resize(800, 600)
        self.center_window()

        # Основной виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Главный Layout
        layout = QVBoxLayout(self.central_widget)

        # Заголовок
        self.header_label = QLabel("Параметры границы диэлектриков")
        self.header_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet("color: #333333;")  # Тёмно-серый цвет текста
        layout.addWidget(self.header_label)

        # Поля ввода
        self.epsilon1_input = self.create_input_field("Диэлектрическая проницаемость первой среды (ε₁):")
        self.epsilon2_input = self.create_input_field("Диэлектрическая проницаемость второй среды (ε₂):")
        self.angle_input = self.create_input_field("Угол падения (в градусах):")
        self.e0_input = self.create_input_field("Модуль напряжённости (E₀):")

        # Кнопка запуска
        self.simulate_button = QPushButton("Построить график")
        self.simulate_button.setFont(QFont("Arial", 14))
        self.simulate_button.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                  stop:0 #4CAF50, stop:1 #2E7D32);
                color: white;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                  stop:0 #66BB6A, stop:1 #43A047);
            }
            QPushButton:pressed {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                  stop:0 #388E3C, stop:1 #1B5E20);
            }
        """)
        self.simulate_button.clicked.connect(self.validate_and_simulate)
        layout.addWidget(self.simulate_button)

        # Добавим отступы между элементами
        layout.addSpacing(20)

        # Стилизация центрального виджета
        self.central_widget.setStyleSheet("""
            QWidget {
                background-color: #F0F4F7;
            }
        """)

    def create_input_field(self, label_text):
        """
        Создаёт горизонтальный layout с меткой и полем ввода.
        """
        layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFont(QFont("Arial", 12))
        label.setStyleSheet("color: #555555;")  # Средне-серый цвет текста
        input_field = QLineEdit()
        input_field.setPlaceholderText("Введите значение")
        input_field.setFont(QFont("Arial", 12))
        input_field.setStyleSheet("""
            QLineEdit {
                border: 2px solid #CCCCCC;
                border-radius: 8px;
                padding: 5px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)
        layout.addWidget(label)
        layout.addWidget(input_field)
        self.centralWidget().layout().addLayout(layout)
        return input_field

    def center_window(self):
        """
        Центрирует окно на экране.
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def validate_and_simulate(self):
        """
        Проверяет данные и строит график.
        """
        try:
            epsilon1 = float(self.epsilon1_input.text())
            epsilon2 = float(self.epsilon2_input.text())
            angle = float(self.angle_input.text())
            e0 = float(self.e0_input.text())

            # Проверка входных данных
            if epsilon1 <= 0 or epsilon2 <= 0:
                raise ValueError("Диэлектрические проницаемости должны быть положительными числами.")
            if not (0 < angle < 90):
                raise ValueError("Угол падения должен быть между 0° и 90°.")
            if e0 <= 0:
                raise ValueError("Модуль напряжённости должен быть положительным числом.")

            # Запуск визуализации
            self.plot_fields(epsilon1, epsilon2, angle, e0)

        except ValueError as e:
            QMessageBox.critical(self, "Ошибка ввода", str(e))

    def refract_fields(self, e1, e2, angle_inc):
        """
        Рассчитывает углы преломления и соотношение для D.
        """
        angle_inc_rad = np.radians(angle_inc)
        # Корректный расчёт угла преломления
        tan_theta2 = (e2 / e1) * np.tan(angle_inc_rad)
        angle_refr_rad = np.arctan(tan_theta2)
        d_ratio = e2 / e1  # Соотношение для D
        return angle_inc_rad, angle_refr_rad, d_ratio

    def plot_fields(self, epsilon1, epsilon2, angle_inc, e0):
        """
        Визуализация линий электрического поля и смещения с использованием quiver plot.
        """
        angle_inc_rad, angle_refr_rad, d_ratio = self.refract_fields(epsilon1, epsilon2, angle_inc)

        # Создание сетки
        X, Y = np.meshgrid(np.linspace(-2, 2, 20), np.linspace(-2, 2, 20))

        # Определение границы
        boundary_x = 0

        # Поле E в первой среде (левая сторона)
        E1_x = e0 * np.ones_like(X)
        E1_y = e0 * np.tan(angle_inc_rad) * np.ones_like(Y)

        # Поле E во второй среде (правая сторона)
        E2_x = e0 * np.cos(angle_refr_rad) / np.cos(angle_inc_rad) * np.ones_like(X)
        E2_y = e0 * np.sin(angle_refr_rad) / np.cos(angle_inc_rad) * np.ones_like(Y)

        # Поле D в первой среде
        D1_x = e0 * d_ratio * np.ones_like(X)
        D1_y = e0 * d_ratio * np.tan(angle_inc_rad) * np.ones_like(Y)

        # Поле D во второй среде
        D2_x = e0 * np.cos(angle_refr_rad) / np.cos(angle_inc_rad) * np.ones_like(X)
        D2_y = e0 * np.sin(angle_refr_rad) / np.cos(angle_inc_rad) * np.ones_like(Y)

        # Объединение полей E и D
        # Для лучшей визуализации будем разделять области
        mask_left = X < boundary_x
        mask_right = X >= boundary_x

        # Настройка фигуры
        plt.figure(figsize=(12, 8))
        ax = plt.gca()

        # Граница диэлектриков
        ax.axvline(boundary_x, color='k', linestyle='--', linewidth=2)

        # Векторные поля E
        plt.quiver(X[mask_left], Y[mask_left], E1_x[mask_left], E1_y[mask_left],
                   color='darkblue', scale=20, label='E в среде 1')
        plt.quiver(X[mask_right], Y[mask_right], E2_x[mask_right], E2_y[mask_right],
                   color='orange', scale=20, label='E в среде 2')

        # Векторные поля D
        plt.quiver(X[mask_left], Y[mask_left], D1_x[mask_left], D1_y[mask_left],
                   color='lightblue', scale=40, label='D в среде 1')
        plt.quiver(X[mask_right], Y[mask_right], D2_x[mask_right], D2_y[mask_right],
                   color='pink', scale=40, label='D в среде 2')

        # Настройка лимитов
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)

        # Подписи и заголовок
        plt.title("Преломление E и D на границе двух диэлектриков", fontsize=16, fontweight='bold')
        plt.xlabel("X", fontsize=14)
        plt.ylabel("Y", fontsize=14)

        # Легенда
        plt.legend(loc='upper right', fontsize=12)

        # Сетка
        plt.grid(True, linestyle='--', alpha=0.5)

        # Визуализация углов
        # Угол θ₁
        arc1 = patches.Arc((-1.5, 0), 0.5, 0.5, angle=0,
                           theta1=90 - angle_inc, theta2=90, edgecolor='darkblue', linewidth=2)
        ax.add_patch(arc1)
        plt.text(-1.8, 0.3, r'$\theta_1$', color='darkblue', fontsize=14)

        # Угол θ₂
        theta2_deg = np.degrees(angle_refr_rad)
        arc2 = patches.Arc((1.5, 0), 0.5, 0.5, angle=0,
                           theta1=90, theta2=90 - theta2_deg, edgecolor='orange', linewidth=2)
        ax.add_patch(arc2)
        plt.text(1.6, 0.3, r'$\theta_2$', color='orange', fontsize=14)

        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DielectricFieldSimulator()
    window.show()
    sys.exit(app.exec_())