def guess_camera(device_dims, coating_dims=[0,0,0], 
        camera_style="perspective", angle=0, center=[0, 0]):
    """ 
    Guesses the camera location if you have no idea what a good camera 
    position is. Can look at the device from the side (angle = 0) or at an 
    angle in the xy-plane (rotate around z-axis, *DEGREES* from x-axis). 
    It has been optimized to give decent results, though fine-tuning in the
    .pov file is always encouraged.
    
    :param device_dims: Dimensions of the unit cell
    :type device_dims: list

    :param coating_dims: Dimensions of the coating layer(s)
    :type device_dims: list

    :param camera_style: The desired camera style, currently accepts perspective and orthographic
    :type camera_sylte: string

    :param angle: Rotates the camera around the z-axis (in degrees)
                  0 will look down the x-axis at the side of the device
    :type angle: float
    
    :param center: The center of the device
    :type center: list

    :return: Tuple containing the camera position, camera look at location, and the light position
    :rtype: tuple
    """
    from math import sin, cos, pi

    camera_position = [0, 0, 0]
    light_position = [0, 0, 0]

    deg_to_rads = pi / 180.0
    angle *= deg_to_rads 

    if camera_style == "perspective":
        x_offset = 1.2
        z_scale = 1.0
    elif camera_style == "orthographic":
        x_offset = 1.2
        z_scale = 1.0
    else:
        x_offset = 1.2
        z_scale = 1.0
        print("WARNING: Camera parameters have not been optimized for this style!")

    # Offset for x,y-dimensions
    camera_offset = x_offset * (max(device_dims) + 0.8 * max(coating_dims))

    camera_position[0] = (camera_offset + device_dims[0]) * cos(angle)
    camera_position[1] = (camera_offset + device_dims[0]) * sin(angle)
    camera_position[2] = z_scale * (device_dims[2] + 0.5 * coating_dims[2])
    camera_look_at = [center[0], center[1], (-0.66 * device_dims[2] + 0.50 * coating_dims[2])]

    light_offset = camera_offset * 1.25 
    light_position[0] = (device_dims[0] + light_offset) * cos(angle - 12 * deg_to_rads)
    light_position[1] = (device_dims[1] + light_offset/1.0) * sin(angle - 12 * deg_to_rads)
    light_position[2] = camera_position[2] + light_offset/3.0

    #print("Write_POV estimated camera parameters:")
    #print("camera_position : " , camera_position)
    #print("camera_look_at : ", camera_look_at)

    return camera_position, camera_look_at, light_position

