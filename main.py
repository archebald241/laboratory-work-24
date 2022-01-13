import sys, os
import threading

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyautogui

from main_window import *
import login

userName = None
userGroup = None
resistance = None
errors = 0


class AuthWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.login = login.Ui_Form()
        self.login.setupUi(self)
        self.setWindowModality(2)

        self.validForm = False

        self.login.submit.clicked.connect(self.checkValidForm)

    def checkValidForm(self):
        global userName, userGroup, resistance

        name = self.login.lineEdit.text().strip()
        group = self.login.lineEdit_2.text().strip()
        res = self.login.comboBox.currentText()

        if len(name) > 0:
            userName = name
        if len(group) > 0:
            userGroup = group
        resistance = res

        if not (userName is None) and not (userGroup is None) and not (resistance is None):
            self.validForm = True
            self.close()
            myapp.show()
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка ввода данных", "Введены некорректные данные!")

    def closeEvent(self, value):
        if not self.validForm:
            raise SystemExit


class MyMain(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.u = 0
        self.i = 0
        # self.homePath = 'C:' + os.getenv('HOMEPATH') + '\Desktop\Отчет.png'

        self.ui.dial.valueChanged.connect(self.printValue)
        self.ui.submit.clicked.connect(self.checkResult)
        self.ui.chngForm.clicked.connect(self.chngForm)
        self.ui.coreAbsent.itemClicked.connect(self.autoInputValue)
        self.ui.corePartly.itemClicked.connect(self.autoInputValue)
        self.ui.coreFull.itemClicked.connect(self.autoInputValue)

        self.button_group = QButtonGroup()
        self.button_group.addButton(self.ui.radioButton)
        self.button_group.addButton(self.ui.radioButton_2)
        self.button_group.addButton(self.ui.radioButton_3)
        self.button_group.buttonClicked.connect(self.onRadioClicked)

    def showEvent(self, value):
        self.ui.label_11.setText(f'<html><head/><body><p><span style=" font-size:12pt;">R = {resistance}</span></p></body></html>')

    def autoInputValue(self):
        if self.button_group.checkedId() == -2:
            item = self.ui.coreAbsent.currentItem()
        elif self.button_group.checkedId() == -3:
            item = self.ui.corePartly.currentItem()
        elif self.button_group.checkedId() == -4:
            item = self.ui.coreFull.currentItem()

        if item.column() == 1:
            item.setText(str(self.i))
        elif item.column() == 2:
            item.setText(str(self.u))

    def chngForm(self):
        index = self.ui.stackedWidget.currentIndex()
        if index == 0:
            self.ui.stackedWidget.setCurrentIndex(1)
        else:
            self.ui.stackedWidget.setCurrentIndex(0)

    def printValue(self):
        l = 0
        if self.ui.radioButton.isChecked():
            l = 0.098
        elif self.ui.radioButton_2.isChecked():
            l = 0.139
        elif self.ui.radioButton_3.isChecked():
            l = 0.208

        z = (int(resistance.split(' ')[0]) ** 2 + (l * 314) ** 2) ** (1 / 2)
        self.u = round(self.ui.dial.value() / (2 ** (1 / 2)), 3)
        self.i = round((self.u / z), 3)

        textResistance = f'<html><head/><body><p align="center"><span style=" font-size:28pt;">{self.ui.dial.value()} В</span> </p></body></html>'
        textVolt = f'<html><head/><body><p align="center"><span style=" font-size:28pt; color: #E80E0E;">{self.u}</span></p></body></html>'
        textAmper = f'<html><head/><body><p align="center"><span style=" font-size:28pt; color: #E80E0E;">{self.i}</span></p></body></html>'

        self.ui.label.setText(textResistance)
        self.ui.voltCount.setText(textVolt)
        self.ui.ameprCount.setText(textAmper)

    def onRadioClicked(self, button):
        if button.objectName() == 'radioButton':
            self.ui.coreAbsent.setEnabled(True)
            self.ui.corePartly.setEnabled(False)
            self.ui.coreFull.setEnabled(False)
            self.ui.core.setGeometry(150, 20, 61, 121)
            self.ui.partlyCore.setGeometry(-1000, -1000, 61, 85)
            self.ui.headCore.setGeometry(-1000, -1000, 61, 51)
        elif button.objectName() == 'radioButton_2':
            self.ui.coreAbsent.setEnabled(False)
            self.ui.corePartly.setEnabled(True)
            self.ui.coreFull.setEnabled(False)
            self.ui.core.setGeometry(-1000, -1000, 61, 121)
            self.ui.partlyCore.setGeometry(58, 25, 61, 85)
            self.ui.headCore.setGeometry(-1000, -1000, 61, 51)
        elif button.objectName() == 'radioButton_3':
            self.ui.coreAbsent.setEnabled(False)
            self.ui.corePartly.setEnabled(False)
            self.ui.coreFull.setEnabled(True)
            self.ui.core.setGeometry(-1000, -1000, 61, 121)
            self.ui.partlyCore.setGeometry(-1000, -1000, 61, 85)
            self.ui.headCore.setGeometry(58, 61, 61, 51)

        textResistance = f'<html><head/><body><p align="center"><span style=" font-size:28pt;">0 В</span> </p></body></html>'
        textVolt = f'<html><head/><body><p align="center"><span style=" font-size:28pt; color: #E80E0E;">0</span></p></body></html>'
        textAmper = f'<html><head/><body><p align="center"><span style=" font-size:28pt; color: #E80E0E;">0</span></p></body></html>'

        self.ui.dial.setValue(0)
        self.ui.label.setText(textResistance)
        self.ui.voltCount.setText(textVolt)
        self.ui.ameprCount.setText(textAmper)

    def checkResult(self):
        global errors, userName, userGroup

        try:
            for i in range(0, 3):
                for j in range(1, 5):
                    if j < 4:
                        float(self.ui.coreAbsent.item(i, j).text())
                        float(self.ui.corePartly.item(i, j).text())
                        float(self.ui.coreFull.item(i, j).text())

                    elif j == 4:
                        if not (0.097 <= float(self.ui.coreAbsent.item(i, j).text()) <= 0.099):
                            errors += 1
                            QtWidgets.QMessageBox.warning(self, "Ошибка ввода данных", "Введены неверные данные в таблице 'Сердечник отсутствует'!")
                            return None

                        elif not (0.138 <= float(self.ui.corePartly.item(i, j).text()) <= 0.140):
                            errors += 1
                            QtWidgets.QMessageBox.warning(self, "Ошибка ввода данных", "Введены неверные данные в таблице 'Сердечник введен частично'!")
                            return None

                        elif not (0.207 <= float(self.ui.coreFull.item(i, j).text()) <= 0.209):
                            errors += 1
                            QtWidgets.QMessageBox.warning(self, "Ошибка ввода данных", "Введены неверные данные в таблице 'Сердечник введен полностью'!")
                            return None

        except ValueError:
            errors += 1
            QtWidgets.QMessageBox.warning(self, "Ошибка ввода данных", "Введены неверные данные!")
            return None

        m1 = f'{userName}, {userGroup}'
        m2 = f'Ошибок допущено: {errors}'
        self.ui.result.item(1, 0).setText(m1)
        self.ui.result.item(3, 0).setText(m2)

        exist = os.path.exists('/home/oleg/Teach/lab24/Отчет.png')
        if exist:
            os.remove('/home/oleg/Teach/lab24/Отчет.png')

        self.ui.result.setGeometry(QtCore.QRect(0, 0, 485, 220))
        self.ui.coreAbsent.setEnabled(True)
        self.ui.corePartly.setEnabled(True)
        self.ui.coreFull.setEnabled(True)

        event = threading.Event()
        thread = threading.Thread(target=self.screeShot, args=(event,))
        thread.start()

    def screeShot(self, event):
        event.wait(0.2)
        core = [self.geometry().x(), self.geometry().y(), self.geometry().width(), self.geometry().height()]
        pyautogui.screenshot('/home/oleg/Teach/lab24/Отчет.png', region=(core[0], core[1], core[2], core[3]))

        self.close()



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    auth = AuthWindow()
    auth.show()
    myapp = MyMain()
    sys.exit(app.exec_())
