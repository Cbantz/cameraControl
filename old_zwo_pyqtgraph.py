import sys
import numpy as np
from PySide6.QtWidgets import QApplication, QLabel, QSlider, QVBoxLayout, QComboBox, QWidget, QLineEdit, QHBoxLayout
from PySide6.QtCore import Qt, QTimer, QPoint, QRect, QSize, QThread, Signal
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import zwoasi as asi

# from utils import FrameCounter
from skimage.draw import ellipse, disk
asi.init(r"C:\Users\peg20\Documents\ASI SDK\lib\x64\ASICamera2.dll")

class FrameCaptureThread(QThread):
    frame_captured = Signal(np.ndarray)  # Signal emitted with the new frame (as a NumPy array)

    def __init__(self, camera, parent=None):
        super().__init__(parent)
        self.camera = camera
        self.running = True

    def run(self):
        while self.running:
            frame = self.camera.capture_video_frame().T
            if frame is not None:
                self.frame_captured.emit(frame)  # Emit the new frame

    def stop(self):
        self.running = False
        self.wait()  # Ensure thread has finished before exiting


class CameraControlGUI(QWidget):
    def __init__(self, camera):
        super().__init__()

        self.camera = camera

        # Set up the GUI layout
        self.init_ui()

        self.frame_capture_thread = FrameCaptureThread(self.camera)
        self.frame_capture_thread.frame_captured.connect(self.on_frame_captured)
        self.frame_capture_thread.start()

        # Timer for updating camera frames
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.update_frame)
        # self.timer.start(33)  # Update every ~33ms (~30 fps)

    def init_ui(self):
        # Create the layout
        layout = QVBoxLayout()

        # Shape selection dropdown
        self.shape_selector = QComboBox(self)
        self.shape_selector.addItems(["Rectangle", "Ellipse", "Circle"])
        self.shape_selector.currentTextChanged.connect(self.update_shape_selection)
        layout.addWidget(self.shape_selector)

        # Exposure slider
        self.exposure_slider = QSlider(Qt.Horizontal)
        self.exposure_slider.setRange(0, 100)  # Adjust as needed for your camera's exposure range
        self.exposure_slider.setValue(1)
        self.exposure_slider.setTickInterval(10)
        self.exposure_slider.valueChanged.connect(self.update_exposure_from_slider)

        # Create a horizontal layout for the slider and label
        exposure_layout = QHBoxLayout()
        
        # Label for current exposure value
        self.exposure_label = QLabel(f"Exposure: {self.exposure_slider.value()}")

        # QLineEdit for manual exposure input
        self.exposure_input = QLineEdit()
        self.exposure_input.setText(str(self.exposure_slider.value()))
        self.exposure_input.setFixedWidth(50)  # Adjust width if necessary
        self.exposure_input.returnPressed.connect(self.update_exposure_from_input)

        # Add slider, label, and input box to layout
        exposure_layout.addWidget(self.exposure_slider)
        exposure_layout.addWidget(self.exposure_label)
        exposure_layout.addWidget(self.exposure_input)
        
        layout.addLayout(exposure_layout)

        # Gain slider (unchanged)
        self.gain_slider = QSlider(Qt.Horizontal)
        self.gain_slider.setRange(0, 300)
        self.gain_slider.setValue(50)
        self.gain_slider.setTickInterval(10)
        self.gain_slider.valueChanged.connect(self.update_gain)
        layout.addWidget(self.gain_slider)

        # Camera feed label (custom with region drawing)
        self.image_view = pg.ImageView(self)
        layout.addWidget(self.image_view)
        #self.image_view.getHistogramWidget().disableAutoHistogramRange()
        self.image_view.getHistogramWidget().setHistogramRange(0, 65535)

        # Set the layout for the window
        self.setLayout(layout)
        self.setWindowTitle("16-bit Mono Camera Control")
        # Set the window size
        self.resize(800, 600)

        # framecnt = FrameCounter()
        # framecnt.sigFpsUpdate.connect(lambda fps: ui.fpsLabel.setText(f'{fps:.1f} fps'))

    def update_exposure_from_slider(self, value):
        # Update the exposure time based on the slider's value
        value = value/10
        print(f"Slider: Updating exposure to {value}")

        # Update the label and input box
        self.exposure_label.setText(f"Exposure: {value}")
        self.exposure_input.setText(str(value))

        print("Updating exposure from slider")
        self.update_exposure(value)

    def update_exposure_from_input(self):
        # Read the value from the input box and set the slider
        try:
            value = float(self.exposure_input.text())
            if 0 <= value <= 100:  # Ensure value is within slider's range
                print(f"Input: Updating exposure to {value}")
                self.exposure_slider.setValue(value*10)
                self.exposure_label.setText(f"Exposure: {value}")
            else:
                print("Invalid exposure value!")
        except ValueError:
            print("Please enter a valid number!")

    def on_frame_captured(self, frame):
        current_view_range = self.image_view.getView().viewRange()
        print(f"Current view range: {current_view_range}")
        # current_histogram_range = self.image_view.getHistogramWidget().getLevels()
        # print(f"Current histogram range: {current_histogram_range}")
        current_histogram_view_range = self.image_view.getHistogramWidget().getHistogramRange()
        print(f"Current histogram view range: {current_histogram_view_range}")

        # Add 30000 count square to the frame
        frame[100:200, 100:200] += 30000
        # Update the image view with the new frame
        self.image_view.setImage(frame, autoLevels=False)
        # Restore the previous view range
        self.image_view.getView().setRange(xRange=current_view_range[0], yRange=current_view_range[1], padding=0)
        # Restore the previous histogram view range
        self.image_view.getHistogramWidget().setHistogramRange(*current_histogram_view_range, padding=0)

    def update_exposure(self, value):
        # Update the camera's exposure time
        value = value
        print(f"Updating exposure to {value} sec")
        # Example: self.camera.set_exposure(value)
        self.camera.set_control_value(asi.ASI_EXPOSURE, int(value * 1e6))
        # Print the current exposure value
        print(f"Current exposure: {self.camera.get_control_value(asi.ASI_EXPOSURE)[0] / 1e6} sec")
        timeout = (self.camera.get_control_value(asi.ASI_EXPOSURE)[0] / 1000) * 2 + 500
        print(f"Setting timeout to {timeout} ms")
        self.camera.default_timeout = timeout

    def update_shape_selection(self, shape):
        self.camera_label.set_shape(shape)

    def update_gain(self, value):
        # Update the camera's gain based on the slider's value
        print(f"Updating gain to {value}")
        # Example: self.camera.set_gain(value)
        self.camera.set_control_value(asi.ASI_GAIN, value)

    def update_frame(self):
        # Capture a frame from the camera (assuming 16-bit mono image)
        print("Capturing next frame...")
        frame = self.camera.capture_video_frame()
        # Add 30000 count square to the frame
        frame[100:200, 100:200] += 30000
        # Calculate mean value of the frame
        #mean = np.mean(frame)
        #print(f"Mean value: {mean}")
        
        if frame is not None:
            # Normalize or scale 16-bit mono image to 8-bit for display
            # frame_8bit = self.convert_16bit_to_8bit(frame)
            frame_8bit = frame
            
            height, width = frame_8bit.shape
            bytes_per_line = width  # 1 byte per pixel (grayscale)
            
            # Convert the NumPy array (8-bit grayscale) to QImage
            # q_img = QImage(frame_8bit.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
            
            # Convert QImage to QPixmap and display it on the QLabel
            self.image_view.setImage(frame_8bit, autoLevels=False)

            # if not self.camera_label.region_rect.isNull():
            #     region = self.camera_label.region_rect
            #     x1, y1 = max(0, region.topLeft().x()), max(0, region.topLeft().y())
            #     x2, y2 = min(width, region.bottomRight().x()), min(height, region.bottomRight().y())

            #     if self.camera_label.current_shape == "Rectangle":
            #         selected_region = frame[y1:y2, x1:x2]

            #     elif self.camera_label.current_shape == "Ellipse":
            #         rr, cc = ellipse((y1 + y2) // 2, (x1 + x2) // 2, (y2 - y1) // 2, (x2 - x1) // 2, shape=frame.shape)
            #         selected_region = frame[rr, cc]

            #     elif self.camera_label.current_shape == "Circle":
            #         # Use the minimum side length to define the circle radius
            #         radius = min((y2 - y1) // 2, (x2 - x1) // 2)
            #         rr, cc = disk(((y1 + y2) // 2, (x1 + x2) // 2), radius, shape=frame.shape)
            #         selected_region = frame[rr, cc]

            #     # Compute statistics for the selected region
            #     if selected_region.size > 0:
            #         mean_value = np.mean(selected_region)
            #         std_value = np.std(selected_region)
            #         print(f"Region Mean: {mean_value}, Std Dev: {std_value}")

    def convert_16bit_to_8bit(self, frame_16bit):
        """
        Convert the 16-bit mono frame (uint16) to 8-bit grayscale (uint8).
        The scaling is done by dividing by 256 to map the 16-bit range [0, 65535]
        to the 8-bit range [0, 255].
        """
        frame_16bit = np.clip(frame_16bit, 0, 65535)  # Ensure values are within 16-bit range
        frame_8bit = (frame_16bit / 256).astype(np.uint8)  # Scale down to 8-bit
        return frame_8bit
    
    def closeEvent(self, event):
        """
        Ensure the camera is stopped and released when the GUI is closed.
        """
        print("Closing application...")
        # self.timer.stop()
        self.frame_capture_thread.stop()
        self.camera.stop_video_capture()
        self.camera.close()
        event.accept()

# Dummy camera class for simulation purposes (returns 16-bit mono images)
class DummyCamera:
    def capture_video_frame(self):
        # Simulate a 16-bit grayscale image (480x640)
        return np.random.randint(0, 65535, (480*2, 640*2), dtype=np.uint16)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Initialize the camera (replace DummyCamera with actual camera class)
    # camera = DummyCamera()

    camera = asi.Camera(0)
    camera.set_control_value(asi.ASI_GAIN, 0)
    exptime_seconds = 0.1
    camera.set_control_value(asi.ASI_EXPOSURE, int(exptime_seconds * 1e6))
    camera.set_control_value(asi.ASI_BANDWIDTHOVERLOAD, 80)
    camera.set_image_type(asi.ASI_IMG_RAW16)

    camera.start_video_capture()
    timeout = (camera.get_control_value(asi.ASI_EXPOSURE)[0] / 1000) * 2 + 500
    camera.default_timeout = timeout

    # Create and show the GUI
    gui = CameraControlGUI(camera)
    gui.show()

    sys.exit(app.exec())
