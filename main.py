import os
import sys
import requests
from PyQt6.QtGui import QPixmap, QColor, QPalette
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit
from PyQt6.QtCore import Qt

SCREEN_SIZE = [600, 600]
API_KEY = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
GEOCODE_API_KEY = '8013b162-6b42-4997-9691-77b7074026e0'  # API key для геокодирования
SERVER_ADDRESS = 'https://static-maps.yandex.ru/v1?'


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.cord1, self.cord2 = 37.530887, 55.703118  # Начальные координаты Москвы
        self.delta = 0.002
        self.map_file = "map.png"
        self.image = None
        self.is_dark_theme = False
        self.point = None  # Переменная для хранения координат метки

        self.initUI()
        self.getImage()

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)

        self.button_theme = QPushButton('Переключить тему', self)
        self.button_theme.setGeometry(200, 500, 200, 40)
        self.button_theme.clicked.connect(self.toggle_theme)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Введите запрос для поиска...")
        self.search_input.setGeometry(0, 460, 450, 30)
        self.search_input.returnPressed.connect(self.search_object)

        self.search_button = QPushButton("Искать", self)
        self.search_button.setGeometry(470, 460, 100, 30)
        self.search_button.clicked.connect(self.search_object)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def getImage(self):
        ll_spn = f'll={self.cord1},{self.cord2}&spn={self.delta},{self.delta}'
        palette = QPalette()
        if self.is_dark_theme:
            map_theme = 'dark'
            palette.setColor(QPalette.ColorRole.Window, QColor('#171717'))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            self.setPalette(palette)
            style_button = """
                        QPushButton {
                            background-color: #1c1c1c;
                            color: white;
                            border: none; /* Убирает рамку (если нужна) */
                            padding: 5px; /* Отступ текста от краев кнопки */
                        }
                        QPushButton:hover {
                            background-color: #262626;
                        }
                        QPushButton:pressed {
                            background-color: #2e2e2e;
                        }
                    """
            self.button_theme.setStyleSheet(style_button)
            self.search_button.setStyleSheet(style_button)
            self.search_input.setStyleSheet("""
                        QLineEdit {
                            background-color: #1c1c1c;
                            color: white;
                            border: none; /* Убирает рамку (если нужна) */
                            padding: 5px; /* Отступ текста от краев кнопки */
                            }
                    """)
        else:
            map_theme = 'light'
            palette.setColor(QPalette.ColorRole.Window, QColor('#ffffff'))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            self.setPalette(palette)
            style_button = """
                                    QPushButton {
                                        background-color: #f5f5f5;
                                        color: black;
                                        border: none; /* Убирает рамку (если нужна) */
                                        padding: 5px; /* Отступ текста от краев кнопки */
                                    }
                                    QPushButton:hover {
                                        background-color: #ededed;
                                    }
                                    QPushButton:pressed {
                                        background-color: #e3e3e3;
                                    }
                                """
            self.button_theme.setStyleSheet(style_button)
            self.search_button.setStyleSheet(style_button)
            self.search_input.setStyleSheet("""
                                    QLineEdit {
                                        background-color: #f5f5f5;
                                        color: black;
                                        border: none; /* Убирает рамку (если нужна) */
                                        padding: 5px; /* Отступ текста от краев кнопки */
                                        }
                                """)

        # Добавляем параметр pt, если есть координаты метки
        if self.point:
            pt = f'&pt={self.point[0]},{self.point[1]},pm2rdl'  # pm2rdl - метка
        else:
            pt = ''

        map_request = f"{SERVER_ADDRESS}{ll_spn}&theme={map_theme}{pt}&apikey={API_KEY}"  # Добавляем метку в запрос
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

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.getImage()

    def search_object(self):
        query = self.search_input.text()
        if query:
            geocode_url = f"https://geocode-maps.yandex.ru/1.x/?apikey={GEOCODE_API_KEY}&geocode={query}&format=json"
            response = requests.get(geocode_url)

            if response.status_code == 200:
                json_response = response.json()
                try:
                    # Извлекаем координаты из ответа
                    coordinates = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
                    self.cord1, self.cord2 = map(float, coordinates.split())

                    # Сохраняем координаты для отображения метки
                    self.point = (self.cord1, self.cord2)

                    self.getImage()  # Обновляем карту с меткой

                except (IndexError, KeyError):
                    print("Объект не найден.")
                    self.point = None  # Сбрасываем метку, если объект не найден
                    self.getImage()

            else:
                print("Ошибка выполнения запроса геокодирования:", response.status_code)
                self.point = None #Сбросить метку

        self.search_input.clear()
        self.setFocus()

    def closeEvent(self, event):
        try:
            os.remove(self.map_file)
        except FileNotFoundError:
            pass
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