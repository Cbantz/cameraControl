datapoints = 10
abs_angles = []
starting_angle = 0
angle_range = 2
step_size = angle_range / datapoints
for i in range(datapoints):
    abs_angles.append(starting_angle - angle_range + (i * step_size))
for i in range(datapoints):
    abs_angles.append(starting_angle + (i + 1)*step_size)
print(abs_angles)