def color_and_finish(dev_string, default_color_dict, material, use_default_colors, 
        custom_color = [0, 0.6667, 0.667, 0, 0], ior = 1, use_finish = "dull",
        custom_finish = ""):
    """ 
    Sets the color and finish of the object and appends this to the device string.
    The filter and transmit terms are both 0 by default.
    Do not remove the underscore from filter_, as filter is a function in python.

    Users may specify their own custom color scheme or use the default, 
    which is based on the material type specified in the device file.

    Available finishes: see ``use_finish``  parameter for details. 
    Specifying "material" will use the material finish (currently "Si", 
    "SiO2", or "subst") finish in order to accomodate multiple material 
    types in a device. The substrate will always have the "dull" finish.

    If using the "custom" finish, the finish details must be specified in the
    custom_finish variable or it will default to "dull".

    If you request one of the following finishes, the code will overwrite 
    your transmit and filter values. If you do now want this to happen, you
    should declare your own custom finish.

    :param dev_string: String describing the device
    :type dev_string: str

    :param default_color_dict: Dictionary containing the default finishes for the 
                               various material types
    :type default_color_dict: dict

    :param use_default_colors: Boolean to select which color set to use. True will 
                               assign colors based on the material type ("Si", 
                               "SiO2", and "subst"). False will use user-assigned 
                               custom colors.
    :type use_default_colors: bool

    :param custom_color: RGBFT values describing a single color. If you set 
                         ``use_default_colors=False`` but forget to specify a 
                         custom color, it will use #00aaaa (the Windows 95 
                         default desktop color).

                         RGB values must be in the range [0,1]. F and T are
                         filter and transmit, respectively. F and T are 
                         optional and both default to 0.
    :type custom_color: list

    :param ior: Index of refraction for transparent finish only
    :type ior: float

    :param use_finish: Select the finish that you want. Current options are:
                       "material", "Si", "SiO2", "glass", "bright_metal", 
                       "dull_metal", "irid", "billiard", "dull", "custom"
    :type use_finish: str

    :param custom_finish: User-defined custom finish. Set ``use_finish=custom``
                          to call this option.
    :type custom_finish: str
    """

    # These two values only matter for SiO2, translucent, glass, and irid finishes
    transmit, filter_ = 0, 0

    # Set finish
    if use_finish == "material":
        use_finish = material

    if use_finish == "Si" or use_finish == "silicon":
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "diffuse 0.2 \n\t\t\t" \
                + "brilliance 5 \n\t\t\t" \
                + "phong 1 \n\t\t\t" \
                + "phong_size 250 \n\t\t\t" \
                + "roughness 0.01 \n\t\t\t" \
                + "reflection <0.10, 0.10, 0.5> metallic \n\t\t\t" \
                + " metallic \n\t\t\t" \
                + "{cb:c}\n\t\t".format(cb=125) \
                + "interior {ob:c} ior 4.24 {cb:c}\n\t\t".format(ob=123, cb=125)
                # IOR taken from blender

    elif use_finish == "SiO2":
        filter_ = 0.98
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "specular 0.6 \n\t\t\t" \
                + "brilliance 5 \n\t\t\t" \
                + "roughness 0.001 \n\t\t\t" \
                + "reflection {ob:c} 0.0, 1.0 fresnel on {cb:c}\n\t\t\t".format(ob=123, cb=125) \
                + "{cb:c}\n\t\t".format(cb=125) \
                + "interior {ob:c} ior 1.45 {cb:c}\n\t\t".format(ob=123, cb=125)

    elif use_finish == "translucent":
        transmit = 0.02
        filter_ = 0.50
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "emission 0.25 \n\t\t\t" \
                + "diffuse 0.75 \n\t\t\t" \
                + "specular 0.4 \n\t\t\t" \
                + "brilliance 4 \n\t\t\t" \
                + "reflection {ob:c} 0.5 fresnel on {cb:c}\n\t\t\t".format(ob=123, cb=125) \
                + "{cb:c}\n\t\t".format(cb=125) \
                + "interior {ob:c} ior {0} {cb:c}\n\t\t".format(ior, ob=123, cb=125)

    elif use_finish == "glass":
        filter_ = 0.95
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "specular 0.6 \n\t\t\t" \
                + "phong 0.8 \n\t\t\t" \
                + "brilliance 5 \n\t\t\t" \
                + "reflection {ob:c} 0.2, 1.0 fresnel on {cb:c}\n\t\t\t".format(ob=123, cb=125) \
                + "{cb:c}\n\t\t".format(cb=125) \
                + "interior {ob:c} ior 1.5 {cb:c}\n\t\t".format(ob=123, cb=125)

    elif use_finish == "dull_metal":
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "emission 0.1 \n\t\t\t" \
                + "diffuse 0.1 \n\t\t\t" \
                + "specular 1.0 \n\t\t\t" \
                + "roughness 0.001 \n\t\t\t" \
                + "reflection 0.5 metallic \n\t\t\t" \
                + " metallic \n\t\t\t" \
                + "{cb:c}\n\t\t".format(cb=125)

    elif use_finish == "bright_metal":
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "emission 0.2 \n\t\t\t" \
                + "diffuse 0.3 \n\t\t\t" \
                + "specular 0.8 \n\t\t\t" \
                + "roughness 0.01 \n\t\t\t" \
                + "reflection 0.5 metallic \n\t\t\t" \
                + " metallic \n\t\t\t" \
                + "{cb:c}\n\t\t".format(cb=125)

    elif use_finish == "irid":
        filter_ = 0.7
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "phong 0.5 \n\t\t\t" \
                + "reflection {ob:c} 0.2 metallic {cb:c}\n\t\t\t".format(ob=123, cb=125) \
                + "diffuse 0.3 \n\t\t\t" \
                + "irid {ob:c} 0.75 thickness 0.5 ".format(ob=123) \
                + "turbulence 0.5 {cb:c}\n\t\t\t".format(cb=125) \
                + "{cb:c}\n\t\t".format(cb=125) \
                + "interior {ob:c} ior 1.5 {cb:c}\n\t\t".format(ob=123, cb=125)

    elif use_finish == "billiard":
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "ambient 0.3 \n\t\t\t" \
                + "diffuse 0.8 \n\t\t\t" \
                + "specular 0.2 \n\t\t\t" \
                + "roughness 0.005 \n\t\t\t" \
                + "metallic 0.5 \n\t\t\t" \
                + "{cb:c}\n\t\t".format(cb=125)

    elif use_finish == "custom":
        extra_finish = custom_finish

    else:
        extra_finish = ""

    # Color declaration for ALL finishes
    if use_default_colors:
        color = default_color_dict[material]
    else:
        color = custom_color

    if len(color) == 3:
        color.append(0)     # filter
        color.append(0)     # transmit

    if use_finish in ["SiO2", "translucent", "glass", "irid"]: 
        print("\nWARNING: color_and_finish is overriding transmit and/or filter value!!")
        color[3] = transmit
        color[4] = filter_

    dev_string += "pigment {ob:c} ".format(ob=123) \
            + "color rgbft " \
            + "<{0}, {1}, {2}, {3}, {4}>".format(color[0], color[1], color[2], color[3], color[4]) \
            + " {cb:c}\n\t\t".format(cb=125)

    # Add the extra bits describing the finish
    #if use_finish != "dull":
    if extra_finish:
        dev_string += extra_finish 

    dev_string += "{cb:c}\n\n\t".format(cb=125)

    return dev_string


