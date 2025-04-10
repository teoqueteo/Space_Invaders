import json
import os
import pygame
from random import choice
from os.path import abspath, dirname, join

# --- Paths ---
BASE_PATH = abspath(dirname(__file__))
IMAGE_PATH = join(BASE_PATH, 'images/')
FONT_PATH = join(BASE_PATH, 'fonts/')
AUDIO_PATH = join(BASE_PATH, 'audio/')

# --- Colors ---
WHITE = (255, 255, 255)
GREEN = (78, 255, 87)
RED = (237, 28, 36)

# --- Initialize ---
pygame.init()
pygame.font.init()
pygame.mixer.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders - Single Player")
CLOCK = pygame.time.Clock()
FONT = pygame.font.Font(join(FONT_PATH, 'space_invaders.ttf'), 24)

# --- Load image utility ---
def load_image(name, scale=None):
    img = pygame.image.load(join(IMAGE_PATH, name)).convert_alpha()
    if scale:
        img = pygame.transform.scale(img, scale)
    return img

# --- Load images ---
IMAGES = {
    'ship': load_image('ship.png'),
    'laser': load_image('laser.png'),
    'enemylaser': load_image('enemylaser.png'),
    'enemy1_1': load_image('enemy1_1.png'),
    'enemy1_2': load_image('enemy1_2.png'),
    'enemy2_1': load_image('enemy2_1.png'),
    'enemy2_2': load_image('enemy2_2.png'),
    'enemy3_1': load_image('enemy3_1.png'),
    'enemy3_2': load_image('enemy3_2.png'),
    'mystery': load_image('mystery.png'),
    'explosiongreen': load_image('explosionGreen.png'),
    'explosionblue': load_image('explosionBlue.png'),
    'explosionpurple': load_image('explosionPurple.png'),
}

SOUNDS = {
    'shoot': pygame.mixer.Sound(join(AUDIO_PATH, 'shoot.wav')),
    'shoot2': pygame.mixer.Sound(join(AUDIO_PATH, 'shoot2.wav')),
    'invaderkilled': pygame.mixer.Sound(join(AUDIO_PATH, 'invaderkilled.wav')),
    'mysteryentered': pygame.mixer.Sound(join(AUDIO_PATH, 'mysteryentered.wav')),
    'mysterykilled': pygame.mixer.Sound(join(AUDIO_PATH, 'mysterykilled.wav')),
    'shipexplosion': pygame.mixer.Sound(join(AUDIO_PATH, 'shipexplosion.wav')),
}


# --- Función para cargar el ranking ---

SINGLE_RANKING_FILE = os.path.join(os.path.dirname(__file__), 'single_ranking.json')

def single_load_ranking():
    if os.path.exists(SINGLE_RANKING_FILE):
        with open(SINGLE_RANKING_FILE, 'r') as f:
            return json.load(f)
    return []

def single_save_score(name, score):
    single_ranking = single_load_ranking()
    single_ranking.append({'name': name, 'score': score})
    single_ranking = sorted(single_ranking, key=lambda x: x['score'], reverse=True)[:5]  # Top 5
    with open(SINGLE_RANKING_FILE, 'w') as f:
        json.dump(single_ranking, f)


# --- Función para cargar el ranking ---
MULTI_RANKING_FILE = os.path.join(os.path.dirname(__file__), 'multi_ranking.json')

def multi_load_ranking():
    if os.path.exists(MULTI_RANKING_FILE):
        with open(MULTI_RANKING_FILE, 'r') as f:
            return json.load(f)
    return []

def multi_save_score(name, score):
    multi_ranking = multi_load_ranking()
    multi_ranking.append({'name': name, 'score': score})
    multi_ranking = sorted(multi_ranking, key=lambda x: x['score'], reverse=True)[:5]  # Top 5
    with open(MULTI_RANKING_FILE, 'w') as f:
        json.dump(multi_ranking, f)


