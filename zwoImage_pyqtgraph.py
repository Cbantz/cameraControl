import sys
import numpy as np
from PySide6.QtWidgets import QApplication, QLabel, QSlider, QVBoxLayout, QComboBox, QCheckBox, QWidget, QLineEdit, QHBoxLayout
from PySide6.QtCore import Qt, QTimer, QPoint, QRect, QSize, QThread, Signal
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import zwoasi as asi

try:
    asi.init(r"C:\Users\bantz\OneDrive - University of Iowa\Work\Diffractometer\cameraControl\ASI SDK\lib\x64\ASICamera2.dll")
except Exception as e:
    asi.init(r"E:\Philip\Documents\ASI SDK\lib\x64\ASICamera2.dll")


class FrameCaptureThread(QThread):
    frame_captured = Signal(
        np.ndarray
    )  # Signal emitted with the new frame (as a NumPy array)

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

        self.bit_depth = 16
        self.division_factor = 1
        self.electron_per_adu = 1
        self.pixel_size = 1
        self.sensor_width_pix = 1
        self.sensor_height_pix = 1
        self.exposure = 0.1  # seconds
        self.plot_list = []

        self.update_camera_properties()
        self.division_factor = 2 ** (16 - self.bit_depth)

        # Set up the GUI layout
        self.init_ui()

        self.frame_capture_thread = FrameCaptureThread(self.camera)
        self.frame_capture_thread.frame_captured.connect(self.on_frame_captured)
        self.frame_capture_thread.start()

        # Set up variables
        self.frame = None
        self.rect_roi_mean = 0

        # Timer for updating camera frames
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.update_frame)
        # self.timer.start(33)  # Update every ~33ms (~30 fps)

    def update_camera_properties(self):
        # camera_props = self.camera.get_camera_property()
        # print(f"Gain is now {self.camera.get_control_value(asi.ASI_GAIN)[0]}")

        # self.bit_depth = camera_props["BitDepth"]
        # self.electron_per_adu = camera_props["ElecPerADU"]
        # self.pixel_size = camera_props["PixelSize"]
        # self.sensor_width_pix = camera_props["MaxWidth"]
        # self.sensor_height_pix = camera_props["MaxHeight"]

        try:
            self.camera_prop_bit_depth.setText(f"Bit Depth: {self.bit_depth}")
            if self.electron_per_adu > 1:
                self.camera_prop_elec_per_adu.setText(
                    f"e-/ADU: {self.electron_per_adu:.2f}"
                )
            else:
                self.camera_prop_elec_per_adu.setText(
                    f"e-/ADU: {self.electron_per_adu:.3f}"
                )
        except AttributeError:
            pass

    def init_ui(self):
        # Create the layout
        layout = QVBoxLayout()

        # Shape selection dropdown
        # self.shape_selector = QComboBox(self)
        # self.shape_selector.addItems(["Rectangle", "Ellipse", "Circle"])
        # self.shape_selector.currentTextChanged.connect(self.update_shape_selection)
        # layout.addWidget(self.shape_selector)

        # Exposure slider
        self.exposure_slider = QSlider(Qt.Horizontal)
        self.exposure_slider.setRange(
            0, 100
        )  # Adjust as needed for your camera's exposure range
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

        # Add h layout for gain slider and line
        gain_layout = QHBoxLayout()

        # Label for current gain value
        self.gain_label = QLabel("Gain ")

        # Gain slider (unchanged)
        self.gain_slider = QSlider(Qt.Horizontal)
        self.gain_slider.setRange(0, 300)
        self.gain_slider.setValue(50)
        self.gain_slider.setTickInterval(10)
        self.gain_slider.valueChanged.connect(self.update_gain_from_slider)

        # Gain input box and label
        self.gain_input = QLineEdit()
        self.gain_input.setText(str(self.gain_slider.value()))
        self.gain_input.setFixedWidth(50)
        self.gain_input.returnPressed.connect(self.update_gain_from_input)

        gain_layout.addWidget(self.gain_label)
        gain_layout.addWidget(self.gain_slider)
        gain_layout.addWidget(self.gain_input)

        layout.addLayout(gain_layout)

        # Camera feed label (custom with region drawing)
        self.image_view = pg.ImageView(self)
        layout.addWidget(self.image_view)

        # self.image_view.getHistogramWidget().disableAutoHistogramRange()
        self.image_view.getHistogramWidget().setHistogramRange(
            0, 65535 / self.division_factor
        )
        self.image_view.getHistogramWidget().setLevels(0, 65535 / self.division_factor)
        # Log scale for histogram
        #self.image_view.getHistogramWidget().plot.setLogMode(True, False)
        print(f"Type of hist widget: {type(self.image_view.getHistogramWidget())}")
        # Get properties of the histogram widget
        # print(f"Properties of histogram widget: {dir(self.image_view.getHistogramWidget())}")
        # self.image_view.getHistogramWidget().item
        
        # Set image view range to show entire frame
        self.image_view.getView().setRange(xRange=[0, self.sensor_width_pix])
        self.image_view.getView().setRange(yRange=[0, self.sensor_height_pix])

        # Add circle ROI to the image view
        self.circle_ROI = pg.CircleROI([100, 100], [50, 50], pen=(4, 9))
        self.image_view.addItem(self.circle_ROI)

        # Add rectangle ROI to the image view
        self.rect_ROI = pg.RectROI([50, 100], [50, 50], pen=(5, 1))
        self.image_view.addItem(self.rect_ROI)

        # Add horizontal layout for statistics labels
        stats_layout = QHBoxLayout()

        # Create a vertical layout for Circle ROI statistics
        circle_ROI_layout = QVBoxLayout()

        # Label for Circle ROI radius, sum, mean, net counts
        self.circle_ROI_label = QLabel("Circle ROI: ")
        circle_ROI_layout.addWidget(self.circle_ROI_label)
        # Each of the following labels will be updated with the corresponding value
        self.circle_ROI_radius = QLabel("Radius: ")
        circle_ROI_layout.addWidget(self.circle_ROI_radius)
        self.circle_ROI_sum = QLabel("Sum: ")
        circle_ROI_layout.addWidget(self.circle_ROI_sum)
        self.circle_ROI_mean = QLabel("Mean: ")
        circle_ROI_layout.addWidget(self.circle_ROI_mean)
        self.circle_ROI_net_counts = QLabel("Net Counts: ")
        self.circle_ROI_net_counts_checkbox = QCheckBox("Plot net?")
        self.circle_ROI_net_counts_checkbox.stateChanged.connect(self.reset_plot)
        circle_ROI_layout.addWidget(self.circle_ROI_net_counts_checkbox)
        circle_ROI_layout.addWidget(self.circle_ROI_net_counts)

        # Add the Circle ROI layout to the stats layout
        stats_layout.addLayout(circle_ROI_layout)

        # Label for Rectangle ROI sum and mean
        # First create a rectangle ROI layout
        rect_ROI_layout = QVBoxLayout()

        # Label for Rectangle ROI sum and mean
        self.rect_ROI_label = QLabel("Rectangle ROI: ")
        rect_ROI_layout.addWidget(self.rect_ROI_label)
        # Each of the following labels will be updated with the corresponding value
        self.rect_ROI_sum = QLabel("Sum: ")
        rect_ROI_layout.addWidget(self.rect_ROI_sum)
        self.rect_ROI_mean = QLabel("Mean: ")
        rect_ROI_layout.addWidget(self.rect_ROI_mean)

        # Add the Rectangle ROI layout to the stats layout
        stats_layout.addLayout(rect_ROI_layout)

        # New layout for camera properties (elec/ADU, bit depth)
        camera_prop_layout = QVBoxLayout()

        # Label for camera properties
        self.camera_prop_label = QLabel("Camera Properties: ")
        camera_prop_layout.addWidget(self.camera_prop_label)
        # Each of the following labels will be updated with the corresponding value
        self.camera_prop_bit_depth = QLabel(f"Bit Depth: {self.bit_depth}")
        camera_prop_layout.addWidget(self.camera_prop_bit_depth)
        self.camera_prop_elec_per_adu = QLabel(f"e-/ADU: {self.electron_per_adu:.2f}")
        camera_prop_layout.addWidget(self.camera_prop_elec_per_adu)
        # Add checkbox to use units of e-/ADU instead of counts
        self.electron_per_adu_checkbox = QCheckBox("Use e-/ADU")
        self.electron_per_adu_checkbox.stateChanged.connect(self.reset_plot)
        # self.electron_per_adu_checkbox.stateChanged.connect(
        #     lambda state: self.electron_per_adu_checkbox.setChecked(True)
        # )
        camera_prop_layout.addWidget(self.electron_per_adu_checkbox)
        # Add checkbox to calculate rate
        self.rate_checkbox = QCheckBox("Calculate Rate")
        # On state change, reset plot
        self.rate_checkbox.stateChanged.connect(self.reset_plot)
        camera_prop_layout.addWidget(self.rate_checkbox)

        # Add the camera properties layout to the stats layout
        stats_layout.addLayout(camera_prop_layout)

        # Add plot to the bottom to display the previous measurements of various values
        # including the net counts or rate, mean, and sum
        self.plot = pg.PlotWidget()
        self.plot.setLabel("bottom", "Time", units="s")
        self.plot.setLabel("left", "Value")
        self.plot.setTitle("Previous Measurements")
        self.plot.showGrid(x=True, y=True)
        self.plot.addLegend()
        # self.plot.setLimits(xMin=0, xMax=10, yMin=0, yMax=100)
        self.plot.setFixedHeight(200)
        self.plot.setFixedWidth(500)
        # Add the plot to the stats layout
        stats_layout.addWidget(self.plot)

        # Add the stats layout to the main layout
        layout.addLayout(stats_layout)

        # Set the layout for the window
        self.setLayout(layout)
        self.setWindowTitle("16-bit Mono Camera Control")
        # Set the window size
        self.resize(800, 600)

        # framecnt = FrameCounter()
        # framecnt.sigFpsUpdate.connect(lambda fps: ui.fpsLabel.setText(f'{fps:.1f} fps'))

    def reset_plot(self):
        # Reset the plot
        self.plot.clear()
        self.plot_list = []

    def update_exposure_from_slider(self, value):
        # Update the exposure time based on the slider's value
        value = value / 10
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
                self.exposure_slider.blockSignals(True)
                self.exposure_slider.setValue(value * 10)
                self.exposure_slider.blockSignals(False)
                self.exposure_label.setText(f"Exposure: {value}")
                self.update_exposure(value)
            else:
                print("Invalid exposure value!")
        except ValueError:
            print("Please enter a valid number!")

    def on_frame_captured(self, frame):
        self.frame = frame // self.division_factor
        current_view_range = self.image_view.getView().viewRange()
        # print(f"Current view range: {current_view_range}")
        # current_histogram_range = self.image_view.getHistogramWidget().getLevels()
        # print(f"Current histogram range: {current_histogram_range}")
        current_histogram_view_range = (
            self.image_view.getHistogramWidget().getHistogramRange()
        )
        # print(f"Current histogram view range: {current_histogram_view_range}")

        # Add 30000 count square to the frame
        # self.frame[100:200, 100:200] += 1000
        # Update the image view with the new frame
        self.image_view.setImage(self.frame, autoLevels=False)
        # Restore the previous view range
        self.image_view.getView().setRange(
            xRange=current_view_range[0], yRange=current_view_range[1], padding=0
        )
        # Restore the previous histogram view range
        self.image_view.getHistogramWidget().setHistogramRange(
            *current_histogram_view_range, padding=0
        )

        # Update the statistics for the rectangle ROI
        self.update_rect_ROI_statistics()

        # Update the statistics for the circle ROI
        self.update_circle_ROI_statistics()

    def update_exposure(self, value):
        # Update the camera's exposure time
        value = value
        print(f"Updating exposure to {value}")
        timeout = (value * 1000) * 4 + 500
        print(f"Setting timeout to {timeout} ms")
        self.camera.default_timeout = timeout
        print(f"Updating exposure to {value} sec")
        # Example: self.camera.set_exposure(value)
        self.camera.set_control_value(asi.ASI_EXPOSURE, int(value * 1e6))
        # Print the current exposure value
        self.exposure = self.camera.get_control_value(asi.ASI_EXPOSURE)[0] / 1e6
        print(f"Current exposure: {self.exposure} sec")

    # def update_shape_selection(self, shape):
    #     self.camera_label.set_shape(shape)

    def update_gain_from_input(self):
        # Update from the input box
        try:
            value = int(self.gain_input.text())
            if 0 <= value <= 300:
                print(f"Input: Updating gain to {value}")
                self.gain_slider.setValue(value)
            else:
                print("Invalid gain value!")
        except ValueError:
            print("Please enter a valid number!")

    def update_gain_from_slider(self, value):
        # Update the gain based on the slider's value
        print(f"Slider: Updating gain to {value}")
        # Update the input box
        self.gain_input.setText(str(value))
        self.update_gain(value)

    def update_gain(self, value):
        # Update the camera's gain based on the input value
        print(f"Updating gain to {value}")
        # Example: self.camera.set_gain(value)
        self.camera.set_control_value(asi.ASI_GAIN, value)
        # Update camera properties
        self.update_camera_properties()

    def update_rect_ROI_statistics(self):
        # Update the statistics for the rectangle ROI
        # Get average in the rectangle ROI
        rect_roi_mask = self.rect_ROI.getArrayRegion(
            self.frame, self.image_view.getImageItem()
        )
        self.rect_roi_sum = np.sum(rect_roi_mask)
        self.rect_roi_mean = np.mean(rect_roi_mask)
        # print(f"Rectangle ROI mean: {self.rect_roi_mean:.4g}")

        if self.electron_per_adu_checkbox.isChecked():
            # Convert counts to electrons using the camera's e-/ADU value
            self.rect_roi_sum *= self.electron_per_adu
            self.rect_roi_mean *= self.electron_per_adu
            units = "e-"  # Electrons
        else:
            units = "counts"

        if self.rate_checkbox.isChecked():
            # Calculate the rate
            self.rect_roi_sum /= self.exposure
            self.rect_roi_mean /= self.exposure
            rateUnit = "/sec"
        else:
            rateUnit = ""

        self.rect_ROI_sum.setText(f"Sum: {self.rect_roi_sum:.3e} {units}{rateUnit}")
        self.rect_ROI_mean.setText(f"Mean: {self.rect_roi_mean:.4g} {units}{rateUnit}")

    def update_circle_ROI_statistics(self):
        # Update the statistics for the circle ROI

        # Get average in the circle ROI
        circle_roi_mask = self.circle_ROI.getArrayRegion(
            self.frame, self.image_view.getImageItem()
        )
        # Calculate mean of non-0 values in the circle ROI
        # First calculate sum of all values in the circle ROI
        circle_roi_sum = np.sum(circle_roi_mask)
        # print(f"Circle ROI sum: {circle_roi_sum:.3e}")

        # Then find number of non-zero values in the circle ROI
        num_nonzero = np.sum(circle_roi_mask != 0)

        # Calculate mean of non-zero values in the circle ROI
        circle_roi_mean = circle_roi_sum / num_nonzero if num_nonzero > 0 else 0
        # print(f"Circle ROI mean: {circle_roi_mean:.4g}")

        # Calculate net counts in the circle ROI
        if self.electron_per_adu_checkbox.isChecked():
            # calculate net counts in e-
            # rectangle mean is in e-
            circle_roi_sum *= self.electron_per_adu
            circle_roi_mean *= self.electron_per_adu
            units = "e-"
            # Still not right - rect mean will have units of counts or e- depending on checkbox
            net_counts = circle_roi_sum - (self.rect_roi_mean * num_nonzero)
        else:
            net_counts = circle_roi_sum - (self.rect_roi_mean * num_nonzero)
            units = "counts"
        # print(f"Net counts in circle ROI: {net_counts:.3e}")

        # # Update the statistics labels
        # if self.electron_per_adu_checkbox.isChecked():
        #     # Convert counts to electrons using the camera's e-/ADU value
        #     circle_roi_sum *= self.electron_per_adu
        #     circle_roi_mean *= self.electron_per_adu
        #     units = "e-"
        # else:
        #     units = "counts"

        if self.rate_checkbox.isChecked():
            # Calculate the rate
            circle_roi_sum /= self.exposure
            circle_roi_mean /= self.exposure
            net_counts = circle_roi_sum - (self.rect_roi_mean * num_nonzero)
            rateUnit = "/sec"
        else:
            rateUnit = ""

        self.circle_ROI_radius.setText(
            f"Radius: {self.circle_ROI.size()[0] / 2:.1f} px"
        )
        self.circle_ROI_sum.setText(f"Sum: {circle_roi_sum:.3e} {units}{rateUnit}")
        self.circle_ROI_mean.setText(f"Mean: {circle_roi_mean:.4g} {units}{rateUnit}")
        self.circle_ROI_net_counts.setText(f"Net: {net_counts:.3e} {units}{rateUnit}")

        if self.circle_ROI_net_counts_checkbox.isChecked():
            # Add the net counts to the plot if the checkbox is checked
            # at the next time step
            self.plot_list.append(net_counts)
            self.plot.clear()
            self.plot.plot(self.plot_list, pen=(255, 0, 0), name="Net Counts")

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
        return np.random.randint(0, 65535, (480 * 2, 640 * 2), dtype=np.uint16)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # qdarktheme.setup_theme()

    # Initialize the camera (replace DummyCamera with actual camera class)
    camera = DummyCamera()

    # camera = asi.Camera(0)
    # camera.set_control_value(asi.ASI_GAIN, 50)
    # exptime_seconds = 0.1
    # camera.set_control_value(asi.ASI_EXPOSURE, int(exptime_seconds * 1e6))
    # camera.set_control_value(asi.ASI_BANDWIDTHOVERLOAD, 80)
    # camera.set_image_type(asi.ASI_IMG_RAW16)

    # camera.start_video_capture()
    # timeout = (camera.get_control_value(asi.ASI_EXPOSURE)[0] / 1000) * 2 + 500
    # camera.default_timeout = timeout

    # Create and show the GUI
    gui = CameraControlGUI(camera)
    gui.show()

    sys.exit(app.exec())
    camera.set_image_type(asi.ASI_IMG_RAW16)

    camera.start_video_capture()
    timeout = (camera.get_control_value(asi.ASI_EXPOSURE)[0] / 1000) * 2 + 500
    camera.default_timeout = timeout

    # Create and show the GUI
    gui = CameraControlGUI(camera)
    gui.show()

    sys.exit(app.exec())
