import math

def hex_to_norm_tuple(hex):
    return list(float(int(hex[i:i+2], 16)/255) for i in (0, 2, 4))

def sRGB_to_LsRGB(color):
    for number, value in enumerate(color):
        if value >= 0.04045:
            color[number] = ((value + 0.055)/(1 + 0.055))**2.4
        else:
            color[number] = value/12.92
    
    return color

def LsRGB_to_sRGB(color):
    for number, value in enumerate(color):
        if value >= 0.0031308:
            color[number] = 1.055*value**(1/2.4) - 0.055
        else:
            color[number] = 12.92*value
    
    return color

def LsRGB_to_OKLAB(color):
    l = (0.4122214708*color[0] + 0.5363325363*color[1] + 0.0514459929*color[2])**(1/3)
    m = (0.2119034982*color[0] + 0.6806995451*color[1] + 0.1073969566*color[2])**(1/3)
    s = (0.0883024619*color[0] + 0.2817188376*color[1] + 0.6299787005*color[2])**(1/3)

    color[0] = 0.2104542553*l + 0.7936177850*m - 0.0040720468*s
    color[1] = 1.9779984951*l - 2.4285922050*m + 0.4505937099*s
    color[2] = 0.0259040371*l + 0.7827717662*m - 0.8086757660*s

    return color

def OKLAB_to_LsRGB(color):
    l = (color[0] + 0.3963377774*color[1] + 0.2158037573*color[2])**3
    m = (color[0] - 0.1055613458*color[1] - 0.0638541728*color[2])**3
    s = (color[0] - 0.0894841775*color[1] - 1.2914855480*color[2])**3

    color[0] = 4.0767416621*l - 3.3077115913*m + 0.2309699292*s
    color[1] = -1.2684380046*l + 2.6097574011*m - 0.3413193965*s
    color[2] = -0.0041960863*l - 0.7034186147*m + 1.7076147010*s

    return color

def sRGB_to_OKLAB(color):
    return LsRGB_to_OKLAB(sRGB_to_LsRGB(color))

def glass_sequence_to_sRGB(block_list):
    n = len(block_list) - 1
    r = (block_list[0][0] + sum(2**(i-1)*block_list[i][0] for i in range(1, n + 1)))/2**n
    g = (block_list[0][1] + sum(2**(i-1)*block_list[i][1] for i in range(1, n + 1)))/2**n
    b = (block_list[0][2] + sum(2**(i-1)*block_list[i][2] for i in range(1, n + 1)))/2**n

    return [r, g ,b]

def find_best_blocks(interpolated_colors, palette):
    best_blocks = []
    for color in interpolated_colors:
        closest = 0
        smallest_distance = math.inf
        for num, (stack_color, _, _, _, _) in enumerate(palette):
            euclidean_distance = euclidean_distance_function_for_tuples(color, stack_color)
            if euclidean_distance < smallest_distance:
                smallest_distance = euclidean_distance
                closest = num

        best_blocks.append(palette[closest][1:])

    return best_blocks

def euclidean_distance_function_for_tuples(color1, color2):
    return (sum((x - y)**2 for x, y in zip(color1, color2)))**(1/2)

def create_all_possible_colors(MC_colors_RGB):
    all_possible_colors = []
    for color1 in range(len(MC_colors_RGB)):
        for color2 in range(len(MC_colors_RGB)):
            for color3 in range(len(MC_colors_RGB)):
                for color4 in range(len(MC_colors_RGB)):
                    all_possible_colors.append([glass_sequence_to_sRGB([MC_colors_RGB[color1],
                                                                MC_colors_RGB[color2],
                                                                MC_colors_RGB[color3],
                                                                MC_colors_RGB[color4]]),
                                                                color1, color2, color3, color4])
                    
    return all_possible_colors

