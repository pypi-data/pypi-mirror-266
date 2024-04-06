import datetime
import os
import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QMessageBox, QVBoxLayout, QLabel, QFileDialog
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel, QPixmap


from shutil import copyfile
from model.conn import Model
import main


class CardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Screens/main_objects.ui', self)
        self.setWindowTitle("Карточки из базы данных")
        self.setGeometry(100, 100, 800, 600)

        connection = Model().conn
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM user')
        rows = cursor.fetchall()
        
        self.scrollArea = self.findChild(QtWidgets.QScrollArea, 'scrollArea')
        self.scrollAreaWidgetContents = self.findChild(QWidget, 'scrollAreaWidgetContents')

        for row in rows:
            card_widget = CardWidget({'id': row[0], 'name': row[1], 'description': row[2], 'photo': row[3]})
            self.scrollAreaWidgetContents.layout().addWidget(card_widget)

        self.lineEdit.textChanged.connect(self.search)
        self.pushButton.clicked.connect(self.exit)
        self.pushButton_2.clicked.connect(self.add_data_show)

    def add_data_show(self):
        self.add = RefactorData()
        self.add.show()
        self.hide()
        
    def search(self):
        text_data = self.lineEdit.text().lower()
        
        for index in range(self.scrollAreaWidgetContents.layout().count()):
            item = self.scrollAreaWidgetContents.layout().itemAt(index).widget()
            
            if any(text_data in field.text().lower() for field in (item.label, item.label_2)):
                item.show()
            elif text_data == '':
                item.show()
            else:
                item.hide()
        
    def exit(self):
        self.login = main.Login()
        self.login.show()
        self.hide()


class CardWidget(QWidget):
    def __init__(self, data):
        super(CardWidget, self).__init__()
        uic.loadUi('Screens/object.ui', self)

        self.id_query = data['id']
        
        self.label_3.setPixmap(QPixmap('img/' + data['photo']).scaled(100, 100))
        self.label.setText(data['name'])
        self.label_2.setText(data['description'])
        
        self.pushButton.clicked.connect(self.delete)
        
    def delete(self):
        conn = Model().conn
        cur = conn.cursor()
        
        try:
            cur.execute('delete from user where user_id = %s', (self.id_query,))
            conn.commit()
            self.deleteLater()
        except Exception as er:
            QMessageBox.information(self, 'Ошибка', f'Ой, почему-то не удалось удалить запись, {er}')


class RefactorData(QtWidgets.QMainWindow):
    def __init__(self):
        super(RefactorData, self).__init__()
        uic.loadUi('Screens/add_data.ui', self)
        
        self.pushButton_3.clicked.connect(self.open_folder)

        self.pushButton.clicked.connect(self.add)
        self.pushButton_2.clicked.connect(self.exit)
    
    def open_folder(self):
        file_name, formats = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.bmp)", options=QFileDialog.Options())
        self.file_name = file_name
        self.label_2.setPixmap(QPixmap(file_name).scaled(200, 200))
    
    def add(self):
        login = self.lineEdit.text()
        password = self.lineEdit_2.text()
        photo = os.path.basename(self.file_name)
        date_time = datetime.datetime.strptime(self.dateTimeEdit.text(), '%d.%m.%Y %H:%M')
        
        conn = Model().conn
        cur = conn.cursor()
        try:
            copyfile(self.file_name, f'img/{photo}')
            cur.execute('insert into user(login, password, photo, date_time) values (%s, %s, %s, %s)', (login, password, photo, date_time))
            conn.commit()
            QMessageBox.information(self, 'Done', "данные успешно добавлены")
            self.exit()
        except Exception as er:
            QMessageBox.warning(self, 'Ошибка', f'Ошибка вставки данных, возможно данные указаны неверно  {er}')
            print(er)
    
    def exit(self):
        self.card = CardApp()
        self.card.show()
        self.hide()
        