LEVEL_PATTERNS = [
    [
        '  111111  ',
        '  222222  ',
        '3333333333',
    ],
    [
        '  222222  ',
        '  111111  ',
        '3333333333',
        '   2222   ',
    ],
    [
        '1111111111',
        '  222222  ',
        '   3333   ',
    ],
    [
        '   1111   ',
        ' 22222222 ',
        '  333333  ',
        '   1111   ',
    ],
    [
        '    1     ',
        '   222    ',
        '  33333   ',
        ' 2222222  ',
    ],
    [
        '1 1 1 1 1 ',
        ' 2 2 2 2 2',
        ' 33333333',
    ],
    [
        '1111111111',
        '2222222222',
        '3333333333',
    ],
    [
        '1 3 3 3 1 ',
        '3 1 2 1 3',
        '2 3 1 3 2',
    ],
    [
        '1 1 1 1 1 ',
        '2 2 2 2 2 ',
        '3 3 3 3 3 ',
        '1 2 3 2 1 ',
    ],
    [
        '    111   ',
        '  2222222 ',
        ' 333333333',
        '    111   ',
    ],
    [
        '1 2 3 2 1 ',
        '3 2 1 2 3 ',
        '1 2 3 2 1 ',
        '3 2 1 2 3 ',
    ],
    [
        '1   1  333 ',
        ' 1 1   3  3',
        '  1    3  3',
        ' 1 1   3  3',
        '1   1  333 ',
    ],
    [
        '1111111111',
        '   2222   ',
        '3333333333',
        '   2222   ',
    ],
    [
        '1 3 1 3 1 ',
        '2 2 2 2 2 ',
        '3 1 3 1 3 ',
    ],
    [
        ' 1 2 3 1 2',
        '3 1 2 3 1 ',
        ' 2 3 1 2 3',
    ],
    [
        '1         ',
        ' 2        ',
        '  3       ',
        '   1      ',
        '    2     ',
        '     3    ',
    ],
    [
        '111   111 ',
        '222   222 ',
        '333   333 ',
    ],
    [
        '     222 ',
        '   2    2',
        '      22 ',
        '   2    2',
        '     222 ',
    ],
    [
        '1 1 1 1 1 ',
        ' 2 2 2 2 2',
        '  3 3 3 3 ',
        '   1 1 1  ',
    ],
    [
        '    1     ',
        '   222    ',
        '  33333   ',
        '   222    ',
        '    1     ',
    ],
    [
        ' 12321 ',
        '1223221',
        ' 12321 ',
    ],
    [
        '111  3  111 ',
        '222  3  222 ',
        '111  3  111 ',
    ],
    [ 
        '3 3 3 3 3 ',
        '2 2 2 2 2 ',
        '1 1 1 1 1 ',
        '2 2 2 2 2 ',
        '3 3 3 3 3 ',
    ],
    [
        '1111111111',
        '   2222   ',
        '   3333   ',
        '   2222   ',
        '1111111111',
    ],
    [
        '1111331111',
        '  222222  ',
        '   3333   ',          #GG bruh
        '  222222  ',
        '1111331111',
    ],
]

# --- Extra (mystery ship) class ---
class Extra(pygame.sprite.Sprite):
    def __init__(self, side, screen_width):
        super().__init__()
        self.image = IMAGES['mystery']
        self.speed = -3 if side == 'right' else 3
        x = screen_width + 50 if side == 'right' else -50
        self.rect = self.image.get_rect(topleft=(x, 80))

    def update(self):
        self.rect.x += self.speed

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type):
        super().__init__()
        self.enemy_type = enemy_type
        self.images = {
            '1': [IMAGES['explosionpurple']],
            '2': [IMAGES['explosionblue']],
            '3': [IMAGES['explosiongreen']],
        }
        self.image = self.images[enemy_type][0]
        self.rect = self.image.get_rect(center=(x, y))
        self.life_time = 500  # Duración de la explosión en milisegundos
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.spawn_time > self.life_time:
            self.kill()

# --- Laser class ---
class Laser(pygame.sprite.Sprite):
    def __init__(self, pos, speed, screen_height, source='player'):
        super().__init__()
        self.image = IMAGES['laser'] if source == 'player' else IMAGES['enemylaser']
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed
        self.height_y_constraint = screen_height

    def destroy(self):
        if self.rect.y <= -50 or self.rect.y >= self.height_y_constraint + 50:
            self.kill()

    def update(self):
        self.rect.y += self.speed
        self.destroy()

# --- Block class ---
class Block(pygame.sprite.Sprite):
    def __init__(self, size, color, x, y):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))


def alien_shoot(aliens, enemy_lasers, screen_height, sound):
    if aliens:
        random_alien = choice(aliens.sprites())
        laser = Laser(random_alien.rect.center, 6, screen_height, source='enemy')
        enemy_lasers.add(laser)
        sound.play()

# --- Create block pattern ---
def create_block_pattern(x_offset, y_offset, size, color):
    shape = [
        '     x     ',
        '    xxx    ',
        '  xxxxxxx  ',
        ' xxxxxxxxx ',
        'xxxxxxxxxxx',
        'xxxxxxxxxxx',
        'xxxxxxxxxxx',
        'xxx     xxx',
        'xx       xx'
    ]
    
    blocks = pygame.sprite.Group()
    for row_idx, row in enumerate(shape):
        for col_idx, char in enumerate(row):
            if char == 'x':
                x = x_offset + col_idx * size
                y = y_offset + row_idx * size
                blocks.add(Block(size, color, x, y))
    return blocks