def distances_between_primary_colors(primary_colors):
    euclidean_distances_list = []
    xyz_distances_list = []

    for color_number in range(len(primary_colors)):
        xyz_distance = list((x - y) for x, y in zip(primary_colors[color_number - 1], primary_colors[color_number]))
        xyz_distances_list.append(xyz_distance)
        euclidean_distances_list.append(euclidean_distance_function_for_tuples(primary_colors[color_number - 1], primary_colors[color_number]))
            
    return xyz_distances_list, euclidean_distances_list

def find_interpolated_points(xyz_distances_list, euclidean_distances_list, interpolated_colors, hop_distance, number_of_beams):
    color = 0
    for beam in range(number_of_beams - 1):
        current_distance = (beam + 1)*hop_distance
        distance_left = hop_distance
        filled_distance = 0
        leftover_xyz = [0, 0, 0]
        while True:
            if current_distance < sum(euclidean_distances_list[:color + 1]):
                interpolated_colors.append([interpolated_colors[beam][0] - xyz_distances_list[color][0]*distance_left/euclidean_distances_list[color] - leftover_xyz[0],
                                            interpolated_colors[beam][1] - xyz_distances_list[color][1]*distance_left/euclidean_distances_list[color] - leftover_xyz[1],
                                            interpolated_colors[beam][2] - xyz_distances_list[color][2]*distance_left/euclidean_distances_list[color] - leftover_xyz[2]])
                break

            else:
                distance_left = current_distance - sum(euclidean_distances_list[:color + 1])
                fill_distance = hop_distance - distance_left - filled_distance
                filled_distance += fill_distance
                leftover_xyz[0] += xyz_distances_list[color][0]*fill_distance/euclidean_distances_list[color] 
                leftover_xyz[1] += xyz_distances_list[color][1]*fill_distance/euclidean_distances_list[color] 
                leftover_xyz[2] += xyz_distances_list[color][2]*fill_distance/euclidean_distances_list[color]
                color += 1

    return interpolated_colors

def id_to_glass_name(id):
    name_list = [
        "white_stained_glass",
        "light_gray_stained_glass",
        "gray_stained_glass",
        "black_stained_glass",
        "brown_stained_glass",
        "red_stained_glass",
        "orange_stained_glass",
        "yellow_stained_glass",
        "lime_stained_glass",
        "green_stained_glass",
        "cyan_stained_glass",
        "light_blue_stained_glass",
        "blue_stained_glass",
        "purple_stained_glass",
        "magenta_stained_glass",
        "pink_stained_glass"]
    
    return name_list[id]

def get_colors(primary_colors_for_beacon_sRGB_hex, number_of_beams):
    minecraft_colors_sRGB_hex = ["F9FFFE", "9D9D97", "474F52", "1D1D21",
                                 "835432", "B02E26", "F9801D", "FED83D",
                                 "80C71F", "5E7C16", "169C9C", "3AB3DA",
                                 "3C44AA", "8932B8", "C74EBD", "F38BAA"]
    
    minecraft_colors_dec_sRGB = list(hex_to_norm_tuple(color) for color in minecraft_colors_sRGB_hex)
    all_possible_minecraft_colors_sRGB = create_all_possible_colors(minecraft_colors_dec_sRGB)
    all_possible_minecraft_colors_OKLAB = list([sRGB_to_OKLAB(color[0]), color[1], color[2], color[3], color[4]] for color in all_possible_minecraft_colors_sRGB)

    primary_colors_for_beacon_OKLAB = list(sRGB_to_OKLAB(hex_to_norm_tuple(color)) for color in primary_colors_for_beacon_sRGB_hex)
    xyz_distances_list, euclidean_distances_list = distances_between_primary_colors(primary_colors_for_beacon_OKLAB)

    interpolated_colors = [primary_colors_for_beacon_OKLAB[-1]]
    hop_distance = sum(euclidean_distances_list)/number_of_beams

    interpolated_colors_OKLAB = find_interpolated_points(xyz_distances_list, euclidean_distances_list, interpolated_colors, hop_distance, number_of_beams)

    return find_best_blocks(interpolated_colors_OKLAB, all_possible_minecraft_colors_OKLAB)