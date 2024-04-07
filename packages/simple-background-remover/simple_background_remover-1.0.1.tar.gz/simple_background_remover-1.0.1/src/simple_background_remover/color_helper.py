import math

class _ColorHelper:
    """
    Contains logic for handling color-related tasks.
    """

    MAX_COLOR_DIFFERENCE: float = 764.83
    MIN_WIGGLE_ROOM: float = 0.03
    TRANSPARENT_COLOR: tuple[int, int, int] = (0,0,0,0)

    def __init__(self, background_color):
        self.__wiggle_room: float = self.MIN_WIGGLE_ROOM
        self.background_color: tuple[int, int, int] = background_color
        self.min_red: int | None = None
        self.max_red: int | None = None
        self.min_blue: int | None = None
        self.max_blue: int | None = None
        self.min_green: int | None = None
        self.max_green: int | None = None

    def __mins_and_maxes_not_initialized(self) -> bool:
        return (self.min_red is None \
                or self.max_red is None \
                or self.min_green is None \
                or self.max_green is None \
                or self.min_blue is None \
                or self.max_blue is None)

    def __initialize_mins_and_maxes(self) -> None:
        self.min_red = self.__get_min_color_value(self.background_color[0])
        self.max_red = self.__get_max_color_value(self.background_color[0])
        self.min_green = self.__get_min_color_value(self.background_color[1])
        self.max_green = self.__get_max_color_value(self.background_color[1])
        self.min_blue = self.__get_min_color_value(self.background_color[2])
        self.max_blue = self.__get_max_color_value(self.background_color[2])

    def __get_min_color_value(self, color_value: tuple[int, int, int]) -> float:
        min_value = round(color_value * (1 - self.__wiggle_room))

        if min_value < 0:
            min_value = 0

        return min_value

    def __get_max_color_value(self, color_value: tuple[int, int, int]) -> float:
        max_value = round((color_value * (1 + self.__wiggle_room)) + 1)

        if max_value >= 255:
            max_value = 256

        return max_value
    
    def get_wiggle_room(self) -> float:
        return self.__wiggle_room
    
    def set_wiggle_room(self, wiggle_room_value: float) -> None:
        self.__wiggle_room = wiggle_room_value
        self.__initialize_mins_and_maxes()

    def is_close_to_background(self, color_r_value, color_g_value, color_b_value) -> bool:
        bg_r_value = self.background_color[0]
        bg_g_value = self.background_color[1]
        bg_b_value = self.background_color[2]

        if (color_r_value, color_g_value, color_b_value) == (bg_r_value, bg_g_value, bg_b_value):
            return True

        if self.__mins_and_maxes_not_initialized():
            self.__initialize_mins_and_maxes()

        red_in_range = color_r_value in range(self.min_red, self.max_red)
        green_in_range = color_g_value in range(self.min_green, self.max_green)
        blue_in_range = color_b_value in range(self.min_blue, self.max_blue)

        return red_in_range and green_in_range and blue_in_range

    def get_color_difference(self, average_color: tuple[int, int, int]) -> bool:
        # Euclidean distance
        delta_r_squared = (average_color[0] - self.background_color[0]) ** 2
        delta_g_squared = (average_color[1] - self.background_color[1]) ** 2
        delta_b_squared = (average_color[2] - self.background_color[2]) ** 2
        average_r = round((average_color[0] + self.background_color[0]) / 2)

        # redmean -> https://en.wikipedia.org/wiki/Color_difference
        term_1 = (2 + (average_r / 256)) * delta_r_squared
        term_2 = 4 * delta_g_squared
        term_3 = (2 + ((255 - average_r) / 256)) * delta_b_squared

        return math.sqrt(term_1 + term_2 + term_3)
    
    def get_ideal_wiggle_room(self, color_difference: float) -> float:
        # In "redmean" Euclidean distance, the largest value (where the background is white
        # and all non-background is black) is 764.83.
        # Take the ratio between calculated color difference and the max possible value (764.83).

        # I find squaring them before dividing gets a more accurate result
        return color_difference ** 2 / self.MAX_COLOR_DIFFERENCE ** 2