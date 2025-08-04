import matplotlib.pyplot as plt
import numpy as np


datapoints = 10
positions = []
thetas = []
distance = 9.5


for angle in thetas:
    pos = distance * np.tan(angle)
    positions.append(np.abs(pos))



