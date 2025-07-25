import sys, re, cv2, os, math, logging, joblib, datetime
import concurrent.futures
import matplotlib.pyplot as plt
import numpy as np
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QPointF, QTimer, QTime, QRectF, QDateTime
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QLineEdit, QLabel, QGraphicsPixmapItem, QWidget, QGraphicsView, QFileDialog, QPushButton
from PyQt5.QtGui import QPixmap, QImage, QTransform, QPainter, QPen, QColor, QPolygonF, QBrush
from geopy.distance import geodesic


class Simulation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DSMAC Simulation")
        self.setGeometry(0, 0, 2048, 1280)

        self.scene = QGraphicsScene(self)
        self.graphicsView = QGraphicsView(self.scene, self)
        self.graphicsView.setGeometry(10, 10, 1440, 900)
        self.graphicsView.setRenderHint(QPainter.Antialiasing)
        self.graphicsView.setRenderHint(QPainter.SmoothPixmapTransform)
        self.graphicsView.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

        scale_factor = 6.5  # Change this value to adjust the size

        trianglePoints = [
            QPointF(0 * scale_factor, -20 * scale_factor),
            QPointF(-17.32 * scale_factor, 10 * scale_factor),
            QPointF(17.32 * scale_factor, 10 * scale_factor),
        ]

        trainglePolygon = QPolygonF(trianglePoints)
        self.plane = QtWidgets.QGraphicsPolygonItem(trainglePolygon)
        self.plane.setBrush(QBrush(Qt.blue))
        self.plane.setPen(QPen(Qt.black, 2))
        self.plane.setZValue(2)
        self.scene.addItem(self.plane)

        
        self.pixmap_item = None
        self.zoom_level = 1.0
        self.captureTimer = QTimer(self)
        self.animationTimer = QTimer(self)
        self.animationTimer.timeout.connect(self.move_plane)
        self.currentIndex = 0
        self.currentTime = 0
        self.captureDir = "Captured_Images"
        os.makedirs(self.captureDir, exist_ok=True)
        self.orbLogFile = f'ORB Log File{self.currentTime}'
        self.inputFile = None
        self.outputFile = None
        self.last_time = None
        self.capture_rate = 1

        # Create a QFont object
        font = QtGui.QFont()
        font.setPointSize(10)  # Adjust the font size as needed
        font1 = QtGui.QFont()
        font1.setPointSize(9)  # Adjust the font size as needed

        self.loadImageButton = QtWidgets.QPushButton('Load Image', self)
        self.loadImageButton.setGeometry(1500, 100, 150, 50)
        self.loadImageButton.setFont(font)  # Apply font to the button
        self.loadImageButton.clicked.connect(self.loadImage)

        self.loadInfoButton = QtWidgets.QPushButton("Load Path", self)
        self.loadInfoButton.setGeometry(1575, 240, 150, 50)
        self.loadInfoButton.setFont(font)  # Apply font
        self.loadInfoButton.clicked.connect(self.loadPathAndData)

        self.startSimulationButton = QtWidgets.QPushButton("Start Flying", self)
        self.startSimulationButton.setGeometry(1575, 300, 150, 50)
        self.startSimulationButton.setFont(font)  # Apply font
        self.startSimulationButton.clicked.connect(self.startSimulation)
        self.startSimulationButton.setEnabled(False)

        self.resetButton = QtWidgets.QPushButton("Reset", self)
        self.resetButton.setGeometry(1660, 100, 150, 50)
        self.resetButton.setFont(font)  # Apply font
        self.resetButton.clicked.connect(self.resetImage)

        self.applyButton = QtWidgets.QPushButton("Apply", self)
        self.applyButton.setGeometry(1500, 160, 150, 50)
        self.applyButton.setFont(font)  # Apply font
        self.applyButton.clicked.connect(self.applyManipulation)

        self.weatherCondition = QtWidgets.QComboBox(self)
        self.weatherCondition.addItems(["Select Effect", "Rainy", "Foggy", "Sunny", "Snowy"])
        self.weatherCondition.setGeometry(1660, 160, 150, 50)
        self.weatherCondition.setFont(font)  # Apply font

        self.topLeftLatLabel = QLabel("TopLeft Y Coord(DD)   :", self)
        self.topLeftLatLabel.setGeometry(1480, 390, 190, 50)
        self.topLeftLatLabel.setFont(font1)  # Apply font
        self.topLeftLat = QLineEdit(self)
        self.topLeftLat.setGeometry(1690, 390, 190, 50)
        self.topLeftLat.setText("28.7380")
        self.topLeftLat.setFont(font)  # Apply font

        self.topLeftLonLabel = QLabel("TopLeft X Coord(DD)   :", self)
        self.topLeftLonLabel.setGeometry(1480, 450, 190, 50)
        self.topLeftLonLabel.setFont(font1)  # Apply font
        self.topLeftLon = QLineEdit(self)
        self.topLeftLon.setGeometry(1690, 450, 190, 50)
        self.topLeftLon.setText("77.0105")
        self.topLeftLon.setFont(font)  # Apply font

        self.bottomRightLatLabel = QLabel("Bot.Right Y Coord(DD) :", self)
        self.bottomRightLatLabel.setGeometry(1480, 510, 190, 50)
        self.bottomRightLatLabel.setFont(font1)  # Apply font
        self.bottomRightLat = QLineEdit(self)
        self.bottomRightLat.setGeometry(1690, 510, 190, 50)
        self.bottomRightLat.setText("28.7321")
        self.bottomRightLat.setFont(font)  # Apply font

        self.bottomRightLonLabel = QLabel("Bot.Right X Coord(DD) :", self)
        self.bottomRightLonLabel.setGeometry(1480, 570, 190, 50)
        self.bottomRightLonLabel.setFont(font1)  # Apply font
        self.bottomRightLon = QLineEdit(self)
        self.bottomRightLon.setGeometry(1690, 570, 190, 50)
        self.bottomRightLon.setText("77.0229")
        self.bottomRightLon.setFont(font)  # Apply font
      
        self.load_button = QPushButton('LatLong to DD', self)
        self.load_button.clicked.connect(self.extract_lat_long)
        self.load_button.setGeometry(1575, 715, 150, 50)
        self.load_button.setFont(font)  # Apply font

        self.weatherCondition = QtWidgets.QComboBox(self)
        self.weatherCondition.addItems(["Select Model", "ORB", "FAISS"])
        self.weatherCondition.setGeometry(1500, 650, 150, 50)
        self.weatherCondition.setFont(font)  # Apply font


        self.performORBButton = QPushButton("Run Model", self)
        self.performORBButton.clicked.connect(self.runORBModel)
        self.performORBButton.setGeometry(1660, 650, 150, 50)
        self.performORBButton.setFont(font)  # Apply font

        self.convertCoordsButton = QPushButton("Plot Lines", self)
        self.convertCoordsButton.clicked.connect(self.drawLinesBetweenPositions)
        self.convertCoordsButton.setGeometry(1660, 780, 150, 50)
        self.convertCoordsButton.setFont(font)  # Apply font

        self.plotComparisonButton = QPushButton("Plot Graph", self)
        self.plotComparisonButton.clicked.connect(self.compare_coordinates_from_files)
        self.plotComparisonButton.setGeometry(1575, 860, 150, 50)
        self.plotComparisonButton.setFont(font)  # Apply font

        self.cleanCoordsButton = QPushButton("Plot Points", self)
        self.cleanCoordsButton.clicked.connect(self.readPointsToPlot)
        self.cleanCoordsButton.setGeometry(1500, 780, 150, 50)
        self.cleanCoordsButton.setFont(font)  # Apply font

    def drawLinesBetweenPositions(self):
        plane_file_path, _ = QFileDialog.getOpenFileName(self, "Select Plane Positions File", "", "Text Files (*.txt);;All Files (*)")
        if not plane_file_path:
            print("No plane positions file selected.")
            return

        # Open dialog to select identified positions file
        identified_file_path, _ = QFileDialog.getOpenFileName(self, "Select Identified Positions File", "", "Text Files (*.txt);;All Files (*)")
        if not identified_file_path:
            print("No identified positions file selected.")
            return

        # Validate map bounds before proceeding
        try:
            topLeftLat = float(self.topLeftLat.text())
            topLeftLon = float(self.topLeftLon.text())
            bottomRightLat = float(self.bottomRightLat.text())
            bottomRightLon = float(self.bottomRightLon.text())
            if not (topLeftLat > bottomRightLat and topLeftLon < bottomRightLon):
                QtWidgets.QMessageBox.warning(self, "Coordinate Error",
                    "Top-Left coordinates must be greater than Bottom-Right coordinates\n"
                    "(Latitude: top > bottom, Longitude: left < right).")
                return
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Input Error",
                "Please enter valid numeric values for Top-Left and Bottom-Right coordinates.")
            return

        # Parse plane positions
        plane_positions = {}
        try:
            with open(plane_file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(". ", 1)
                    if len(parts) != 2:
                        print(f"Skipping malformed plane position line: '{line}'")
                        continue
                    name, coords = parts
                    lat_lon = [float(c.strip()) for c in coords.split(",")]
                    if len(lat_lon) != 2:
                        print(f"Skipping invalid plane coordinates: '{line}'")
                        continue
                    plane_positions[name] = (lat_lon[0], lat_lon[1])
        except Exception as e:
            print(f"Error reading plane positions file '{plane_file_path}': {e}")
            return

        # Parse identified positions
        identified_positions = {}
        try:
            with open(identified_file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(". ", 1)
                    if len(parts) != 2:
                        print(f"Skipping malformed identified position line: '{line}'")
                        continue
                    name, coords = parts
                    lat_lon = [float(c.strip()) for c in coords.split(",")]
                    if len(lat_lon) != 2:
                        print(f"Skipping invalid identified coordinates: '{line}'")
                        continue
                    identified_positions[name] = (lat_lon[0], lat_lon[1])
        except Exception as e:
            print(f"Error reading identified positions file '{identified_file_path}': {e}")
            return

        # Match and draw lines
        line_pen = QPen(QColor(255, 192, 203), 20)  # Pink line, width 2
        width = 19200
        height = 9640
        scaleX = width / (bottomRightLon - topLeftLon)
        scaleY = height / (topLeftLat - bottomRightLat)

        scaleX_forPlane = self.graphicsView.width() / (bottomRightLon - topLeftLon)
        scaleY_forPlane = self.graphicsView.height() / (topLeftLat - bottomRightLat)

        for name in plane_positions:
            if name in identified_positions:
                plane_lat, plane_lon = plane_positions[name]
                ident_lat, ident_lon = identified_positions[name]

                # Convert to pixel coordinates
                plane_x = (plane_lon - topLeftLon) * scaleX
                plane_y = (topLeftLat - plane_lat) * scaleY
                ident_x = (ident_lon - topLeftLon) * scaleX
                ident_y = (topLeftLat - ident_lat) * scaleY

                # Draw line
                self.scene.addLine(plane_x, plane_y, ident_x, ident_y, line_pen)
                print(f"Drew line for {name}: ({plane_lat}, {plane_lon}) -> ({ident_lat}, {ident_lon})")

                # Optionally plot points for visibility
                point_pen = QPen(QColor(255, 0, 0), 20)
                self.scene.addEllipse(plane_x - 5, plane_y - 5, 10, 10, point_pen)
                self.scene.addEllipse(ident_x - 5, ident_y - 5, 10, 10, point_pen)

        self.graphicsView.viewport().update()
        print("Line drawing complete.")

    def readPointsToPlot(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Select Position File", "", "Text Files (*.txt);;All Files (*)")
        if not filePath:
            print("No file selected.")
            return

        try:
            with open(filePath, "r") as file:
                for line in file:
                    parts = line.strip().split(". ", 1)
                    if len(parts) != 2:
                        continue
                    
                    coords = parts[1].strip().split(",")
                    if len(coords) != 2:
                        continue

                    lat, lon = float(coords[0].strip()), float(coords[1].strip())
                    self.plotPointsOnMap(lat, lon)
        except Exception as e:
            print(f"Error reading file: {e}")

    def plotPointsOnMap(self, lat, lon):
        topLeftLat = float(self.topLeftLat.text())
        topLeftLon = float(self.topLeftLon.text())
        bottomRightLat = float(self.bottomRightLat.text())
        bottomRightLon = float(self.bottomRightLon.text())

        width = 19200
        height = 9640

        if not (topLeftLat > bottomRightLat and topLeftLon < bottomRightLon):
            print("Error: Top-Left coordinates should be greater than Bottom-Right coordinates.")
            return

        # Correct scale calculations
        scaleX = width / (bottomRightLon - topLeftLon)
        scaleY = height / (topLeftLat - bottomRightLat)

        diffX = lon - topLeftLon
        diffY = topLeftLat - lat

        scaledX = diffX * scaleX
        scaledY = diffY * scaleY

        pointPen = QPen(QColor(255, 0, 0), 50)
        self.scene.addEllipse(scaledX - 5, scaledY - 5, 10, 10, pointPen)
        #print(f"Plotted point on map: {lat}, {lon}")

    def pixelToLatLon(self, x, y):
        topLeftLat = float(self.topLeftLat.text())
        topLeftLon = float(self.topLeftLon.text())
        bottomRightLat = float(self.bottomRightLat.text())
        bottomRightLon = float(self.bottomRightLon.text())
        mapWidth = 19200
        mapHeight = 9640
        latRange = topLeftLat - bottomRightLat
        lonRange = bottomRightLon - topLeftLon

        lat = topLeftLat - (y / mapHeight) * latRange
        lon = topLeftLon + (x / mapWidth) * lonRange

        return lat, lon

    def loadImage(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.image = cv2.imread(file_path)
            if self.image is None:
                print("Error: Could not load image from path:", file_path)
                return
        self.originalImage = self.image.copy()
        self.display_image(self.image)

    def display_image(self, image):
        if image is None:
            return
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        if self.pixmap_item is None:
            self.pixmap_item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(self.pixmap_item)
        else:
            self.pixmap_item.setPixmap(pixmap)

        self.scene.setSceneRect(self.pixmap_item.boundingRect())

    def loadPathAndData(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Path and Data File", "", "Text Files (*.txt)")
        if fileName:
            self.wayPoints = []
            self.speeds = []
            self.altitudes = []
            self.wayPoints, self.speeds, self.altitudes = self.readPathAndData(fileName)
            if self.wayPoints and self.speeds and self.altitudes:
                self.drawPathandWaypoints()
                self.startSimulationButton.setEnabled(True)

    def move_plane(self):
        if not self.wayPoints or self.currentIndex >= len(self.wayPoints):
            self.timer.stop()
            self.captureTimer.stop()
            return

        now = QTime.currentTime()
        elapsed_time = self.last_time.msecsTo(now) / 1000.0 if self.last_time else 0
        self.last_time = now

        start_point = self.plane.pos()
        end_point = self.wayPoints[self.currentIndex]

        dx = end_point.x() - start_point.x()
        dy = end_point.y() - start_point.y()
        distance_to_waypoint = math.sqrt(dx**2 + dy**2)

        distance_to_cover = self.speeds[self.currentIndex - 1] * elapsed_time

        if distance_to_cover >= distance_to_waypoint:
            self.plane.setPos(end_point)
            self.currentIndex += 1
            if self.currentIndex >= len(self.wayPoints):
                self.animationTimer.stop()
                self.captureTimer.stop()
                return
            else:
                self.last_time = QTime.currentTime()
                return

        angle = math.atan2(dy, dx)
        dx_move = distance_to_cover * math.cos(angle)
        dy_move = distance_to_cover * math.sin(angle)

        self.plane.moveBy(dx_move, dy_move)

        transform = QTransform()
        transform.rotate(math.degrees(angle))
        self.plane.setTransform(transform)

        if self.currentTime % int(self.capture_rate) == 0:
            self.captureImage()

        self.currentTime += 1
    
    def captureImage(self):
        if not self.wayPoints or self.currentIndex >= len(self.wayPoints) or self.pixmap_item is None:
            print("Capture skipped: No waypoints or invalid index")
            return

        # Define ROI dimensions
        roi_width, roi_height = 1920, 964
        planePos = self.plane.scenePos()
        roi_x, roi_y = planePos.x() - roi_width / 2, planePos.y() - roi_height / 2
        roi = QRectF(roi_x, roi_y, roi_width, roi_height)

        # Capture image from scene
        image = QImage(int(roi.width()), int(roi.height()), QImage.Format_RGB888)
        painter = QPainter(image)
        self.scene.render(painter, target=QRectF(0, 0, roi.width(), roi.height()), source=roi)
        painter.end()

        plane_x, plane_y = planePos.x(), planePos.y()
        lat, lon = self.pixelToLatLon(plane_x, plane_y)

        if self.currentIndex < len(self.wayPoints):
            targetPos = self.wayPoints[self.currentIndex]
            dx, dy = targetPos.x() - plane_x, targetPos.y() - plane_y
            angle = math.atan2(dy, dx)

            transform = QTransform()
            transform.rotate(math.degrees(angle))
            rotatedImage = image.transformed(transform, mode=Qt.SmoothTransformation)

            self.captureImagesFolder = "Captured_images"
            os.makedirs(self.captureImagesFolder, exist_ok=True)

            existingFiles = [f for f in os.listdir(self.captureImagesFolder) if f.endswith(".png")]
            existingNumbers = [int(f.split(".")[0]) for f in existingFiles if f.split(".")[0].isdigit()]
            nextImageNumber = max(existingNumbers, default=0) + 1

            fileName = f"{nextImageNumber}.png"
            filePath = os.path.join(self.captureImagesFolder, fileName)
            success = rotatedImage.save(filePath)

            if success:
                print(f"Image saved: {filePath}")

                log_file_path = os.path.join(os.getcwd(), "plane_positions.txt")
                log_entry = f"{nextImageNumber}. {lat}, {lon}\n"

                try:
                    with open(log_file_path, "a") as file:
                        file.write(log_entry)
                    print(f"Position logged: {log_entry.strip()} in {log_file_path}")
                except Exception as e:
                    print(f"Error writing to file: {e}")
            else:
                print(f"Error saving image: {filePath}")
        else:
            print("Stopping captureTimer: No more waypoints.")
            self.captureTimer.stop()
    
    def readPathAndData(self, fileName):
        wayPoints = []
        speeds = []
        altitudes = []
        try:
            with open(fileName, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    parts = line.strip().split(',')
                    if len(parts) == 4:
                        try:
                            x = float(parts[0])
                            y = float(parts[1])
                            speed = float(parts[2])
                            altitude = float(parts[3])
                            wayPoints.append(QPointF(x, y))
                            speeds.append(speed)
                            altitudes.append(altitude)
                        except ValueError:
                            print(f"Error converting line: {line}")
        except FileNotFoundError:
            print(f"Error: File not found: {fileName}")
        except Exception as e:
            print(f"Error reading path and data: {e}")
        return wayPoints, speeds, altitudes
    
    def drawPathandWaypoints(self):
            pathPen = QPen(QColor(57, 255, 20), 40)
            for i in range(len(self.wayPoints) - 1):
                startPoint = self.wayPoints[i]
                endPoint = self.wayPoints[i + 1]
                self.scene.addLine(startPoint.x(), startPoint.y(), endPoint.x(), endPoint.y(), pathPen)

            wayPointPen = QPen(QColor(128, 0, 128), 50)
            wayPointBrush = QBrush(QColor(128, 0, 128))
            radius = 10
            diameter = radius * 2
            wayPointPen.setWidth(2)
            for wayPoint in self.wayPoints:
                self.scene.addEllipse(wayPoint.x() - radius, wayPoint.y() - radius, diameter, diameter, wayPointPen, wayPointBrush)

    def startSimulation(self):
        if self.wayPoints:
            self.current_waypoint_index = 0
            self.animation_progress = 0.0
            self.plane.setPos(self.wayPoints[0])
            self.animationTimer.start(16)
            self.captureTimer.start(200)
            self.currentTime = 0
    
    def applyManipulation(self):
        if self.image is None:
            return

        selected_effect = self.weatherCondition.currentText()
        if selected_effect == "Select Effect":
            return

        manipulation_function = {
            "Rainy": self.add_rain_effect,
            "Foggy": self.add_fog_effect,
            "Sunny": self.add_sunny_effect,
            "Snowy": self.add_snow_effect,
        }.get(selected_effect)

        if manipulation_function:
            manipulated_image = manipulation_function(self.image)
            self.display_image(manipulated_image)
            self.image = manipulated_image

    def resetImage(self):
        if self.originalImage is None:
            return
        self.image = self.originalImage.copy()
        self.display_image(self.image)
        self.zoom_level = 1.0
        self.update_view()
    
    def update_view(self):
        if self.pixmap_item is not None:
            transform = QTransform()
            transform.scale(self.zoom_level, self.zoom_level)
            self.graphicsView.setTransform(transform)
            self.graphicsView.centerOn(self.pixmap_item)
        
    def add_rain_effect(self, image):
        rain_layer = np.zeros_like(image, dtype=np.uint8)
        for _ in range(10000):
            x1, y1 = np.random.randint(0, image.shape[1]), np.random.randint(0, image.shape[0])
            x2, y2 = x1 + np.random.randint(-10, 10), y1 + np.random.randint(20, 50)
            cv2.line(rain_layer, (x1, y1), (x2, y2), (200, 200, 200), 1)
        blended = cv2.addWeighted(image, 0.8, rain_layer, 0.2, 0)
        return cv2.GaussianBlur(blended, (5, 5), 0)

    def add_fog_effect(self, image):
        fog_layer = np.full_like(image, 255, dtype=np.uint8)
        foggy_image = cv2.addWeighted(image, 0.7, fog_layer, 0.3, 0)
        return cv2.GaussianBlur(foggy_image, (15, 15), 0)

    def add_sunny_effect(self, image):
        brightened = cv2.convertScaleAbs(image, alpha=1.2, beta=30)
        return brightened

    def add_snow_effect(self, image, flake_count=2000):
        snow_layer = np.zeros_like(image, dtype=np.uint8)
        for _ in range(flake_count):
            x, y = np.random.randint(0, image.shape[1]), np.random.randint(0, image.shape[0])
            cv2.circle(snow_layer, (x, y), 1, (255, 255, 255), -1)
        snow_image = cv2.addWeighted(image, 0.8, snow_layer, 0.2, 0)
        return cv2.GaussianBlur(snow_image, (5, 5), 0)

    def update_view(self):
        if self.pixmap_item is not None:
            transform = QTransform()
            transform.scale(self.zoom_level, self.zoom_level)
            self.graphicsView.setTransform(transform)
            self.graphicsView.centerOn(self.pixmap_item)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def zoom_in(self):
        current_scale = self.graphicsView.transform().m11()
        
        if current_scale < 3.0:
            self.graphicsView.scale(1.1, 1.1)

    def zoom_out(self):
        current_scale = self.graphicsView.transform().m11()
        
        if current_scale > 0.1:
            self.graphicsView.scale(1 / 1.1, 1 / 1.1)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_Equal:
                self.zoom_in()
            elif event.key() == Qt.Key_Minus:
                self.zoom_out()
    
    def load_points_from_file(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Points File", "", "Text Files (*.txt)")
        if fileName:
            points = []
            try:
                with open(fileName, 'r') as file:
                    lines = file.readlines()
                    for line in lines:
                        if "Latitude-Longitude:" in line:
                            parts = line.strip().split("Latitude-Longitude:")[1].split(',')
                            if len(parts) == 2:
                                try:
                                    lat = float(parts[0].strip())
                                    lon = float(parts[1].strip())
                                    points.append((lat, lon))
                                except ValueError:
                                    print(f"Error converting line: {line}")
                        else:
                            print(f"Skipping invalid line: {line}")

            except FileNotFoundError:
                print(f"Error: File not found: {fileName}")
            except Exception as e:
                print(f"Error reading points file: {e}")

            try:
                self.top_left_lat = float(self.topLeftLat.text())
                self.top_left_lon = float(self.topLeftLon.text())
                self.bottom_right_lat = float(self.bottomRightLat.text())
                self.bottom_right_lon = float(self.bottomRightLon.text())
            except ValueError:
                print("Error: Invalid input for reference points.")
                return

            self.plot_points_on_map(points)
        
    def plot_points_on_map(self, points):
        width = self.graphicsView.width()
        height = self.graphicsView.height()

        if not (self.top_left_lat > self.bottom_right_lat and self.top_left_lon < self.bottom_right_lon):
            print("Error: Top-left coordinates should be greater than bottom-right coordinates.")
            return

        scale_x = width / (self.top_left_lon - self.bottom_right_lon)
        scale_y = height / (self.top_left_lat - self.bottom_right_lat)

        pointPen = QPen(QColor(0, 255, 255), 50)

        for lat, lon in points:
            if (self.bottom_right_lat <= lat <= self.top_left_lat) and (self.top_left_lon <= lon <= self.bottom_right_lon):
                diff_x = self.top_left_lon - lon
                diff_y = self.top_left_lat - lat

                scaled_x = diff_x * scale_x
                scaled_y = diff_y * scale_y

                self.scene.addEllipse(scaled_x - 5, scaled_y - 5, 10, 10, pointPen)
            else:
                print(f"Point ({lat}, {lon}) is outside the defined area and will not be plotted.")
    
    def runORBModel(self):
        test_folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        model_data = load_100m_model()
        lat_long_mapping = load_lat_long_mapping()
        process_folder(test_folder, model_data, lat_long_mapping, output_file_path="output.txt")
    
    def extract_lat_long(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open ORB Output File", "", "Text Files (*.txt);;All Files (*)")
        if not file_path:
            print("No file selected.")
            return []

        def dms_to_decimal(dms_str, is_longitude=False):
            try:
                parts = re.split(r'\s+', dms_str.strip())
                if len(parts) < 3:
                    raise ValueError("Expected at least 3 values (degrees, minutes, seconds)")
                
                degrees = float(parts[0])
                minutes = float(parts[1])
                seconds = float(parts[2])

                # Handle additional precision for latitude (e.g., "96" in "28 44 15 96")
                if len(parts) > 3 and not is_longitude:
                    hundredths = float(parts[3]) / 100  # Treat as hundredths of a second
                    seconds += hundredths
                
                # Handle decimal seconds for longitude (e.g., "39.93" split as "39" and ".93")
                if is_longitude and "." in parts[2]:
                    seconds = float(parts[2])  # Already includes decimal

                return degrees + (minutes / 60) + (seconds / 3600)
            except Exception as e:
                raise ValueError(f"Invalid DMS format: {dms_str} ({e})")

        extracted_waypoints = []
        current_image_name = None

        try:
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue

                    # Extract image name from "Processing:" line without extension
                    if "Processing:" in line:
                        full_path = line.split("Processing:")[1].strip()
                        base_name = os.path.basename(full_path)  # e.g., "1.png" from "/1.png"
                        current_image_name = os.path.splitext(base_name)[0]  # e.g., "1" from "1.png"
                        continue

                    # Process latitude-longitude line if we have an image name
                    if "Latitude-Longitude:" in line and current_image_name:
                        try:
                            latlong_str = line.split("Latitude-Longitude:")[1].strip()
                            lat_dms_str, long_dms_str = map(str.strip, latlong_str.split(","))

                            latitude = dms_to_decimal(lat_dms_str)
                            longitude = dms_to_decimal(long_dms_str, is_longitude=True)

                            # Store as tuple with image name
                            extracted_waypoints.append((current_image_name, latitude, longitude))

                        except (ValueError, IndexError) as e:
                            print(f"Skipped invalid lat-long entry for {current_image_name}: {line} ({e})")
                            logging.exception(f"Error parsing lat-long: {e}")

        except FileNotFoundError:
            print(f"File not found: {file_path}")
            logging.error(f"File not found: {file_path}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception(f"An unexpected error occurred: {e}")

        self.recognisedWaypoints = extracted_waypoints

        # Save to file with image name prefix (no extension)
        save_file_path, _ = QFileDialog.getSaveFileName(self, "Save Waypoints", "", "Text Files (*.txt);;All Files (*)")
        if save_file_path:
            try:
                with open(save_file_path, 'w') as save_file:
                    for image_name, lat, lon in extracted_waypoints:
                        save_file.write(f"{image_name}. {lat}, {lon}\n")
                print(f"Waypoints saved to {save_file_path}")
            except Exception as e:
                print(f"Failed to save waypoints: {e}")
                logging.exception(f"Failed to save waypoints: {e}")

        return extracted_waypoints
    
    def open_and_clean_file(self):
        input_file, _ = QFileDialog.getOpenFileName(None, "Select Input File", "", "Text Files (*.txt)")
        if not input_file:
            print("No input file selected.")
            return

        output_file, _ = QFileDialog.getSaveFileName(None, "Save Output File", "", "Text Files (*.txt)")
        if not output_file:
            print("No output file selected.")
            return

        try:
            self.convert_clean_and_convert_dms_file(input_file, output_file)
            print(f"File conversion complete. Output saved to: {output_file}")
        except Exception as e:
            print(f"An error occurred: {e}")
        
    def convert_clean_and_convert_dms_file(self, input_file, output_file):
        if not isinstance(input_file, (str, bytes, os.PathLike)):
            raise TypeError(f"Expected a file path, but got {type(input_file)}")
        if not isinstance(output_file, (str, bytes, os.PathLike)):
            raise TypeError(f"Expected a file path, but got {type(output_file)}")

        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                if "Latitude-Longitude" in line:
                    image_name, coords = self.process_line(line)
                    cleaned_coords = self.remove_decimal(coords)
                    lat_dms, lon_dms = cleaned_coords.split(", ")
                    lat_decimal = self.dms_to_decimal(lat_dms)
                    lon_decimal = self.dms_to_decimal(lon_dms)
                    if lat_decimal is not None and lon_decimal is not None:
                        outfile.write(f"{image_name}: {lat_decimal}, {lon_decimal}\n")

    def extractCoordsComparison(self, file_path):
        coords = {}
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split('.', 1)
                    if len(parts) != 2:
                        continue
                    index = parts[0].strip()
                    coord_part = parts[1].strip()
                    lat_lon = coord_part.split(',')
                    if len(lat_lon) != 2:
                        continue
                    try:
                        lat = float(lat_lon[0].strip())
                        lon = float(lat_lon[1].strip())
                        coords[index] = (lat, lon)
                    except ValueError:
                        print(f"Skipping invalid coordinate in {file_path}: {line}")
                        continue
            return coords
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return {}

    def compare_coordinates_from_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(None, "Select ORB Output Files", "", "Text Files (*.txt);;All Files (*)")

        if len(file_paths) != 2:
            print("Please select exactly two files for comparison.")
            return

        coords1 = self.extractCoordsComparison(file_paths[0])
        coords2 = self.extractCoordsComparison(file_paths[1])

        if not coords1 or not coords2:
            print("Could not extract coordinates from one or both files.")
            return

        file_name1 = os.path.basename(file_paths[0])
        file_name2 = os.path.basename(file_paths[1])

        common_indices = sorted(set(coords1.keys()) & set(coords2.keys()), key=int)
        if not common_indices:
            print("No common indices found between the two files for comparison.")
            return

        # Extract latitude and longitude values for each common index
        longitudes_file1 = [coords1[idx][1] for idx in common_indices]
        latitudes_file1 = [coords1[idx][0] for idx in common_indices]
        longitudes_file2 = [coords2[idx][1] for idx in common_indices]
        latitudes_file2 = [coords2[idx][0] for idx in common_indices]

        # Compute geodesic distance errors (in meters)
        distance_errors = [
            geodesic((latitudes_file1[i], longitudes_file1[i]), 
                    (latitudes_file2[i], longitudes_file2[i])).meters
            for i in range(len(common_indices))
        ]

        mean_distance_error = np.mean(distance_errors)
        max_distance_error = np.max(distance_errors)
        min_distance_error = np.min(distance_errors)

        # Find the indices corresponding to max and min error
        max_error_idx = common_indices[np.argmax(distance_errors)]
        min_error_idx = common_indices[np.argmin(distance_errors)]

        plt.figure(figsize=(12, 8))

        plt.scatter(longitudes_file1, latitudes_file1, color='red', label=file_name1, marker='o', s=50)
        plt.scatter(longitudes_file2, latitudes_file2, color='blue', label=file_name2, marker='x', s=50)

        for i, idx in enumerate(common_indices):
            plt.plot([longitudes_file1[i], longitudes_file2[i]], 
                    [latitudes_file1[i], latitudes_file2[i]], 
                    color='gray', linestyle='--', alpha=0.5)
            plt.text(longitudes_file2[i] + 0.0001, latitudes_file2[i], idx, 
                    fontsize=8, ha='left', va='center')

        # Annotate max and min error points on the graph
        plt.scatter(longitudes_file2[np.argmax(distance_errors)], latitudes_file2[np.argmax(distance_errors)], 
                    color='gold', edgecolors='black', s=100, label="Max Distance Error Point", marker='*')

        plt.scatter(longitudes_file2[np.argmin(distance_errors)], latitudes_file2[np.argmin(distance_errors)], 
                    color='cyan', edgecolors='black', s=100, label="Min Distance Error Point", marker='*')

        # Position the error box in the top-right corner **outside** the main plot area
        plt.annotate(
            f"Mean Distance Error: {mean_distance_error:.2f} meters\n"
            f"Max Distance Error: {max_distance_error:.2f} meters (Point {max_error_idx})\n"
            f"Min Distance Error: {min_distance_error:.2f} meters (Point {min_error_idx})",
            xy=(1, 1), xycoords='axes fraction',
            xytext=(-10, -10), textcoords='offset points',
            fontsize=10, color='black', ha='right', va='top',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='black')
        )

        plt.xlabel("Longitude (Decimal Degrees)")
        plt.ylabel("Latitude (Decimal Degrees)")
        plt.title("Comparison of Coordinates from Two Files (Distance in Meters)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()



    def process_line(self, line):
        parts = line.strip().split(":")
        image_name = parts[0].split("/")[-1].strip()
        coords = parts[-1].strip()
        return image_name, coords

    def remove_decimal(self, coords):
        lat, lon = coords.split(", ")
        lat_clean = "".join(lat.split("."))
        lon_clean = "".join(lon.split("."))
        return f"{lat_clean}, {lon_clean}"
    
    def dms_to_decimal(self, dms):
        try:
            parts = dms.strip().split()
            if len(parts) < 3:
                raise ValueError(f"Invalid DMS format: {dms}")
            
            degrees = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])
            
            decimal = degrees + (minutes / 60) + (seconds / 3600)
            return decimal
        except Exception as e:
            print(f"Error parsing DMS format: {dms}")
            return None

def extract_features(image):
    orb = cv2.ORB_create(nfeatures=300)
    keypoints, descriptors = orb.detectAndCompute(image, None)
    if descriptors is None:
        print(f"Warning: No descriptors found for the image.")
        return None
    return descriptors

def softmax(x, temperature=1.0):
    e_x = np.exp((x - np.max(x)) / temperature)
    return e_x / e_x.sum()

def load_100m_model():
    model_file = '100m_image_model.pkl'
    model_data = joblib.load(model_file)
    return model_data

def load_lat_long_mapping():
    mapping_file = 'lat_long_mapping.pkl'
    mapping_data = joblib.load(mapping_file)
    return mapping_data

def match_image_with_softmax(test_image, model_data, temperature=1.5):
    test_descriptors = extract_features(test_image)
    if test_descriptors is None:
        return "No features found in test image.", None

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    def match_single_image(filename, descriptors):
        if descriptors is not None:
            matches = bf.match(test_descriptors, descriptors)
            good_matches = [m for m in matches if m.distance < 32]
            if good_matches:
                avg_distance = np.mean([m.distance for m in good_matches])
                score = len(good_matches) / (avg_distance + 1e-6)
            else:
                score = 0
        else:
            score = 0
        return score, filename

    scores_filenames = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(lambda item: match_single_image(item[0], item[1]), model_data['image_features'].items())
        scores_filenames = list(results)

    scores = np.array([score for score, _ in scores_filenames])
    filenames = [filename for _, filename in scores_filenames]
    probabilities = softmax(scores, temperature=temperature)
    coords_probabilities = {filename: prob for filename, prob in zip(filenames, probabilities)}

    return coords_probabilities

def process_single_image(model_data, lat_long_mapping, output_file_path):
    """Prompt user to select an image and process it."""
    
    # Let user select an image
    image_path, _ = QFileDialog.getOpenFileName(None, "Select an Image", "", 
                                                "Image Files (*.jpg *.jpeg *.png *.bmp *.tiff);;All Files (*)")
    
    if not image_path:
        print("No image selected.")
        return

    print(f"Processing: {image_path}")

    try:
        with open(output_file_path, 'a') as output_file:  # Open in append mode to avoid overwriting
            output_line = f"Processing: {image_path}\n"
            output_file.write(output_line)
            output_file.flush()
            print(output_line.strip())

            original_image = cv2.imread(image_path)
            if original_image is None:
                error_message = f"Error: Image at {image_path} could not be read.\n"
                output_file.write(error_message)
                output_file.flush()
                print(error_message.strip())
                return

            coords_probabilities = match_image_with_softmax(original_image, model_data, temperature=2.0)

            if coords_probabilities:
                top_match_filename = max(coords_probabilities, key=coords_probabilities.get)
                top_match_probability = coords_probabilities[top_match_filename] * 100
                lat_long = lat_long_mapping.get(top_match_filename, "Unknown Lat-Long")

                match_line = f"Top Match: {top_match_filename}\n"
                probability_line = f"Probability: {top_match_probability:.2f}%\n"
                lat_long_line = f"Latitude-Longitude: {lat_long}\n"

                output_file.write(match_line)
                output_file.write(probability_line)
                output_file.write(lat_long_line)
                output_file.flush()

                print(match_line.strip())
                print(probability_line.strip())
                print(lat_long_line.strip())

            else:
                no_match_line = "No coordinates probabilities found for this image.\n"
                output_file.write(no_match_line)
                output_file.flush()
                print(no_match_line.strip())

    except IOError as e:
        print(f"Error writing to file {output_file_path}: {e}")


def process_folder(test_folder, model_data, lat_long_mapping, output_file_path):
    test_images = [os.path.join(test_folder, file) for file in os.listdir(test_folder)
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]

    if not test_images:
        print(f"No valid images found in the folder: {test_folder}")
        return

    print(f"Attempting to write to: {output_file_path}")

    try:
        with open(output_file_path, 'w') as output_file:
            for test_image_path in test_images:
                output_line = f"Processing: {test_image_path}\n"
                output_file.write(output_line)
                output_file.flush()
                print(output_line.strip())

                original_image = cv2.imread(test_image_path)
                if original_image is None:
                    error_message = f"Error: Image at {test_image_path} could not be read.\n"
                    output_file.write(error_message)
                    output_file.flush()
                    print(error_message.strip())
                    continue

                coords_probabilities = match_image_with_softmax(original_image, model_data, temperature=2.0)
                print(f"Coords Probabilities: {coords_probabilities}")

                if coords_probabilities:
                    top_match_filename = max(coords_probabilities, key=coords_probabilities.get)
                    top_match_probability = coords_probabilities[top_match_filename] * 100
                    lat_long = lat_long_mapping.get(top_match_filename, "Unknown Lat-Long")

                    match_line = f"Top Match: {top_match_filename}\n"
                    probability_line = f"Probability: {top_match_probability:.2f}%\n"
                    lat_long_line = f"Latitude-Longitude: {lat_long}\n"

                    output_file.write(match_line)
                    output_file.write(probability_line)
                    output_file.write(lat_long_line)
                    output_file.flush()  # Ensure data is written immediately

                    print(match_line.strip())
                    print(probability_line.strip())
                    print(lat_long_line.strip())

                else:
                    no_match_line = "No coordinates probabilities found for this image.\n"
                    output_file.write(no_match_line)
                    output_file.flush()
                    print(no_match_line.strip())

    except IOError as e:
        print(f"Error writing to file {output_file_path}: {e}")


if __name__ == "__main__":
    app = QApplication([])
    window = Simulation()
    window.show()
    app.exec_()