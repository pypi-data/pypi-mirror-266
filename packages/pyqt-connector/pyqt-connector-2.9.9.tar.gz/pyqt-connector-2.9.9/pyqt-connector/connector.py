import datetime
import sys
import time
from random import randint

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QPixmap
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QLineEdit, QLabel, QComboBox, QFileDialog
from sqlalchemy import and_, update

from utils.model import Model

import phonenumbers



class Login(QtWidgets.QMainWindow):
    def __init__(self):
        super(Login, self).__init__()
        uic.loadUi('Windows/login_and_registr.ui', self)
        self.setWindowTitle('Вау, это вход!')
        self.setWindowIcon(QIcon('Source/icons/people_gesture_hand_man_icon_258682.ico'))

        self.label.setText('Вход')
        self.label_3.setText('')
        self.label_2.setText('Нету аккаунта?')

        self.lineEdit_2.setEchoMode(QLineEdit.Password)
        self.lineEdit_2.setPlaceholderText('Пароль')


        self.pushButton.setText('Вход')
        self.pushButton_2.setText('Регистрация')


        self.pushButton.setAutoDefault(True)
        self.pushButton.setDefault(True)
        self.pushButton.clicked.connect(self.log)
        self.pushButton_2.clicked.connect(self.reg_window)

    def log(self):
        login = self.lineEdit.text()
        password = self.lineEdit_2.text()
        cur = Model().conn.cursor()
        if len(login) != 0 or len(password) != 0:
            cur.execute("select id_role, id_user, photo_moderator from users where email_moderator = %s AND password_moderator = %s", (login, password))
            query = cur.fetchone()
            if query:
                if query[0] == 4:
                    self.profile = Profile(query[1], query[2])
                    self.hide()
                    self.profile.show()
            else:
                QMessageBox.information(self, 'Ошибка', 'Данный пользователь не найден', QMessageBox.Ok)



        else:
            self.label_3.setText("* Все поля должны быть заполнены!")

    def reg_window(self):
        self.reg_start_polling = Registration()
        self.reg_start_polling.show()
        self.hide()


class Registration(QtWidgets.QMainWindow):
    def __init__(self):
        super(Registration, self).__init__()
        uic.loadUi('Windows/login_and_registr.ui', self)
        self.setWindowTitle('Регистрация!')
        self.setWindowIcon(QIcon('Source/icons/people_gesture_hand_man_icon_258682.ico'))

        self.label.setText('Регистрация')
        self.label_3.setText('')
        self.label_2.setText('Есть аккаунт?')

        self.pushButton.setText('Регистрация')
        self.pushButton_2.setText('Войти')

        self.pushButton.clicked.connect(self.start_reg)
        self.pushButton_2.clicked.connect(self.log_window)

    def start_reg(self):
        login = self.lineEdit.text()
        password = self.lineEdit_2.text()
        session = Model().Session()
        query = session.query(Users.id_user).filter(and_(Users.login == login, Users.password == password)).first()

        if len(login) != 0 or len(password) != 0:
            if query is None:
                user = Users(
                    login=login,
                    password=password,
                    last_come=datetime.datetime.now(),
                    role_id=2
                )
                try:
                    session.add(user)
                    session.commit()
                    QMessageBox.information(self, "Регистрация", "Успешно создан аккаунт", QMessageBox.Ok)
                    self.log_window()

                except Exception as e:
                    self.label_3.setText('Ошибка вставки данных в бд')
            else:
                self.label.setText('Такой пользователь уже создан')
        else:
            self.label_3.setText("* Все поля должны быть заполнены!")

    def log_window(self):
        self.log_start_polling = Login()
        self.log_start_polling.show()
        self.hide()


