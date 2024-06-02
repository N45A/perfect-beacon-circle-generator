import math
import os
import sys
import mcschematic
from oklab import *

number_of_beams = int(input("number of beams: "))
min_radius = int(input("min radius: "))
max_radius = int(input("max radius: "))
number_of_colors = int(input("number of colors: "))
print("input colors in HEX (without #)")

colors = []
for color in range(number_of_colors):
    colors.append(input(f"nr. {color+1}: "))

print("\nprocessing...")

"""
number_of_beams = 96
min_radius = 13
max_radius = 23
colors = ["FF0000", "00FF00", "0000FF"]
"""

def on_axies(beam_angle):
    if math.isclose(beam_angle, 0):
        all_points.append((average_radius, 0))
    elif math.isclose(beam_angle, 0.5*math.pi):
        all_points.append((0, average_radius))
    elif math.isclose(beam_angle, math.pi):
        all_points.append((-average_radius, 0))
    elif math.isclose(beam_angle, 1.5*math.pi):
        all_points.append((0, -average_radius))
    else:
        return False
    return True

def fix_xy_signs(x, y):
    x, y = abs(x), abs(y)

    if 0.5*math.pi < beam_angle < math.pi:
        x, y = -x, y
    elif math.pi < beam_angle < 1.5*math.pi:
        x, y = -x, -y
    elif 1.5*math.pi < beam_angle:
        x, y = x, -y

    return x, y

def euclidean_distance_function(x, y):
    return (x**2 + y**2)**(1/2)

def find_possible_angles(x, y):
    if min_radius <= euclidean_distance_function(x, y) <= max_radius:
        lowered_beam_angle = beam_angle
        if beam_angle >= math.pi:
            lowered_beam_angle = 2*math.pi - beam_angle
        list_of_possible_angles.append((x, y, abs(abs(math.atan2(y, x)) - lowered_beam_angle)))

def find_best_beam():
    min_index = min(enumerate(list_of_possible_angles), key=lambda x: x[1][2])[0]
    angle_error = list_of_possible_angles[min_index][2]
    best_beam = (0, 0, math.inf)

    for angle_number in range(len(list_of_possible_angles)):
        if math.isclose(list_of_possible_angles[angle_number][2], angle_error):
            x, y, angle_error = list_of_possible_angles[angle_number]
            if abs((x**2 + y**2)**(1/2) - average_radius) < abs((best_beam[0]**2 + best_beam[1]**2)**(1/2) - average_radius):
                best_beam = x, y, angle_error

    return best_beam

def place_blocks():
    setblock((0, 0, 0), "emerald_block")

    for beam, (x, y) in enumerate(all_points):
        setblock((x, 1, y), "beacon")

        if number_of_colors != 0:
            block_colors = all_colors_blocks[beam]
            for block in range(len(block_colors)):
                setblock((x, block + 2, y), id_to_glass_name(block_colors[block]))

        for k in range(-1, 2):
            for j in range(-1, 2):
                setblock((x+k, 0, y+j), "iron_block")

def setblock(coords, block_name):
    schematic.setBlock(coords, f"minecraft:{block_name}")

def save_schematic():
    roaming_dir = os.path.expandvars(r'%APPDATA%')
    schematic_dir = os.path.join(roaming_dir, r".minecraft\schematics")
    file_name = f"beacon_{number_of_beams}_{min_radius}_{max_radius}"

    if os.path.exists(schematic_dir):
        schematic.save(schematic_dir, file_name, mcschematic.Version.JE_1_20_1)
        print(f"File saved: {os.path.join(schematic_dir, file_name)}")
    else:
        current_directory = os.path.dirname(sys.argv[0])
        schematic.save(current_directory, file_name, mcschematic.Version.JE_1_20_1)
        print(f"File saved: {os.path.join(current_directory, file_name)}]")

average_radius = math.floor((max_radius + min_radius)/2)
#total_angle_error = 0
#highest_angle_error = 0
all_points = []

for beam_number in range(number_of_beams):
    beam_angle = 2*math.pi*beam_number/number_of_beams

    if not on_axies(beam_angle):
        list_of_angles = []
        list_of_possible_angles = []
        beam_y = math.tan(beam_angle)

        for radius in(range(max_radius)):
            list_of_angles.append((radius, math.floor(radius*beam_y)))
            list_of_angles.append((radius, math.ceil(radius*beam_y)))

        for x, y in list_of_angles:
            x, y = fix_xy_signs(x, y)
            find_possible_angles(x, y)

        if list_of_possible_angles == []:
            raise Exception(f"Error: no matching positions for beam {beam_number} found. Try moving the radii further apart.")

        x, y, angle_error = find_best_beam()

        #total_angle_error += angle_error
        #highest_angle_error = max(highest_angle_error, angle_error)
        all_points.append((x, y))

if number_of_colors != 0:
    all_colors_blocks = get_colors(colors, number_of_beams)
schematic = mcschematic.MCSchematic()

place_blocks()
save_schematic()