from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QMainWindow, QLabel, QVBoxLayout, QWidget, QComboBox
import requests
import json
from PyQt5.QtGui import QIcon



class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("D-CAS")
        self.resize(800, 600)

        # Set the window icon (top image)
        self.setWindowIcon(QIcon("ade.png"))

        # Set the background image
        self.setStyleSheet("""
            QMainWindow {
                background-image: url('backgroundF.jpg');  /* Replace with your image file name */
                background-repeat: no-repeat;
                background-position: center;
                background-size: cover;  /* Adjust to cover the entire window */
            }
        """)

        # QStackedWidget to manage all pages
        self.central_stack = QtWidgets.QStackedWidget(self)
        self.setCentralWidget(self.central_stack)

        # Initialize pages
        self.main_page = MainPage(self)
        self.next_page = NextPage(self)
        self.third_page = ThirdPage(self)

        # Add pages to the stack
        self.central_stack.addWidget(self.main_page)
        self.central_stack.addWidget(self.next_page)
        self.central_stack.addWidget(self.third_page)

        # Connect navigation signals
        self.main_page.next_page_requested.connect(self.go_to_next_page)
        self.next_page.third_page_requested.connect(self.go_to_third_page)

    def go_to_next_page(self, kml_file_name):
        self.next_page.set_kml_file_name(kml_file_name)
        self.central_stack.setCurrentWidget(self.next_page)

    def go_to_third_page(self, kml_file_name, choice1, choice2):
        self.third_page.set_choices(kml_file_name, choice1, choice2)
        self.central_stack.setCurrentWidget(self.third_page)



class MainPage(QWidget):
    next_page_requested = QtCore.pyqtSignal(str)  # Signal to navigate to the next page

    def __init__(self, parent=None):
        super().__init__(parent)

        # Label for drag and drop
        self.label = DropLabel(self)
        self.label.setGeometry(QtCore.QRect(200, 120, 400, 300))
        self.label.setText("Upload a KML file")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("border: 2px dashed #aaa; font-size: 48px; color: white;")

        # Upload button
        self.pushButton = QtWidgets.QPushButton("Upload", self)
        self.pushButton.setGeometry(QtCore.QRect(300, 440, 200, 50))  # Increased size
        upload_font = QtGui.QFont()
        upload_font.setPointSize(19)  # Increase font size (e.g., 14pt)
        self.pushButton.setFont(upload_font)

        # Next button
        self.nextButton = QtWidgets.QPushButton("Next", self)
        self.nextButton.setGeometry(QtCore.QRect(300, 500, 200, 50))  # Increased size
        next_font = QtGui.QFont()
        next_font.setPointSize(19)
        self.nextButton.setFont(next_font)
        self.nextButton.setEnabled(False)  # Initially disabled

        # Connect signals
        self.pushButton.clicked.connect(self.upload_file)
        self.nextButton.clicked.connect(self.emit_next_page_signal)

    def upload_file(self):
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
                url = "http://127.0.0.1:8000/upload/"
                with open(file_path, 'rb') as f:
                    files = {'file': f}
                    response = requests.post(url, files=files)

                if response.status_code == 201:
                    QMessageBox.information(self, "File Uploaded", "File uploaded successfully to the backend!")
                    self.kml_file_name = file_path
                    self.nextButton.setEnabled(True)
                else:
                    QMessageBox.warning(self, "Upload Failed", f"Error: {response.json().get('error', 'Unknown error')}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "No File", "No file was uploaded. Please select a .kml file.")

    def emit_next_page_signal(self):
        self.next_page_requested.emit(self.kml_file_name)


class NextPage(QWidget):
    third_page_requested = QtCore.pyqtSignal(str, str, str)  # Signal to navigate to the third page

    def __init__(self, parent=None):
        super().__init__(parent)

        # Dropdown 1 (double width: 150 → 300, double height: 30 → 60)
        self.dropdown1 = QComboBox(self)
        self.dropdown1.setGeometry(QtCore.QRect(25, 200, 350, 60))
        self.dropdown1.setFont(QtGui.QFont("Arial", 24))
        self.dropdown1.addItem("Select Overlap")
        self.dropdown1.addItems(["True", "False"])

        # Dropdown 2 (placed beside dropdown1, same size)
        self.dropdown2 = QComboBox(self)
        self.dropdown2.setGeometry(QtCore.QRect(425, 200, 350, 60))
        self.dropdown2.setFont(QtGui.QFont("Arial", 24))
        self.dropdown2.addItem("Image Quality")
        self.dropdown2.addItems(["720 HD", "8K UHD"])

        # Next Button (original: 200x40 → now: 400x80)
        self.nextButton = QtWidgets.QPushButton("Next", self)
        self.nextButton.setGeometry(QtCore.QRect(200, 450, 400, 80))  # Centered (800 - 400)/2
        self.nextButton.setFont(QtGui.QFont("Arial", 24))
        self.nextButton.clicked.connect(self.emit_third_page_signal)


    def set_kml_file_name(self, kml_file_name):
        self.kml_file_name = kml_file_name

    def emit_third_page_signal(self):
        choice1 = self.dropdown1.currentText()
        choice2 = self.dropdown2.currentText()

        if choice1 == "Select Overlapping" or choice2 == "Image Quality":
            QMessageBox.warning(self, "Invalid Selection", "Please select valid options from both dropdowns.")
        else:
            self.third_page_requested.emit(self.kml_file_name, choice1, choice2)


class ThirdPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Labels for displaying data
        self.label1 = QLabel(self)
        self.label1.setGeometry(QtCore.QRect(50, 50, 200, 30))

        self.label2 = QLabel(self)
        self.label2.setGeometry(QtCore.QRect(300, 50, 200, 30))

        self.label3 = QLabel(self)
        self.label3.setGeometry(QtCore.QRect(550, 50, 200, 30))

        # Big Button
        self.bigButton = QtWidgets.QPushButton("Start Generating Dataset", self)
        self.bigButton.setGeometry(QtCore.QRect(250, 200, 300, 60))

        # Progress Bar
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setGeometry(QtCore.QRect(150, 300, 500, 30))
        self.progressBar.setValue(0)

        # Connect button to dataset generation
        self.bigButton.clicked.connect(self.start_generation_process)

    def set_choices(self, kml_file_name, choice1, choice2):
        self.label1.setText(f"KML File: {kml_file_name}")
        self.label2.setText(f"Choice 1: {choice1}")
        self.label3.setText(f"Choice 2: {choice2}")

        self.label1.setStyleSheet("color: white;")  # Change text color to red
        self.label2.setStyleSheet("color: white;")  # Change text color to blue
        self.label3.setStyleSheet("color: white;")  # Change text color to green


    def start_generation_process(self):
        # Backend logic 
        url = "http://127.0.0.1:8000/process-options/"
        data = {
            "option1": self.label2.text().split(": ")[1],
            "option2": self.label3.text().split(": ")[1]
        }
        try:
            requests.post(url, json=data)
            self.generate_dataset()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def generate_dataset(self):
        self.progress_value = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)

    def update_progress(self):
        if self.progress_value < 100:
            self.progress_value += 5
            self.progressBar.setValue(self.progress_value)
        else:
            self.timer.stop()
            QMessageBox.information(self, "Dataset Generation", "Dataset generation completed successfully!")


class DropLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
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
                self.parentWidget().nextButton.setEnabled(True)
                return
        QMessageBox.warning(self, "Invalid File", "Only .kml files are allowed!")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = Ui_MainWindow()
    main_window.show()
    sys.exit(app.exec_())
