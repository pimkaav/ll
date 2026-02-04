import sys
import mysql.connector
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6 import uic


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('login.ui', self)
        self.login_button.clicked.connect(self.login)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="flower_shop"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE username=%s AND password=%s",
                           (username, password))
            result = cursor.fetchone()

            if result:
                role = result[0]
                self.main_window = MainWindow(role, conn)
                self.main_window.show()
                self.hide()
            else:
                QMessageBox.warning(self, "Ошибка", "Неверные данные")

        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))


class MainWindow(QMainWindow):
    def __init__(self, role, connection):
        super().__init__()
        self.role = role
        self.conn = connection
        self.cursor = self.conn.cursor()

        if role == "admin":
            uic.loadUi('admin.ui', self)
            self.setup_admin()
        else:
            uic.loadUi('user.ui', self)
            self.setup_user()

    def setup_admin(self):
        self.load_data()
        self.add_button.clicked.connect(self.add_flower)
        self.delete_button.clicked.connect(self.delete_flower)
        self.update_button.clicked.connect(self.update_flower)
        self.filter_button.clicked.connect(self.filter_data)
        self.show_all_button.clicked.connect(self.load_data)

    def setup_user(self):
        self.load_data()

    def load_data(self):
        query = "SELECT id, name, color, price, type, occasion, quantity FROM flowers"
        self.cursor.execute(query)
        data = self.cursor.fetchall()

        self.table.setRowCount(len(data))
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(['ID', 'Название', 'Цвет', 'Цена', 'Тип', 'Повод', 'Кол-во'])

        for row_num, row_data in enumerate(data):
            for col_num, col_data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))

    def add_flower(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить цветок")
        layout = QVBoxLayout()

        form = QFormLayout()
        name_input = QLineEdit()
        color_input = QLineEdit()
        price_input = QLineEdit()
        type_input = QLineEdit()
        occasion_input = QLineEdit()
        quantity_input = QLineEdit()

        form.addRow("Название:", name_input)
        form.addRow("Цвет:", color_input)
        form.addRow("Цена:", price_input)
        form.addRow("Тип:", type_input)
        form.addRow("Повод:", occasion_input)
        form.addRow("Количество:", quantity_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(lambda: self.save_flower(
            name_input.text(), color_input.text(), price_input.text(),
            type_input.text(), occasion_input.text(), quantity_input.text(), dialog))
        buttons.rejected.connect(dialog.reject)

        layout.addLayout(form)
        layout.addWidget(buttons)
        dialog.setLayout(layout)
        dialog.exec()

    def save_flower(self, name, color, price, type_, occasion, quantity, dialog):
        try:
            query = """INSERT INTO flowers (name, color, price, type, occasion, quantity) 
                      VALUES (%s, %s, %s, %s, %s, %s)"""
            self.cursor.execute(query, (name, color, float(price), type_, occasion, int(quantity)))
            self.conn.commit()
            self.load_data()
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def delete_flower(self):
        selected = self.table.currentRow()
        if selected >= 0:
            id_item = self.table.item(selected, 0).text()
            reply = QMessageBox.question(self, 'Удаление',
                                         'Удалить запись?',
                                         QMessageBox.StandardButton.Yes |
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.cursor.execute("DELETE FROM flowers WHERE id = %s", (id_item,))
                self.conn.commit()
                self.load_data()

    def update_flower(self):
        selected = self.table.currentRow()
        if selected >= 0:
            id_val = self.table.item(selected, 0).text()
            name = self.table.item(selected, 1).text()
            color = self.table.item(selected, 2).text()
            price = self.table.item(selected, 3).text()
            type_ = self.table.item(selected, 4).text()
            occasion = self.table.item(selected, 5).text()
            quantity = self.table.item(selected, 6).text()

            dialog = QDialog(self)
            dialog.setWindowTitle("Изменить цветок")
            layout = QVBoxLayout()

            form = QFormLayout()
            name_input = QLineEdit(name)
            color_input = QLineEdit(color)
            price_input = QLineEdit(price)
            type_input = QLineEdit(type_)
            occasion_input = QLineEdit(occasion)
            quantity_input = QLineEdit(quantity)

            form.addRow("Название:", name_input)
            form.addRow("Цвет:", color_input)
            form.addRow("Цена:", price_input)
            form.addRow("Тип:", type_input)
            form.addRow("Повод:", occasion_input)
            form.addRow("Количество:", quantity_input)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                       QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(lambda: self.save_update(
                id_val, name_input.text(), color_input.text(), price_input.text(),
                type_input.text(), occasion_input.text(), quantity_input.text(), dialog))
            buttons.rejected.connect(dialog.reject)

            layout.addLayout(form)
            layout.addWidget(buttons)
            dialog.setLayout(layout)
            dialog.exec()

    def save_update(self, id_val, name, color, price, type_, occasion, quantity, dialog):
        try:
            query = """UPDATE flowers SET name=%s, color=%s, price=%s, 
                      type=%s, occasion=%s, quantity=%s WHERE id=%s"""
            self.cursor.execute(query, (name, color, float(price), type_,
                                        occasion, int(quantity), id_val))
            self.conn.commit()
            self.load_data()
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def filter_data(self):
        filter_text = self.filter_input.text()
        if filter_text:
            query = """SELECT * FROM flowers WHERE 
                      name LIKE %s OR color LIKE %s OR occasion LIKE %s"""
            search = f"%{filter_text}%"
            self.cursor.execute(query, (search, search, search))
        else:
            self.cursor.execute("SELECT * FROM flowers")

        data = self.cursor.fetchall()
        self.table.setRowCount(len(data))

        for row_num, row_data in enumerate(data):
            for col_num, col_data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())