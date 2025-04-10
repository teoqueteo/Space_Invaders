import pygame
from pygame import display, event, font, image, mouse
import sys
from os.path import abspath, dirname, join
from random import randint, uniform
import json
from game_objects import single_load_ranking, multi_load_ranking

BASE_PATH = abspath(dirname(__file__))
FONT_PATH = join(BASE_PATH, 'fonts/')
IMAGE_PATH = join(BASE_PATH, 'images/')

WHITE = (255, 255, 255)
GREEN = (78, 255, 87)
BLUE = (80, 255, 239)
PURPLE = (203, 0, 255)
RED = (237, 28, 36)

pygame.init()
pygame.font.init()

SCREEN = display.set_mode((800, 600))
display.set_caption("Space Invaders Menu")

FONT = font.Font(FONT_PATH + 'space_invaders.ttf', 40)
SMALL_FONT = font.Font(FONT_PATH + 'space_invaders.ttf', 24)
TITLE_FONT = font.Font(FONT_PATH + 'space_invaders.ttf', 64)

background_image = image.load(join(IMAGE_PATH, 'background.jpg')).convert()
background_image = pygame.transform.scale(background_image, (800, 600))

class Star:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = randint(0, 800)
        self.y = randint(-600, 0)
        self.speed = uniform(0.5, 2)
        self.size = randint(1, 2)
        self.color = (randint(180, 255), randint(180, 255), randint(180, 255))

    def update(self):
        self.y += self.speed
        if self.y > 600:
            self.reset()

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

stars = [Star() for _ in range(100)]

def start_single_player():
    import single_player
    single_player.run_game()  # Esta función debe terminar limpiamente y regresar aquí

def start_multiplayer():
    import multiplayer
    multiplayer.run_game()  # Esta función debe terminar limpiamente y regresar aquí

def exit_game():
    pygame.quit()
    sys.exit()

def render_glow_text(text, pos, font_obj, base_color, glow_color):
    for offset in range(1, 5):
        glow_surface = font_obj.render(text, True, glow_color)
        SCREEN.blit(glow_surface, (pos[0] - offset, pos[1] - offset))
        SCREEN.blit(glow_surface, (pos[0] + offset, pos[1] + offset))
        SCREEN.blit(glow_surface, (pos[0] - offset, pos[1] + offset))
        SCREEN.blit(glow_surface, (pos[0] + offset, pos[1] - offset))
    text_surface = font_obj.render(text, True, base_color)
    SCREEN.blit(text_surface, pos)

def draw_text_button(text, pos, default_color, hover_color, action=None):
    mouse_pos = mouse.get_pos()
    mouse_click = mouse.get_pressed()

    is_hovered = False
    text_surface = FONT.render(text, True, default_color)
    rect = text_surface.get_rect(topleft=pos)

    if rect.collidepoint(mouse_pos):
        is_hovered = True
        if mouse_click[0] and action:
            action()

    inner_color = hover_color if is_hovered else default_color
    glow_color = (40, 40, 40)
    render_glow_text(text, pos, FONT, inner_color, glow_color)

def load_enemy_image(filename, size):
    img = image.load(join(IMAGE_PATH, filename)).convert_alpha()
    return pygame.transform.scale(img, size)

enemy_images = {
    "enemy1_1.png": {
        "points": "10 PTS",
        "color": (209, 43, 255),
        "size": (40, 30),
        "pos": (320, 400),
        "text_pos": (390, 405)
    },
    "enemy2_1.png": {
        "points": "20 PTS",
        "color": (0, 255, 240),
        "size": (45, 35),
        "pos": (318, 440),
        "text_pos": (390, 445)
    },
    "enemy3_1.png": {
        "points": "30 PTS",
        "color": (6, 253, 90),
        "size": (50, 40),
        "pos": (316, 480),
        "text_pos": (390, 485)
    },
    "mystery.png": {
        "points": "50 PTS",
        "color": (236, 28, 36),
        "size": (60, 30),
        "pos": (312, 520),
        "text_pos": (390, 525)
    }
}


for key, data in enemy_images.items():
    data["img"] = load_enemy_image(key, data["size"])

def main():
    running = True
    while running:
        SCREEN.blit(background_image, (0, 0))

        for star in stars:
            star.update()
            star.draw(SCREEN)

        title_pos = (SCREEN.get_width() // 2 - 300, 50)
        render_glow_text("Space Invaders", title_pos, TITLE_FONT, WHITE, (100, 100, 255))

        draw_text_button("Single Player", (50, 200), GREEN, BLUE, start_single_player)
        draw_text_button("Multiplayer", (450, 200), GREEN, BLUE, start_multiplayer)
        draw_text_button("Exit", (650, 500), RED, PURPLE, exit_game)

        for data in enemy_images.values():
            SCREEN.blit(data["img"], data["pos"])
            text_surface = SMALL_FONT.render(data["points"], True, data["color"])
            SCREEN.blit(text_surface, data["text_pos"])

        for e in event.get():
            if e.type == pygame.QUIT:
                running = False

        single_ranking = single_load_ranking()
        start_y = 260
        colors = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]  # Oro, plata, bronce
        for i, player in enumerate(single_ranking):
            text = f"{i+1}. {player['name']} - {player['score']} pts"
            color = colors[i] if i < 3 else WHITE
            text_surface = font.Font(FONT_PATH + 'space_invaders.ttf', 18).render(text, True, color)
            SCREEN.blit(text_surface, (60, start_y + i * 25))

                # Ranking multijugador
        multi_ranking = multi_load_ranking()
        start_y_multi = 260
        for i, player in enumerate(multi_ranking):
            text = f"{i+1}. {player['name']} - {player['score']} pts"
            color = colors[i] if i < 3 else WHITE
            text_surface = font.Font(FONT_PATH + 'space_invaders.ttf', 18).render(text, True, color)
            SCREEN.blit(text_surface, (460, start_y_multi + i * 25))


        display.update()

    pygame.quit()

# Solo se ejecuta si este archivo se ejecuta directamente
if __name__ == "__main__":
    main()
