import random

class Minesweeper:
    """BillyBot's gateway to everything minesweeper"""

    _game_tile_map = {}
    _width = None
    _height = None
    _mines = None

    _starting_choice = None
    _forbidden_mine_tiles = []
    _used_tiles = []

    def _column_of_tile(self, tile):
        return int((tile - 1) % self._width)

    def _line_of_tile(self, tile):
        return int((tile + tile / self._width - 1) / (self._width + 1))

    def _get_neighboring_tiles(self, tile):
        output = [-1, -1, -1, -1, -1, -1, -1, -1]

        # Tile to the left
        if self._column_of_tile(tile) > 0:
            output[0] = tile - 1
        # Tile to the right
        if self._column_of_tile(tile) < self._width - 1:
            output[1] = tile + 1
        # Tile above
        if self._line_of_tile(tile) > 0 and self._line_of_tile(tile) > 0:
            output[2] = tile - self._width
        # Tile below
        if self._line_of_tile(tile) < self._height - 1:
            output[3] = tile + self._width
        # Tile left up
        if self._column_of_tile(tile) > 0 and self._line_of_tile(tile) > 0:
            output[4] = tile - 1 - self._width
        # Tile right up
        if self._column_of_tile(tile) < self._width - 1 and self._line_of_tile(tile) > 0:
            output[5] = tile + 1 - self._width
        # Tile left down
        if self._column_of_tile(tile) > 0 and self._line_of_tile(tile) < self._height - 1:
            output[6] = tile - 1 + self._width
        # Tile right down
        if self._column_of_tile(tile) < self._width - 1 and self._line_of_tile(tile) < self._height - 1:
            output[7] = tile + 1 + self._width

        for val in output:
            if val < -1:
                print(val)
        return output

    def __init__(self, width, height, mines):
        self._width = width
        self._height = height
        self._mines = mines

    def generate(self):
        self._starting_choice = random.randint(1, self._width*self._height)
        self._forbidden_mine_tiles = []
        self._used_tiles = []

        self._forbidden_mine_tiles.append(self._starting_choice)
        for neighboring_tile in self._get_neighboring_tiles(self._starting_choice):
            if neighboring_tile != -1:
                self._forbidden_mine_tiles.append(neighboring_tile)

        # Generates all of the mines
        for i in range(self._mines):
            random_tile = -1
            while (random_tile in self._used_tiles or random_tile == -1 or random_tile in self._forbidden_mine_tiles):
                random_tile = random.randint(1, self._width * self._height)

            self._game_tile_map[random_tile] = -1
            self._used_tiles.append(random_tile)

        # Set default value of none mines at 0
        for tile in range(1, self._width * self._height + 1):
            if not tile in self._game_tile_map:
                self._game_tile_map[tile] = 0

        # Actually calculate none mine tile values
        for tile in range(1, self._width * self._height + 1):
            if self._game_tile_map[tile] >= 0:
                for neighboring_tile in self._get_neighboring_tiles(tile):
                    if neighboring_tile != -1:
                        if self._game_tile_map[neighboring_tile] < 0:
                            self._game_tile_map[tile] += -self._game_tile_map[neighboring_tile]

    def __str__(self):
        output_message = ""

        for final_tile in sorted(self._game_tile_map.keys()):
            if not final_tile in self._forbidden_mine_tiles:
                output_message += "||"

            if self._game_tile_map[final_tile] == -1:
                output_message += ":boom:"
            elif self._game_tile_map[final_tile] == 0:
                output_message += ":zero:"
            elif self._game_tile_map[final_tile] == 1:
                output_message += ":one:"
            elif self._game_tile_map[final_tile] == 2:
                output_message += ":two:"
            elif self._game_tile_map[final_tile] == 3:
                output_message += ":three:"
            elif self._game_tile_map[final_tile] == 4:
                output_message += ":four:"
            elif self._game_tile_map[final_tile] == 5:
                output_message += ":five:"
            elif self._game_tile_map[final_tile] == 6:
                output_message += ":six:"
            elif self._game_tile_map[final_tile] == 7:
                output_message += ":seven:"
            elif self._game_tile_map[final_tile] == 8:
                output_message += ":eight:"
            elif self._game_tile_map[final_tile] == 9:
                output_message += ":nine:"

            if not final_tile in self._forbidden_mine_tiles:
                output_message += "||"

            if self._column_of_tile(final_tile) == self._width - 1:
                output_message += "\n"
        return output_message

    def get_width(self):
        """Returns game width"""
        return self._width

    def get_height(self):
        """Returns game width"""
        return self._height

    def get_mines(self):
        """Returns game width"""
        return self._mines