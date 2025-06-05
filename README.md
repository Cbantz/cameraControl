# ZWO Image GUI in PyQtGraph

## Installation
Clone the repository to your computer.

Download the ZWO SDK library. This can be found on the ZWO Website (https://www.zwoastro.com/software/) under `Other` and `For Developers`.

Unzip this folder and move the ASI SDK folder (from the ZIP file for your operating system) to the CameraControl folder.

Make a new python environment (or add to an existing one). To do this in VSCode, you can open a terminal by dragging up from the bottom, and changing the terminal type from PowerShell to cmd (on Windows, similar on Mac).

`conda create -n pyqtgraph python` (You can choose another name)
`conda activate pyqtgraph`
`pip install numpy pyqtgraph pyside6 zwoasi`

Required Packages
- zwoasi (https://pypi.org/project/zwoasi/)
- pyqtgraph
- pyside6
- numpy
- scikit-image (optional, for `zwoImage.py`)

Main file is `zwoImage_pyqtgraph.py`