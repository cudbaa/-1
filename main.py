from gettext import install
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QDialog, QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt6.QtGui import QPixmap
import sqlite3
import random
from datetime import datetime
from PyQt6.QtCore impo


# Функция создания базы данных
def create_database():
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            count_rounds INTEGER,
            date_start TEXT,
            date_end TEXT,
            status TEXT,
            result TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_game INTEGER,
            state TEXT,
            result INTEGER,
            FOREIGN KEY (id_game) REFERENCES Games(id)
        )
    """)

    conn.commit()
    conn.close()


class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Игра: Камень, Ножницы, Бумага")
        self.setGeometry(200, 200, 400, 300)

        # Основные кнопки
        self.play_button = QPushButton("Играть", self)
        self.play_button.setFixedSize(150, 50)
        self.play_button.clicked.connect(self.start_game)

        self.history_button = QPushButton("Посмотреть историю игр", self)
        self.history_button.setFixedSize(150, 50)
        self.history_button.clicked.connect(self.show_history)

        # Расположение кнопок
        layout = QVBoxLayout()
        layout.addWidget(self.play_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.history_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Центральный виджет
        central_widget = QLabel("Добро пожаловать в игру!")
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    def start_game(self):
        # Запускаем диалоговое окно для ввода имени игрока
        name_dialog = NameInputDialog(self)
        if name_dialog.exec():
            player_name = name_dialog.player_name
            game_window = GameWindow(player_name)
            game_window.show()

    def show_history(self):
        self.history_window = HistoryWindow()
        self.history_window.show()


class NameInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Введите имя")
        self.setGeometry(300, 300, 200, 100)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Ваше имя")

        self.submit_button = QPushButton("Начать", self)
        self.submit_button.clicked.connect(self.submit_name)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Введите ваше имя:"))
        layout.addWidget(self.name_input)
        layout.addWidget(self.submit_button)
        self.setLayout(layout)

    def submit_name(self):
        self.player_name = self.name_input.text()
        if self.player_name:
            self.accept()  # Закрыть диалог
            self.game_window = GameWindow(self.player_name)  # Создать окно игры
            self.game_window.show()  # Показать окно игры


class GameWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle("Раунды")
        self.setGeometry(200, 200, 500, 400)
        self.username = username
        self.current_round = 1
        self.max_rounds = 3
        self.score = 0
        self.date_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.game_id = None

        self.round_label = QLabel(f"Раунд {self.current_round}", self)
        self.result_label = QLabel("", self)
        self.player_image = QLabel(self)
        self.computer_image = QLabel(self)

        self.images = {
            "Камень": "rock.png",
            "Бумага": "paper.png",
            "Ножницы": "scissors.png",
        }

        self.rock_button = QPushButton("Камень", self)
        self.paper_button = QPushButton("Бумага", self)
        self.scissors_button = QPushButton("Ножницы", self)

        self.rock_button.clicked.connect(lambda: self.play_round("Камень"))
        self.paper_button.clicked.connect(lambda: self.play_round("Бумага"))
        self.scissors_button.clicked.connect(lambda: self.play_round("Ножницы"))

        layout = QVBoxLayout()
        layout.addWidget(self.round_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.player_image, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel("VS", self), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.computer_image, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.result_label, alignment=Qt.AlignmentFlag.AlignCenter)

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.rock_button)
        button_layout.addWidget(self.paper_button)
        button_layout.addWidget(self.scissors_button)

        layout.addLayout(button_layout)

        central_widget = QLabel("Выберите действие:")
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.create_game_record()

    def create_game_record(self):
        conn = sqlite3.connect("game.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Games (username, count_rounds, date_start, date_end, status, result)
            VALUES (?, 0, ?, NULL, 'Игра идет', NULL)
        """, (self.username, self.date_start))
        self.game_id = cursor.lastrowid
        conn.commit()
        conn.close()

    def play_round(self, player_choice):
        computer_choice = random.choice(["Камень", "Бумага", "Ножницы"])
        self.player_image.setPixmap(QPixmap(self.images[player_choice]).scaled(100, 100))
        self.computer_image.setPixmap(QPixmap(self.images[computer_choice]).scaled(100, 100))

        if player_choice == computer_choice:
            result = 0
            outcome_text = "Ничья!"
            self.setStyleSheet("background-color: white;")
        elif (player_choice == "Камень" and computer_choice == "Ножницы") or \
             (player_choice == "Ножницы" and computer_choice == "Бумага") or \
             (player_choice == "Бумага" and computer_choice == "Камень"):
            result = 1
            outcome_text = "Вы выиграли раунд!"
            self.score += 1
            self.setStyleSheet("background-color: green;")
        else:
            result = -1
            outcome_text = "Вы проиграли раунд."
            self.setStyleSheet("background-color: red;")

        self.result_label.setText(outcome_text)
        self.save_round(player_choice, computer_choice, result)
        self.current_round += 1

        if self.current_round > self.max_rounds:
            self.finish_game()
        else:
            self.round_label.setText(f"Раунд {self.current_round}")

    def save_round(self, player_choice, computer_choice, result):
        conn = sqlite3.connect("game.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Rounds (id_game, state, result)
            VALUES (?, ?, ?)
        """, (self.game_id, f"Игрок: {player_choice}, Компьютер: {computer_choice}", result))
        conn.commit()
        conn.close()

    def finish_game(self):
        date_end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "Полностью завершена" if self.current_round > self.max_rounds else "Завершена досрочно"
        
        # Подсчет результатов
        conn = sqlite3.connect("game.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT result FROM Rounds WHERE id_game = ?
        """, (self.game_id,))
        results = cursor.fetchall()  # Получаем все результаты раундов
        
        player_wins = sum(1 for r in results if r[0] == 1)
        computer_wins = sum(1 for r in results if r[0] == -1)
        
        # Определяем итог игры
        if player_wins > computer_wins:
            result = "Winner"
        elif player_wins < computer_wins:
            result = "Lose"
        else:
            result = "Draw"  # Добавляем ничью

        # Обновляем запись об игре
        cursor.execute("""
            UPDATE Games
            SET count_rounds = ?, date_end = ?, status = ?, result = ?
            WHERE id = ?
        """, (self.current_round - 1, date_end, status, result, self.game_id))
        conn.commit()
        conn.close()

        # Вывод результата игры
        QMessageBox.information(self, "Игра завершена", f"Игра завершена! Итог: {result}")
        self.close()


class HistoryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("История игр")
        self.setGeometry(200, 200, 600, 400)

        self.table = QTableWidget(self)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Имя", "Раунды", "Начало", "Конец", "Статус", "Результат"])
        self.setCentralWidget(self.table)

        self.load_history()

    def load_history(self):
        conn = sqlite3.connect("game.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Games")
        games = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(games))
        for row_index, game in enumerate(games):
            for col_index, value in enumerate(game):
                self.table.setItem(row_index, col_index, QTableWidgetItem(str(value)))


if __name__ == "__main__":
    create_database()
    app = QApplication(sys.argv)
    main_window = StartWindow()  # Создаем главное окно
    main_window.show()  # Отображаем главное окно
    sys.exit(app.exec())  # Запускаем цикл приложения