from PIL import Image
from color_helper import _ColorHelper

def remove_background(input_filename: str, output_filename: str, wiggle_room: float = None, background_color: tuple[int, int, int] = None) -> None:
    """
    Removes the background of the provided image and saves it as a PNG.
    
    :param input_filename: The path and file name of the input image, including file type.
    :param output_filename: The desired path and file name of the output image, not including file type. 
    :param wiggle_room: Optional parameter between 0 and 1, which contains the +/- %
    range a color can be similar to the background color. If not passed, the wiggle room
    will be auto-determined.
    :param background_color: Optional parameter for the RGB color of the background.
    If not passed, the background will be auto-determined.

    See https://github.com/oversizedcanoe/BackgroundRemover for more detailed info.
    """
    image = Image.open(input_filename).convert("RGBA")
    image_data = image.getdata()
    new_data = []

    if background_color is None:
        background_color = __get_determined_background_color(image)

    helper = _ColorHelper(background_color)

    if wiggle_room is None:
        wiggle_room = __get_ideal_wiggle_room(helper, image_data)

    helper.set_wiggle_room(wiggle_room)
        
    for pixel_data in image_data:
        if helper.is_close_to_background(pixel_data[0], pixel_data[1], pixel_data[2]):
            new_data.append(helper.TRANSPARENT_COLOR)
        else:
            new_data.append(pixel_data)

    image.putdata(new_data)
    file_name = f'{output_filename}-{round(helper.get_wiggle_room(), 3)}.png'
    image.save(file_name, "PNG")
    print(f'Image saved: \'{file_name}\'')
            

def __get_determined_background_color(image: Image.Image) -> tuple[int, int, int]:
    """
    Determines the solid background color of an image by looking at 
    the top-left 5% of the image and taking the average pixel color.
    """
    width, height = image.size
    
    # top 5%
    width_limit = round(width * 0.05)
    height_limit = round(height * 0.05)

    total_pixels = 0
    total_red = 0
    total_green = 0
    total_blue = 0

    for x in range(0, width_limit):
        for y in range(0, height_limit):
            pixel_color = image.getpixel((x,y))
            total_red += pixel_color[0]
            total_green += pixel_color[1]
            total_blue += pixel_color[2]
            total_pixels += 1

    return (round(total_red/total_pixels), round(total_green/total_pixels), round(total_blue/total_pixels))

def __get_ideal_wiggle_room(helper: _ColorHelper, image_data: list) -> float:
    """
    Determine the ideal wiggle room of an image. This is done by determining the contrast between
    foreground and background colors. A larger contrast means a larger wiggle room can be used. A
    smaller contrast means foreground pixels are similar to the background, and we need to
    use a smaller contrast to prevent accidentally transparent-ifying foreground pixels.
    """
    
    total_r = 0
    total_g = 0
    total_b = 0
    foreground_pixels_counted = 0

    # Start with min wiggle room to take a conservative estimate of foreground vs background pixels
    helper.set_wiggle_room(helper.MIN_WIGGLE_ROOM)

    for pixel_data in image_data:
        red = pixel_data[0]
        green = pixel_data[1]
        blue = pixel_data[2]
        if helper.is_close_to_background(red, green, blue) == False:
            total_r += red
            total_g += green
            total_b += blue
            foreground_pixels_counted += 1

    if foreground_pixels_counted == 0:
        # Only possible if image is 'all background', meaning it will be made entirely transparent.
        return helper.MIN_WIGGLE_ROOM
    
    average_r = round(total_r / foreground_pixels_counted)
    average_g = round(total_g / foreground_pixels_counted)
    average_b = round(total_b / foreground_pixels_counted)
    color_difference = helper.get_color_difference((average_r, average_g, average_b))
    ideal_wiggle_room = helper.get_ideal_wiggle_room(color_difference)

    return ideal_wiggle_room