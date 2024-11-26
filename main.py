import pygame
from settings import *
from sprites import *


class Game:
    pygame.init()

    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

    def new(self):
        self.board = Board()
        self.board.display_board()

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.draw()
        else:
            self.end_screen()

    def draw(self):
        self.screen.fill(BGCOLOUR)
        self.board.draw(self.screen)

        if self.board.shield > 0:
            shield_image = pygame.image.load(os.path.join("assets", "khien.jpg"))
            shield_image = pygame.transform.scale(shield_image, (64, 64))
            self.screen.blit(shield_image, (WIDTH - 80, 10))  # Hiển thị ở góc phải trên
        pygame.display.flip()

    def check_win(self):
        for row in self.board.board_list:
            for tile in row:
                if tile.type != "X" and not tile.revealed:
                    return False
        return True

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                mx //= TILESIZE
                my //= TILESIZE

                if event.button == 1:
                    if not self.board.board_list[mx][my].flagged:
                        if not self.board.dig(mx, my):
                            for row in self.board.board_list:
                                for tile in row:
                                    if tile.flagged and tile.type != "X":
                                        tile.flagged = False
                                        tile.revealed = True
                                        tile.image = tile_not_mine
                                    elif tile.type == "X":
                                        tile.revealed = True
                            self.playing = False

                if event.button == 3:
                    if not self.board.board_list[mx][my].revealed:
                        self.board.board_list[mx][my].flagged = not self.board.board_list[mx][my].flagged

                if self.check_win():
                    self.show_win()
                    self.win = True
                    self.playing = False
                    for row in self.board.board_list:
                        for tile in row:
                            if not tile.revealed:
                                tile.flagged = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s and self.board.shield > 0:
                    print("Bảo vệ đã được kích hoạt!")

            # Kích hoạt chức năng gợi ý khi nhấn phím H
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    if self.board.hint():
                        print("Đã gợi ý một ô không có mìn.")
                    else:
                        print("Không còn ô nào để gợi ý.")
    def show_win(self):
        popup_font = pygame.font.Font(None, 48)
        popup_text = popup_font.render('You win!', True, WHITE)

        popup_rect = popup_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        pygame.draw.rect(self.screen, BLACK, (popup_rect.x - 10, popup_rect.y - 10, popup_rect.width + 20, popup_rect.height + 20))
        self.screen.blit(popup_text, popup_rect)

        pygame.display.flip()
        pygame.time.delay(5000)

    def end_screen(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit(0)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    return


game = Game()
while True:
    game.new()
    game.run()
