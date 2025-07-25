from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QMainWindow, QLabel, QVBoxLayout, QWidget, QComboBox
import requests
import json


class Ui_MainWindow(object):
    def __init__(self):
        super().__init__()
        # Initialize QStackedWidget
        self.central_stack = QtWidgets.QStackedWidget(self)
        self.setCentralWidget(self.central_stack)

        
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../Desktop/icon.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Label for drag and drop
        self.label = DropLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(230, 170, 301, 141))
        self.label.setText("Drag and drop a KML file here")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("border: 2px dashed #aaa; font-size: 16px; color: #555;")
        self.label.setObjectName("label")
        
        # Upload button
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(310, 340, 141, 31))
        self.pushButton.setObjectName("pushButton")
        
        # Next button
        self.nextButton = QtWidgets.QPushButton(self.centralwidget)
        self.nextButton.setGeometry(QtCore.QRect(310, 380, 141, 31))
        self.nextButton.setObjectName("nextButton")
        self.nextButton.setEnabled(False)  # Initially disabled
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        # Menu bar
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        # Menu actions
        self.actionUpload = QtWidgets.QAction(MainWindow)
        self.actionUpload.setObjectName("actionUpload")
        self.actionCopy_Ctrl_C = QtWidgets.QAction(MainWindow)
        self.actionCopy_Ctrl_C.setObjectName("actionCopy_Ctrl_C")
        self.actionPaste_Ctrl_V = QtWidgets.QAction(MainWindow)
        self.actionPaste_Ctrl_V.setObjectName("actionPaste_Ctrl_V")
        self.menuFile.addAction(self.actionUpload)
        self.menuEdit.addAction(self.actionCopy_Ctrl_C)
        self.menuEdit.addAction(self.actionPaste_Ctrl_V)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Connect the upload button to the function
        self.pushButton.clicked.connect(self.upload_file)
        
        # Connect the next button to move to the next page
        self.nextButton.clicked.connect(self.open_next_page)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "D-CAS"))
        self.pushButton.setText(_translate("MainWindow", "Upload"))
        self.nextButton.setText(_translate("MainWindow", "Next"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.actionUpload.setText(_translate("MainWindow", "Upload"))
        self.actionCopy_Ctrl_C.setText(_translate("MainWindow", "Copy(Ctrl+C)"))
        self.actionPaste_Ctrl_V.setText(_translate("MainWindow", "Paste(Ctrl+V)"))

    def upload_file(self):
        # Open a file dialog to select .kml files
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select KML File",
            "",
            "KML Files (*.kml);;All Files (*)",
            options=options
        )

        if file_path:
            try:
                # Send the file to the Django backend
                url = "http://127.0.0.1:8000/upload/"  # Adjust the URL to your Django server
                with open(file_path, 'rb') as f:
                    files = {'file': f}
                    response = requests.post(url, files=files)

                if response.status_code == 201:
                    QMessageBox.information(None, "File Uploaded", "File uploaded successfully to the backend!")
                    self.kml_file_name = file_path  # Store the file path
                    self.nextButton.setEnabled(True)  # Activate the Next button
                else:
                    QMessageBox.warning(None, "Upload Failed", f"Error: {response.json().get('error', 'Unknown error')}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")
        else:
            QMessageBox.warning(None, "No File", "No file was uploaded. Please select a .kml file.")

    def open_next_page(self):
        # Open the next page
        self.window = QMainWindow()
        self.ui = NextPage(self.kml_file_name)
        self.ui.setupUi(self.window)
        self.window.show()


class DropLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            # Check if the dragged file is a .kml file
            for url in event.mimeData().urls():
                if url.toLocalFile().endswith(".kml"):
                    event.accept()
                    return
        event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(".kml"):
                QMessageBox.information(self, "File Dropped", f"KML file uploaded successfully:\n{file_path}")
                self.parentWidget().parent().nextButton.setEnabled(True)
                return
        QMessageBox.warning(self, "Invalid File", "Only .kml files are allowed!")


class NextPage:
    def __init__(self, kml_file_name):
        self.kml_file_name = kml_file_name

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("NextPage")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Dropdown 1
        self.dropdown1 = QComboBox(self.centralwidget)
        self.dropdown1.setGeometry(QtCore.QRect(200, 200, 150, 30))
        self.dropdown1.addItem("Select Overlapping")
        self.dropdown1.addItems(["True", "False"])
        
        # Dropdown 2
        self.dropdown2 = QComboBox(self.centralwidget)
        self.dropdown2.setGeometry(QtCore.QRect(400, 200, 150, 30))
        self.dropdown2.addItem("Image Quality")
        self.dropdown2.addItems(["720 HD", "8K UHD"])
        
        # Next Button
        self.nextButton = QtWidgets.QPushButton(self.centralwidget)
        self.nextButton.setGeometry(QtCore.QRect(300, 300, 200, 40))
        self.nextButton.setText("Next")
        self.nextButton.setObjectName("nextButton")
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.nextButton.clicked.connect(self.open_third_page)


    def open_third_page(self):
        selected_option1 = self.dropdown1.currentText()
        selected_option2 = self.dropdown2.currentText()

        if selected_option1 == "Select Overlapping" or selected_option2 == "Image Quality":
            QMessageBox.warning(None, "Invalid Selection", "Please select valid options from both dropdowns.")
        else:
            # Proceed to the third page without sending options to the backend immediately
            self.window = QMainWindow()
            self.ui = ThirdPage(self.kml_file_name, selected_option1, selected_option2)
            self.ui.setupUi(self.window)
            self.window.show()


class ThirdPage:
    def __init__(self, kml_file_name, choice1, choice2):
        self.kml_file_name = kml_file_name
        self.choice1 = choice1
        self.choice2 = choice2

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("ThirdPage")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Labels for displaying data
        self.label1 = QLabel(f"KML File: {self.kml_file_name}", self.centralwidget)
        self.label1.setGeometry(QtCore.QRect(50, 50, 200, 30))
        
        self.label2 = QLabel(f"Choice 1: {self.choice1}", self.centralwidget)
        self.label2.setGeometry(QtCore.QRect(300, 50, 200, 30))
        
        self.label3 = QLabel(f"Choice 2: {self.choice2}", self.centralwidget)
        self.label3.setGeometry(QtCore.QRect(550, 50, 200, 30))
        
        # Big Button
        self.bigButton = QtWidgets.QPushButton("Start Generating Dataset", self.centralwidget)
        self.bigButton.setGeometry(QtCore.QRect(250, 200, 300, 60))
        self.bigButton.setObjectName("bigButton")
        
        # Progress Bar
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(150, 300, 500, 30))
        self.progressBar.setValue(0)
        self.progressBar.setObjectName("progressBar")
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        # Connect button to dataset generation
        self.bigButton.clicked.connect(self.start_generation_process)

    def start_generation_process(self):
        # Send the options to the Django backend
        url = "http://127.0.0.1:8000/process-options/"  # Adjust the URL to your Django server
        data = {
            "option1": self.choice1,
            "option2": self.choice2
        }
        try:
            # Send data to the backend and start dataset generation without interruption
            requests.post(url, json=data)
            self.generate_dataset()  # Start generating dataset immediately after passing values
        except Exception as e:
            QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")

    def generate_dataset(self):
        # Simulate dataset generation using QTimer
        self.progress_value = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)  # Update every 100ms

    def update_progress(self):
        if self.progress_value < 100:
            self.progress_value += 5  # Increment progress
            self.progressBar.setValue(self.progress_value)
        else:
            self.timer.stop()
            QMessageBox.information(None, "Dataset Generation", "Dataset generation completed successfully!")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