class Profile(QMainWindow):
    def __init__(self, *args):
        super(Profile, self).__init__()
        self.args = args

        uic.loadUi('Windows/profile_organisator.ui', self)
        self.setWindowTitle('Профиль!')
        self.setWindowIcon(QIcon('Source/icons/people_gesture_hand_man_icon_258682.ico'))
        time_of_day = {
            (4, 12): "Доброе утро",
            (13, 17): "Добрый день",
            (17, 24): "Добрый вечер"
        }

        current_time = datetime.datetime.now().time().hour
        greeting = next((g for time, g in time_of_day.items() if time[0] <= current_time <= time[1]), "Доброй ночи")

        self.label_2.setText(f"{greeting}")

        self.label_3 = self.findChild(QLabel, 'label_3')
        self.pixmap = QPixmap(f'Source/image/{args[1]}')
        self.label_3.setPixmap(self.pixmap)

        self.pushButton = self.findChild(QtWidgets.QPushButton, 'pushButton')
        self.pushButton_2 = self.findChild(QtWidgets.QPushButton, 'pushButton_2')
        self.pushButton_3 = self.findChild(QtWidgets.QPushButton, 'pushButton_3')
        self.pushButton_4 = self.findChild(QtWidgets.QPushButton, 'pushButton_4')
        self.pushButton_5 = self.findChild(QtWidgets.QPushButton, 'pushButton_5')
        self.pushButton_6 = self.findChild(QtWidgets.QPushButton, 'pushButton_6')
        self.pushButton.setText('Жюри')
        self.pushButton_2.setText('Участники')
        self.pushButton_3.setText('Мероприятия')
        self.pushButton_4.setText('Профиль')
        self.pushButton_5.setText('ВЫХОД')
        self.pushButton_6.setText('Создать нового Жюри/Модератора')

        self.pushButton_4.clicked.connect(self.about_me)
        self.pushButton_5.clicked.connect(self.exit)
        self.pushButton_6.clicked.connect(self.New_moder_zuri)


    def about_me(self):
        cur = Model().conn.cursor()
        cur.execute("""
            select r.role, u.last_name, u.first_name, u.middle_name, u.sex, u.email_moderator, u.password_moderator, 
            u.birthday_date, c.country_name_ru, u.phone_number, d.direction
            from users u
                join roles r on u.id_role = r.id_role
                join country c on u.id_country = c.id_country 
                join directions d on u.id_direction = d.id_direction
            where u.id_user = %s;
        """, (str(self.args[0])))
        data = cur.fetchall()[0]
        text = f"""
            Вы - {data[0]}\n
            ФИО - {data[1]} {data[2]} {data[3]}\n
            пол - {data[4]}\n
            --------------------\n
            Логин - {data[5]}\n
            Пароль - {data[6]}\n
            --------------------\n
            Дата рождения - {data[7]}\n
            Страна - {data[8]}\n
            Номер телефона - {data[9]}\n
            Направление - {data[10]}
            
        """
        QMessageBox.information(self, 'Профиль', text, QMessageBox.Ok)

    def exit(self):
        self.log_start_polling = Login()
        self.log_start_polling.show()
        self.hide()

    def New_moder_zuri(self):
        self.form = NewModerOrZuri()
        self.hide()
        self.form.show()

