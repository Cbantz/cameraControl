import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from eeroi import EE_ROI
from bg_roi import Background_ROI

class ROI_Manager():
    def __init__(self):
        self.ee_roi = EE_ROI(pos=QtCore.QPoint(0,0))
        self.bg_roi = Background_ROI(pos=QtCore.QPoint(0,0))