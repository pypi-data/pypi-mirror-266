import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QMessageBox, QVBoxLayout, QLabel
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel, QPixmap

from model.conn import Model
import card_view

class Login(QMainWindow):
    def __init__(self):
        super(Login, self).__init__()
        uic.loadUi('Screens/login.ui', self)
        self.setWindowIcon(QIcon('img/icon.png'))
        self.setWindowTitle('Окно входа')
        self.label.hide()
        
        self.pushButton = self.findChild(QtWidgets.QPushButton, 'pushButton')
        self.pushButton.clicked.connect(self.log)
        
    def log(self):
        login = self.lineEdit.text()
        password = self.lineEdit_2.text()
        
        if not (login and password):
            self.label.setText('Заполните все поля')
            self.label.show()
        else:
            conn = Model().conn
            cur = conn.cursor()
            cur.execute('select * from user where login = %s and password = %s', 
                        (login, password))
            data = cur.fetchone()
            if data:
                QMessageBox.information(self, 'Ok', f'привет {data[1]}')
                self.table = card_view.CardApp()
                self.table.show()
                self.hide()
            else:
                QMessageBox.information(self, 'Не ок', 'пользователь не найден')


if __name__ == '__main__':
    conn = Model().conn
    app = QtWidgets.QApplication([])
    # login = Login()
    login = card_view.CardApp()
    login.show()
    sys.exit(app.exec_())