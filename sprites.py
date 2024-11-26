import random
import pygame
from settings import *

# Types list:
# "." -> unknown
# "X" -> mine
# "C" -> clue
# "/" -> empty

class Tile:
    def __init__(self, x, y, image, type, revealed=False, flagged=False):
        self.x, self.y = x * TILESIZE, y * TILESIZE
        self.image = image
        self.type = type
        self.revealed = revealed
        self.flagged = flagged

    def draw(self, board_surface):
        if not self.flagged and self.revealed:
            board_surface.blit(self.image, (self.x, self.y))
        elif self.flagged and not self.revealed:
            board_surface.blit(tile_flag, (self.x, self.y))
        elif not self.revealed:
            board_surface.blit(tile_unknown, (self.x, self.y))

    def __repr__(self):
        return self.type


class Board:
    def __init__(self):
        self.board_surface = pygame.Surface((WIDTH, HEIGHT))
        self.board_list = [[Tile(col, row, tile_empty, ".") for row in range(ROWS)] for col in range(COLS)]
        self.first_click = True  # Mark to indicate the first click
        self.dug = []
        self.shield = 1

    def place_mines(self, safe_x=None, safe_y=None):
        for _ in range(AMOUNT_MINES):
            while True:
                x = random.randint(0, ROWS - 1)
                y = random.randint(0, COLS - 1)

                # Ensure the first click is safe by avoiding the first tile and its neighbors
                if safe_x is not None and safe_y is not None:
                    if abs(x - safe_x) <= 1 and abs(y - safe_y) <= 1:
                        continue

                if self.board_list[x][y].type == ".":
                    self.board_list[x][y].image = tile_mine
                    self.board_list[x][y].type = "X"
                    break

    def place_clues(self):
        for x in range(ROWS):
            for y in range(COLS):
                if self.board_list[x][y].type != "X":
                    total_mines = self.check_neighbours(x, y)
                    if total_mines > 0:
                        self.board_list[x][y].image = tile_numbers[total_mines - 1]
                        self.board_list[x][y].type = "C"

    @staticmethod
    def is_inside(x, y):
        return 0 <= x < ROWS and 0 <= y < COLS

    def check_neighbours(self, x, y):
        total_mines = 0
        for x_offset in range(-1, 2):
            for y_offset in range(-1, 2):
                neighbour_x = x + x_offset
                neighbour_y = y + y_offset
                if self.is_inside(neighbour_x, neighbour_y) and self.board_list[neighbour_x][neighbour_y].type == "X":
                    total_mines += 1

        return total_mines

    def draw(self, screen):
        for row in self.board_list:
            for tile in row:
                tile.draw(self.board_surface)
        screen.blit(self.board_surface, (0, 0))

    def dig(self, x, y):
        # Ensure the first click is always safe
        if self.first_click:
            self.first_click = False
            self.place_mines(x, y)  # Place mines, avoiding the first clicked tile and its neighbors
            self.place_clues()      # Place clues after mines are set

        self.dug.append((x, y))
        if self.board_list[x][y].type == "X":
            if self.shield > 0:  # Kích hoạt bảo vệ nếu còn
                self.shield -= 1
                print("Bạn đã sử dụng bảo vệ! Ô này là bom, nhưng bạn được an toàn.")
                return True  # Không thất bại
            else:
                self.board_list[x][y].revealed = True
                self.board_list[x][y].image = tile_exploded
                return False  # Thất bại
        elif self.board_list[x][y].type == "C":
            self.board_list[x][y].revealed = True
            return True

        self.board_list[x][y].revealed = True

        # Reveal nearby safe tiles randomly if this is a safe tile
        nearby_safe_tiles = [
            (nx, ny) for nx in range(max(0, x - 1), min(ROWS - 1, x + 1) + 1)
            for ny in range(max(0, y - 1), min(COLS - 1, y + 1) + 1)
            if (nx, ny) != (x, y) and self.board_list[nx][ny].type != "X" and (nx, ny) not in self.dug
        ]

        random.shuffle(nearby_safe_tiles)
        for nx, ny in nearby_safe_tiles:
            if (nx, ny) not in self.dug:
                self.dig(nx, ny)

        return True

    def display_board(self):
        for row in self.board_list:
            print(row)

    def hint(self):
        # Generate a list of revealed tiles
        revealed_tiles = [(x, y) for x in range(ROWS) for y in range(COLS) if self.board_list[x][y].revealed]

        # If there are no revealed tiles, we cannot give a hint
        if not revealed_tiles:
            return False

        # Randomly pick a revealed tile
        x, y = random.choice(revealed_tiles)

        # Find unrevealed, non-mine tiles around the chosen tile
        possible_hints = [
            (nx, ny) for x_offset in range(-1, 2) for y_offset in range(-1, 2)
            if self.is_inside(nx := x + x_offset, ny := y + y_offset)
            and not self.board_list[nx][ny].revealed
            and self.board_list[nx][ny].type != "X"
        ]

        # If there are possible hints, reveal one randomly
        if possible_hints:
            nx, ny = random.choice(possible_hints)
            self.board_list[nx][ny].revealed = True
            return True

        # Return False if no valid hint is found
        return False
