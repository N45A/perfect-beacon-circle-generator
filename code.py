import math
import os
import sys
import numpy as np 
import matplotlib.pyplot as plt


num_beams = int(input("input num_beams: "))
min_radius = int(input("input min_radius: "))
max_radius = int(input("input max_radius: "))
"""
num_beams = 16
min_radius = 7
max_radius = 13
"""

average_angle_error = 0
max_angle_error = 0

current_dir = os.path.dirname(sys.argv[0])
f = open(rf"{current_dir}\{num_beams}_{min_radius}_{max_radius}.mcfunction", 'w')

block_map = np.zeros((2*max_radius + 1, 2*max_radius + 1))
block_map[max_radius, max_radius] = num_beams/2

for i in range(num_beams):
    if i/num_beams <= 1/8 or i/num_beams >= 7/8:
        x1 = max_radius
        x2 = 0
        y1 = max_radius
        y2 = -max_radius-1

    elif i/num_beams <= 3/8 and i/num_beams > 1/8:
        x1 = -max_radius
        x2 = max_radius+1
        y1 = max_radius
        y2 = 0

    elif i/num_beams <= 5/8 and i/num_beams > 3/8:
        x1 = -max_radius
        x2 = 0
        y1 = -max_radius
        y2 = max_radius

    elif i/num_beams < 7/8 and i/num_beams > 5/8:
        x1 = -max_radius
        x2 = max_radius+1
        y1 = -max_radius
        y2 = 0

    smallest_angle = 1000
    smallest_x = x1
    smallest_y = y1
    min_max_dist = 1000

    for j in range(x1, x2, int(math.copysign(1, x2-x1))):
        for k in range(y1, y2, int(math.copysign(1, y2-y1))):
            if math.sqrt(j**2 + k**2) <= max_radius and math.sqrt(j**2 + k**2) >= min_radius:

                a = math.tan(i/num_beams*math.pi*2)
                distance_error = round(abs(a*j - k) / math.sqrt(a**2 + 1), 7)
                distance = round(math.sqrt(j**2 + k**2), 7)
                angle = round(math.asin(distance_error/distance), 5)
                current_min_max_dist = abs((min_radius + max_radius)/2 - distance)

                if (angle < smallest_angle or angle == smallest_angle and min_max_dist > current_min_max_dist):
                    smallest_angle = angle
                    smallest_x = j
                    smallest_y = k
                    min_max_dist = current_min_max_dist


    if block_map[-smallest_y - max_radius-1, smallest_x + max_radius] == 0:
        block_map[-smallest_y - max_radius-1, smallest_x + max_radius] = i + num_beams/2
    
    else:
        print("error: overlapping blocks")
        input()
        exit()

    average_angle_error += smallest_angle/num_beams

    if max_angle_error < smallest_angle:
        max_angle_error = smallest_angle
    
    f.write(f"setblock ~{smallest_x} ~ ~{smallest_y} minecraft:beacon\n")

f.close()

print()
arc = 360/num_beams
rad_to_degree = 180/math.pi
print("angle between beams in degrees:", round(arc, 3))
print("average angle error in degrees:", round(average_angle_error*rad_to_degree, 4),  f"{round(average_angle_error/arc*100*rad_to_degree, 2)}%")
print("max angle error in degrees:", round(max_angle_error*rad_to_degree, 4), f"{round(max_angle_error/arc*100*rad_to_degree, 2)}%")

plt.imshow(block_map, cmap='viridis')
tick_range = np.arange(-max_radius, max_radius + 1)
plt.xticks(tick_range + max_radius, tick_range)
plt.yticks(tick_range + max_radius, -tick_range)
#plt.grid()
plt.show()