def write_header_and_camera(device_dims, coating_dims = [0, 0, 0], 
        camera_style = "perspective", camera_rotate = 60, 
        camera_options = "", camera_loc = [], look_at = [], 
        light_loc = [], up_dir = [0, 0, 1], right_dir = [0, 1, 0], 
        sky = [0, 0, 1.33], bg_color = [1, 1, 1], shadowless=False):
    """
    Does exactly what the function name says. It creates a string 
    containing the header and camera information.

    :param device_dims: Device dimensions
    :type device_dims: list

    :return:
    :rtype: string
    """

    # If any of the three options are missing, take a guess at them
    if camera_loc == [] or look_at == [] or light_loc == []:
        camera_loc, look_at, light_loc = \
                guess_camera(device_dims, coating_dims=coating_dims, \
                camera_style=camera_style, angle = camera_rotate, center=[0, 0])


    #### ---- WRITE POV FILE ---- ####
    header = "#version 3.7;\n"
    header += "global_settings {ob:c} assumed_gamma 1.0 {cb:c}\n\n".format(ob=123, cb=125)
    header += "background {ob:c} ".format(ob=123) \
            + "color rgb <{0}, {1}, {2}> ".format(bg_color[0], bg_color[1], bg_color[2]) \
            + "{cb:c}\n\n".format(cb=125) \
            + "camera \n\t{ob:c}\n\t".format(ob=123) \
            + "{0} {1} \n\t".format(camera_style, camera_options) \
            + "location <{0}, {1}, {2}>\n\t".format(camera_loc[0], camera_loc[1], camera_loc[2]) \
            + "look_at <{0}, {1}, {2}>\n\t".format(look_at[0], look_at[1], look_at[2]) \
            + "up <{0}, {1}, {2}>\n\t".format(up_dir[0], up_dir[1], up_dir[2]) \
            + "right <{0}, {1}, {2}>\n\t".format(right_dir[0], right_dir[1], right_dir[2]) \
            + "sky <{0}, {1}, {2}>\n\t".format(sky[0], sky[1], sky[2]) \
            + "{cb:c}\n\n".format(cb=125)

    if shadowless:
        header += "light_source \n\t{ob:c} \n\t".format(ob=123) \
                + "<{0}, {1}, {2}> \n\t".format(light_loc[0], light_loc[1], light_loc[2]) \
                + "color rgb <1.0,1.0,1.0> \n\t" \
                + "shadowless \n\t" \
                + "{cb:c}\n\n".format(cb=125)
    else:
        header += "light_source \n\t{ob:c} \n\t".format(ob=123) \
                + "<{0}, {1}, {2}> \n\t".format(light_loc[0], light_loc[1], light_loc[2]) \
                + "color rgb <1.0,1.0,1.0> \n\t" \
                + "{cb:c}\n\n".format(cb=125)

    return header


def render_pov(pov_name, image_name, height, width,
        display = False, transparent = True, antialias = True,
        num_threads = 0, open_png = True, render = True):
    
    from os import system

    command = "povray Input_File_Name={0} Output_File_Name={1} ".format(pov_name, image_name) \
            + "+H{0} +W{1}".format(height, width)

    if display:
        command += " Display=on"
    else:
        command += " Display=off"

    if transparent:
        command += " +ua"

    if antialias:
        command += " +A"

    if num_threads != 0:
        command += " +WT{0}".format(num_threads)

    if open_png == True:
        command += " && eog {}".format(image_name)

    if render == True:
        system(command)

    div = '----------------------------------------------------'
    print("write_POV: Render with: \n{0}\n{1}\n{0}".format(div,command))

    return

