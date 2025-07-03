from pyqtgraph.Qt import QtCore
import pyqtgraph
import numpy as np


class Signal_Manager(QtCore.QObject):
    connect_to_camera = QtCore.Signal()
    main_win_start_live_view = QtCore.Signal()
    main_win_req_frame = QtCore.Signal(pyqtgraph.ROI, pyqtgraph.ImageItem)
    main_win_end_live_view = QtCore.Signal()
    cam_frame_ready = QtCore.Signal(np.ndarray)
    cam_first_frame = QtCore.Signal()

signals = Signal_Manager()