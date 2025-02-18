import os
import sys

import requests
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtCore import Qt

SCREEN_SIZE = [600, 600]
API_KEY = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
SERVER_ADDRESS = 'https://static-maps.yandex.ru/v1?'


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.cord1, self.cord2 = 37.530887, 55.703118
        self.delta = 0.002
        self.map_file = "map.png"
        self.image = None

        self.initUI()
        self.getImage()

    def getImage(self):
        ll_spn = f'll={self.cord1},{self.cord2}&spn={self.delta},{self.delta}'
        map_request = f"{SERVER_ADDRESS}{ll_spn}&apikey={API_KEY}"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        try:
            with open(self.map_file, "wb") as file:
                file.write(response.content)
        except Exception as e:
            print(f"Ошибка при сохранении изображения: {e}")
            return

        self.update_map()

    def update_map(self):
        try:
            self.pixmap = QPixmap(self.map_file)
            self.image.setPixmap(self.pixmap)
        except Exception as e:
            print(f"Ошибка при загрузке или отображении изображения: {e}")

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)

    def closeEvent(self, event):
        try:
            os.remove(self.map_file)
        except FileNotFoundError:
            pass  # Файл уже удален, ничего страшного
        except Exception as e:
            print(f"Ошибка при удалении файла: {e}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_PageUp:
            self.change_delta(2)
        elif event.key() == Qt.Key.Key_PageDown:
            self.change_delta(0.5)
        elif event.key() == Qt.Key.Key_Right:
            d = self.move_key()
            self.cord1 += d

            self.getImage()
        elif event.key() == Qt.Key.Key_Left:
            d = self.move_key()
            self.cord1 -= d
            self.getImage()
        elif event.key() == Qt.Key.Key_Down:
            d = self.move_key()
            self.cord2 -= d

            self.getImage()
        elif event.key() == Qt.Key.Key_Up:
            d = self.move_key()
            self.cord2 += d
            self.getImage()

    def change_delta(self, delta_change):
        if 0.000125 <= self.delta * delta_change <= 66:
            self.delta *= delta_change
            self.getImage()

    def move_key(self):
        return self.delta / 10


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
