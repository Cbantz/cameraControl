import pyqtgraph as pg
import numpy as np
from PIL import Image
from pyqtgraph.Qt import QtGui
#from pyqtgraph.Qt.QtWidgets import QApplication
from PySide6.QtWidgets import QApplication, QLabel, QSlider, QVBoxLayout, QComboBox, QWidget, QLineEdit, QHBoxLayout
from PySide6.QtCore import Qt, QTimer, QPoint, QRect, QSize
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen

# Dummy camera class for simulation purposes (returns 16-bit mono images)
class DummyCamera:
    def capture_video_frame(self):
        # Simulate a 16-bit grayscale image (480x640)
        return np.random.randint(0, 65535, (480*2, 640*2), dtype=np.uint16)
    
    def start_video_capture(self):
        pass

    def stop_video_capture(self):
        pass

    def close(self):
        pass

class CameraControlGUI(QWidget):
    def __init__(self, camera):
        super().__init__()

        self.camera = camera

        self.init_ui()

        # Timer
        # Create a timer to update the image view
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_image)
        self.timer.start(30)

    def init_ui(self):
        # Create the layout
        layout = QVBoxLayout()

        # Create QWidget to contain imview
        self.image_view_container = QWidget()
        self.image_view_layout = QVBoxLayout(self.image_view_container)
        self.imv = pg.ImageView()
        print(type(self.imv))
        self.image_view_layout.addWidget(self.imv)
        layout.addWidget(self.image_view_container)
        

        self.setLayout(layout)
        self.setWindowTitle('Camera Control GUI')


    def update_image(self):
        # Capture a frame from the camera
        frame = self.camera.capture_video_frame()

        # Update the image view
        self.imv.setImage(frame)

    def closeEvent(self, event):
        # Stop the timer when the window is closed
        print('Closing application...')
        self.timer.stop()
        self.camera.stop_video_capture()
        self.camera.close()
        event.accept()

# # Import image_0.tiff
# img = Image.open('image_0.tiff')

# # Convert image to numpy array
# img_array = np.transpose(np.array(img))

# # Create application
# app = QApplication([])

# # Create image view
# image_view = pg.ImageView()
# image_view.setImage(img_array)

# # Show image view
# image_view.show()

# App
app = QApplication([])
# Camera
camera = DummyCamera()

# Create the main window
window = CameraControlGUI(camera)
window.show()

# Start Qt event loop
app.exec()