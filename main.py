import os
import sys
import requests
from PyQt6.QtGui import QPixmap, QColor, QPalette
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QCheckBox
from PyQt6.QtCore import Qt

SCREEN_SIZE = [600, 700]  # Увеличиваем высоту окна для размещения поля адреса
API_KEY = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
GEOCODE_API_KEY = '8013b162-6b42-4997-9691-77b7074026e0'
SERVER_ADDRESS = 'https://static-maps.yandex.ru/v1?'
GEOCODE_ADDRESS_API = "https://geocode-maps.yandex.ru/1.x"


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.cord1, self.cord2 = 37.530887, 55.703118
        self.delta = 0.002
        self.map_file = "map.png"
        self.image = None
        self.is_dark_theme = False
        self.point = None
        self.address = None  # Переменная для хранения адреса
        self.include_postal_code = True  # По умолчанию почтовый индекс включен

        self.initUI()
        self.getImage()

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        main_layout = QVBoxLayout(self)  # Основной вертикальный макет

        self.image = QLabel(self)
        self.image.resize(600, 450)
        main_layout.addWidget(self.image)

        # Добавляем поле для отображения адреса
        self.address_label = QLabel("Адрес: ")
        main_layout.addWidget(self.address_label)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Введите запрос для поиска...")
        main_layout.addWidget(self.search_input)

        button_layout = QVBoxLayout()  # Горизонтальный макет для кнопок
        main_layout.addLayout(button_layout)

        self.search_button = QPushButton("Искать", self)
        button_layout.addWidget(self.search_button)
        self.search_button.clicked.connect(self.search_object)

        self.reset_button = QPushButton("Сброс", self)
        button_layout.addWidget(self.reset_button)
        self.reset_button.clicked.connect(self.reset_search)

        self.button_theme = QPushButton('Переключить тему', self)
        button_layout.addWidget(self.button_theme)
        self.button_theme.clicked.connect(self.toggle_theme)

        # Добавляем CheckBox для включения/выключения почтового индекса
        self.postal_code_checkbox = QCheckBox("Включить почтовый индекс", self)
        self.postal_code_checkbox.setChecked(self.include_postal_code)  # Устанавливаем начальное состояние
        self.postal_code_checkbox.stateChanged.connect(self.toggle_postal_code)
        main_layout.addWidget(self.postal_code_checkbox)

        self.setLayout(main_layout)  # Устанавливаем основной макет для окна
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
            self.reset_button.setStyleSheet(style_button)
            self.search_input.setStyleSheet("""
                        QLineEdit {
                            background-color: #1c1c1c;
                            color: white;
                            border: none; /* Убирает рамку (если нужна) */
                            padding: 5px; /* Отступ текста от краев кнопки */
                            }
                    """)
            self.address_label.setStyleSheet("color: white;")
            self.postal_code_checkbox.setStyleSheet("color: white;")
        else:
            map_theme = 'light'
            palette.setColor(QPalette.ColorRole.Window, QColor('#ffffff'))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
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
            self.reset_button.setStyleSheet(style_button)
            self.search_input.setStyleSheet("""
                                    QLineEdit {
                                        background-color: #f5f5f5;
                                        color: black;
                                        border: none; /* Убирает рамку (если нужна) */
                                        padding: 5px; /* Отступ текста от краев кнопки */
                                        }
                                """)
            self.address_label.setStyleSheet("color: black;")
            self.postal_code_checkbox.setStyleSheet("color: black;")

        if self.point:
            pt = f'&pt={self.point[0]},{self.point[1]},pm2rdl'
        else:
            pt = ''

        map_request = f"{SERVER_ADDRESS}{ll_spn}&theme={map_theme}{pt}&apikey={API_KEY}"
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

        self.update_address_label()  # Обновляем отображение адреса

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
                    coordinates = \
                        json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point'][
                            'pos']
                    self.cord1, self.cord2 = map(float, coordinates.split())
                    self.point = (self.cord1, self.cord2)
                    self.get_address()
                    self.getImage()

                except (IndexError, KeyError):
                    print("Объект не найден.")
                    self.point = None
                    self.address = None
                    self.getImage()

            else:
                print("Ошибка выполнения запроса геокодирования:", response.status_code)
                self.point = None
                self.address = None

        self.search_input.clear()
        self.setFocus()

    def get_address(self):
        try:
            params = {
                "apikey": GEOCODE_API_KEY,
                "geocode": f"{self.cord1},{self.cord2}",
                "format": "json"
            }
            response = requests.get(GEOCODE_ADDRESS_API, params=params)
            json_data = response.json()
            geo_object = json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            self.address = geo_object["metaDataProperty"]["GeocoderMetaData"]["text"]

            if self.include_postal_code:
                try:
                    postal_code = geo_object["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
                    self.address = f"{postal_code}, {self.address}"
                except KeyError:
                    print("Почтовый индекс не найден.")

            self.update_address_label()
        except Exception as e:
            print(f"Ошибка при получении адреса: {e}")
            self.address = "Адрес не найден"
            self.update_address_label()

    def update_address_label(self):
        if self.address:
            self.address_label.setText(f"Адрес: {self.address}")
        else:
            self.address_label.setText("Адрес: ")

    def reset_search(self):
        self.point = None
        self.address = None  # Сбрасываем адрес
        self.update_address_label()  # Обновляем поле адреса
        self.getImage()
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

    def toggle_postal_code(self, state):
        self.include_postal_code = (state == Qt.CheckState.Checked.value)  # Обновляем состояние
        self.get_address()  # Обновляем адрес при изменении состояния CheckBox


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