class NewModerOrZuri(QMainWindow):
    def __init__(self):
        super(NewModerOrZuri, self).__init__()
        uic.loadUi('Windows/Create_new_moder_zuri.ui', self)

        with Model().conn.cursor() as cur:
            while True:
                self.number = randint(1, 10000)
                cur.execute("select id_user from users where id_user = %s",(str(self.number),))
                if cur.fetchone() is None:
                    break

        self.label.setText(f'Создания новой Фигуры номер - {self.number}')

        self.lineEdit_5 = self.findChild(QLineEdit, 'lineEdit_5')
        self.lineEdit_5.setInputMask('+7 000 000 00 00')
        self.lineEdit_8.setEchoMode(QLineEdit.Password)
        self.checkBox.stateChanged.connect(self.visible_password)

        self.load_combobox()

        self.pushButton.clicked.connect(self.place_photo)
        self.pushButton_2.clicked.connect(self.add_data_to_db)


    def add_data_to_db(self):
        with Model().conn.cursor() as cur:
            cur.execute("select id_role from roles where role = %s",(self.comboBox_role.currentText(),))
            role = cur.fetchone()[0]

            cur.execute("select id_counry from counry where counry_name_ru = %s",(self.comboBox_country.currentText(),))
            counry = cur.fetchone()[0]


            data = {
                'id_user': self.number,
                'id_role': role,
                'last_name': self.lineEdit.text(),
                'first_name': self.lineEdit_3.text(),
                'middle_name': self.lineEdit_2.text(),
                'sex': self.comboBox_sex.currentText().lower(),
                'email_moderator': self.lineEdit_7.text(),
                'birthday_date': self.dateEdit.text(),
                'id_counry': counry,
                # доделать

            }

    def place_photo(self):
        file_heandel = QFileDialog()
        image_path, _ = file_heandel.getOpenFileName(self, 'Выберите изображение', '', 'Image (*.png *.jpg *.jpeg)')

        if image_path:
            self.pixmap = QPixmap(image_path)
            self.label_2.setPixmap(self.pixmap.scaled(450, 450))
    def visible_password(self, state):
        if state == Qt.Checked:
            self.lineEdit_8.setEchoMode(QLineEdit.Normal)
        else:
            self.lineEdit_8.setEchoMode(QLineEdit.Password)

    def load_combobox(self):
        with Model().conn.cursor() as cur:
            self.comboBox_sex = self.findChild(QComboBox, 'comboBox')
            self.comboBox_sex.addItems(['М', 'Ж'])

            self.comboBox_role = self.findChild(QComboBox, 'comboBox_2')
            cur.execute("select role from roles")
            data = cur.fetchall()
            format_data = [item[0] for item in data]
            self.comboBox_role.addItems(format_data)

            self.comboBox_directions = self.findChild(QComboBox, 'comboBox_3')
            cur.execute("select direction from directions")
            data = cur.fetchall()
            format_data = [item[0] for item in data]
            self.comboBox_directions.addItems(format_data)

            self.comboBox_country = self.findChild(QComboBox, 'comboBox_4')
            cur.execute("select cou from directions")
            data = cur.fetchall()
            format_data = [item[0] for item in data]
            self.comboBox_directions.addItems(format_data)



class AdminProfile(QMainWindow):
    def __init__(self, *args):
        super(AdminProfile, self).__init__()
        uic.loadUi('Windows/admin_panel.ui', self)

        self.sort_order = Qt.AscendingOrder
        self.lineEdit.setPlaceholderText('Поиск по логину')
        self.pushButton.clicked.connect(self.filter_user)
        self.tableView.horizontalHeader().setSortIndicatorShown(True)
        self.tableView.horizontalHeader().setSortIndicator(0, Qt.DescendingOrder)
        self.tableView.setSortingEnabled(True)
        self.tableView.sortByColumn(0, Qt.AscendingOrder)


        self.load_data()

        self.setMinimumSize(1000, 1000)
        self.setMaximumSize(1000, 1000)

        self.tableView.clicked.connect(self.editing)

    def editing(self, index):
        row = index.row()
        id_column_index = 0
        id_item = self.table_model.item(row, id_column_index)
        # недописал
    def filter_user(self):
        filter_text = self.lineEdit.text()
        session = Model().Session()
        if filter_text:
            query = session.query(Users).filter(Users.login == filter_text).all()
            self.load_data(query)
        else:
            self.load_data(session.query(Users).all())


    def load_data(self, undata=None):

        session = Model().Session()
        if undata is not None:
            data = undata
        else:
            data = session.query(Users).all()
        if data:
            column_names = Users.__table__.columns.keys()
            num_rows = len(data)
            num_columns = len(column_names)

            self.table_model = QStandardItemModel(num_rows, num_columns)
            self.tableView.setModel(self.table_model)

            for row_index, user in enumerate(data):
                for col_index, column_name in enumerate(column_names):
                    cell_data = getattr(user, column_name)
                    item = QStandardItem(str(cell_data))
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                    self.table_model.setItem(row_index, col_index, item)
        else:
            print('Пусто')


class Editing(QMainWindow):
    def __init__(self):
        super(Editing, self).__init__()

        uic.loadUi('Windows/editing_win.ui', self)

        self.label.setText('Редактирование')

        self.lineEdit.setPlaceholderText('Логин')



if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    login = Login()
    login.show()

    sys.exit(app.exec_())