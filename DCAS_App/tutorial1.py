from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow,self).__init__()
        self.setGeometry(400,400,500,500)
        self.setWindowTitle("AutomationAPP")
        self.initUI()

    def initUI(self):
        self.label= QtWidgets.QLabel(self)
        self.label.setText("kingo")
        self.label.move(175,175)

        self.b1= QtWidgets.QPushButton(self)
        self.b1.setText("Click me")
        self.b1.move(200,200)
        self.b1.clicked.connect(self.clicked)

    def clicked(self):
        self.label.setText("You clicked on me")
        self.update()
    
    def update(self):
        self.label.adjustSize()


def windows():
    app= QApplication(sys.argv)
    win= MyWindow()
    win.show()
    sys.exit(app.exec_())

windows()