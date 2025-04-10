import pygame
import sys
from os.path import abspath, dirname, join
from random import choice, randint
from game_objects import LEVEL_PATTERNS, IMAGES, SOUNDS
from game_objects import multi_save_score, create_block_pattern, alien_shoot, Extra, Explosion, Block, Laser
from single_player import create_aliens

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
pygame.display.set_caption("Space Invaders - Multiplayer")
CLOCK = pygame.time.Clock()
FONT = pygame.font.Font(join(FONT_PATH, 'space_invaders.ttf'), 24)

# --- Load image utility ---
def load_image(name, scale=None):
    img = pygame.image.load(join(IMAGE_PATH, name)).convert_alpha()
    if scale:
        img = pygame.transform.scale(img, scale)
    return img


# --- Player class ---
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, constraint, speed, screen_height, controls, player_id):
        super().__init__()
        self.image = IMAGES['ship']
        self.rect = self.image.get_rect(midbottom=pos)
        self.speed = speed
        self.max_x_constraint = constraint
        self.ready = True
        self.laser_time = 0
        self.laser_cooldown = 600
        self.lasers = pygame.sprite.Group()
        self.screen_height = screen_height
        self.laser_sound = SOUNDS['shoot']
        self.laser_sound.set_volume(0.5)
        self.controls = controls  # Controles para cada jugador
        self.player_id = player_id
        self.score = 0
        self.lives = 3
        self.is_alive = True  # Nuevo atributo para verificar si está vivo

    def get_input(self):
        if not self.is_alive:
            return  # Si el jugador está muerto, no recibe input
        keys = pygame.key.get_pressed()
        if self.controls['right'] and keys[self.controls['right']]:
            self.rect.x += self.speed
        if self.controls['left'] and keys[self.controls['left']]:
            self.rect.x -= self.speed
        if self.controls['shoot'] and keys[self.controls['shoot']] and self.ready:
            self.shoot_laser()
            self.ready = False
            self.laser_time = pygame.time.get_ticks()
            self.laser_sound.play()

    def recharge(self):
        if not self.ready:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_time >= self.laser_cooldown:
                self.ready = True

    def constraint(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= self.max_x_constraint:
            self.rect.right = self.max_x_constraint

    def shoot_laser(self):
        self.lasers.add(Laser(self.rect.center, -8, self.screen_height))

    def update(self):
        if self.is_alive:
            self.get_input()
            self.constraint()
            self.recharge()
            self.lasers.update()

    def die(self):
        """Método para manejar la muerte del jugador."""
        self.is_alive = False
        self.image = IMAGES['explosiongreen']  # Cambia la nave por una explosión verde
        self.rect = self.image.get_rect(center=self.rect.center)  # Centra la explosión en la posición de la nave
        SOUNDS['shipexplosion'].play()
        pygame.time.wait(500)  # Espera para la animación de la explosión
        self.lasers.empty()  # Elimina las balas del jugador muerto


# --- Alien class ---
class Alien(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        # Definir las imágenes de animación para cada tipo de enemigo
        self.animations = {
            '1': [IMAGES['enemy1_1'], IMAGES['enemy1_2']],
            '2': [IMAGES['enemy2_1'], IMAGES['enemy2_2']],
            '3': [IMAGES['enemy3_1'], IMAGES['enemy3_2']],
        }
        self.image = self.animations[color][0]  # Empezamos con la primera imagen
        self.rect = self.image.get_rect(topleft=(x, y))
        self.value = {'1': 10, '2': 20, '3': 30}[color]
        self.color = color  # Guardamos el color para seleccionar la animación correcta
        self.animation_timer = 0  # Temporizador para alternar la imagen
        self.animation_speed = 500  # Cada cuántos milisegundos cambiar la imagen (500 ms)
    
    def update(self, direction):
        # Actualizamos el temporizador
        current_time = pygame.time.get_ticks()
        if current_time - self.animation_timer > self.animation_speed:
            # Alternamos entre las dos imágenes
            current_image_index = self.animations[self.color].index(self.image)
            next_image_index = (current_image_index + 1) % 2
            self.image = self.animations[self.color][next_image_index]
            self.animation_timer = current_time  # Reiniciamos el temporizador
        
        self.rect.x += direction

alien_lasers = pygame.sprite.Group()

def get_player_name(player_num):
    input_active = True
    name = ''
    input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 32, 300, 64)
    color_active = pygame.Color('lightskyblue3')
    base_font = pygame.font.Font(join(FONT_PATH, 'space_invaders.ttf'), 32)

    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if name:
                        return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 10 and event.unicode.isalnum():
                        name += event.unicode

        SCREEN.fill((0, 0, 0))
        prompt = base_font.render(f"Jugador {player_num}, Ingresa tu nombre:", True, WHITE)
        text_surface = base_font.render(name, True, WHITE)
        SCREEN.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
        SCREEN.blit(text_surface, (input_rect.x + 10, input_rect.y + 10))
        pygame.draw.rect(SCREEN, color_active, input_rect, 2)
        pygame.display.flip()
        CLOCK.tick(60)

def handle_collisions(player1, player2, aliens, enemy_lasers, blocks, extra_group, explosions, sounds, player1_name, player2_name):
    # Solo las colisiones con jugadores vivos
    if player1.is_alive:
        for laser in player1.lasers:
            # Con aliens
            aliens_hit = pygame.sprite.spritecollide(laser, aliens, True)
            if aliens_hit:
                for alien in aliens_hit:
                    laser.kill()
                    player1.score += alien.value  # Sumar puntos dependiendo del tipo de alien
                    explosion = Explosion(alien.rect.centerx, alien.rect.centery, alien.color)
                    explosions.add(explosion)
                    sounds['invaderkilled'].play()

            # Con nave misteriosa
            if pygame.sprite.spritecollide(laser, extra_group, True):
                player1.score += 50  # Mystery ship suma 50 puntos
                laser.kill()
                sounds['mysterykilled'].play()

    if player2.is_alive:
        for laser in player2.lasers:
            # Con aliens
            aliens_hit = pygame.sprite.spritecollide(laser, aliens, True)
            if aliens_hit:
                for alien in aliens_hit:
                    laser.kill()
                    player2.score += alien.value  # Sumar puntos dependiendo del tipo de alien
                    explosion = Explosion(alien.rect.centerx, alien.rect.centery, alien.color)
                    explosions.add(explosion)
                    sounds['invaderkilled'].play()

            # Con nave misteriosa
            if pygame.sprite.spritecollide(laser, extra_group, True):
                player2.score += 50  # Mystery ship suma 50 puntos
                laser.kill()
                sounds['mysterykilled'].play()

    # --- Colisiones de láser enemigo --- (igual que antes para ambos jugadores)
    for laser in enemy_lasers:
        # Con barreras (las balas enemigas destruyen las barreras)
        if pygame.sprite.spritecollide(laser, blocks, True):
            laser.kill()

        # Con jugadores vivos
        if player1.is_alive and pygame.sprite.spritecollide(player1, enemy_lasers, True):
            laser.kill()
            player1.lives -= 1
            SOUNDS['shipexplosion'].play()
            if player1.lives <= 0:
                player1.die()  # Llamamos al método para hacer morir al jugador

        if player2.is_alive and pygame.sprite.spritecollide(player2, enemy_lasers, True):
            laser.kill()
            player2.lives -= 1
            SOUNDS['shipexplosion'].play()
            if player2.lives <= 0:
                player2.die()  # Llamamos al método para hacer morir al jugador

    # Verificar si ambos jugadores han perdido todas las vidas
    if player1.lives <= 0 and player2.lives <= 0:
        game_over_text = FONT.render("GAME OVER", True, RED)
        score_p1_text = FONT.render(f'{player1_name}: {player1.score}', True, WHITE)
        score_p2_text = FONT.render(f'{player2_name}: {player2.score}', True, WHITE)
        total_score = player1.score + player2.score
        score_total_text = FONT.render(f'Total: {total_score}', True, GREEN)
        multi_save_score(f"{player1_name} y {player2_name}", total_score)
        SCREEN.fill((0, 0, 0))
        SCREEN.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
        SCREEN.blit(score_p1_text, (SCREEN_WIDTH // 2 - score_p1_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
        SCREEN.blit(score_p2_text, (SCREEN_WIDTH // 2 - score_p2_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
        SCREEN.blit(score_total_text, (SCREEN_WIDTH // 2 - score_total_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        pygame.display.update()
        pygame.time.wait(5000)
        import main_menu
        main_menu.main()
        return



# --- Main game loop for Multiplayer ---
def main():
    player1_name = get_player_name(1)
    player2_name = get_player_name(2)
    controls_player1 = {'right': pygame.K_d, 'left': pygame.K_a, 'shoot': pygame.K_w}
    controls_player2 = {'right': pygame.K_RIGHT, 'left': pygame.K_LEFT, 'shoot': pygame.K_UP}

    player1 = Player((200, 580), SCREEN_WIDTH, 5, SCREEN_HEIGHT, controls_player1, 1)
    player2 = Player((600, 580), SCREEN_WIDTH, 5, SCREEN_HEIGHT, controls_player2, 2)

    player_group = pygame.sprite.Group(player1, player2)
    explosions = pygame.sprite.Group()

    current_level = 0
    aliens = create_aliens(LEVEL_PATTERNS[current_level])

    blocks = pygame.sprite.Group()
    for i in range(4):
        blocks_pattern = create_block_pattern(100 + i * 150, 450, 6, GREEN)
        blocks.add(*blocks_pattern)

    direction = 1
    extra_group = pygame.sprite.Group()
    extra_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(extra_timer, randint(4000, 8000))

    enemy_lasers = pygame.sprite.Group()
    enemy_shoot_timer = pygame.USEREVENT + 2
    pygame.time.set_timer(enemy_shoot_timer, 800)

    running = True
    while running:
        SCREEN.fill((0, 0, 0))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == extra_timer:
                side = choice(['left', 'right'])
                extra_group.add(Extra(side, SCREEN_WIDTH))
                SOUNDS['mysteryentered'].play()
            elif e.type == enemy_shoot_timer and aliens:
                alien_shoot(aliens, enemy_lasers, SCREEN_HEIGHT, SOUNDS['shoot2'])

        # Movimiento de los aliens
        aliens.update(direction)
        for alien in aliens:
            if alien.rect.right >= SCREEN_WIDTH or alien.rect.left <= 0:
                direction *= -1
                for a in aliens:
                    a.rect.y += 10
                break

        # Actualización de los grupos
        player_group.update()
        extra_group.update()
        enemy_lasers.update()

        # Manejo de las colisiones
        handle_collisions(player1, player2, aliens, enemy_lasers, blocks, extra_group, explosions, SOUNDS, player1_name, player2_name)


        # Verificar si pasamos de nivel
        if not aliens:
            current_level += 1
            if current_level >= len(LEVEL_PATTERNS):
                win_text = FONT.render("¡VICTORIA!", True, GREEN)
                score_p1_text = FONT.render(f'{player1_name}: {player1.score}', True, WHITE)
                score_p2_text = FONT.render(f'{player2_name}: {player2.score}', True, WHITE)
                total_score = player1.score + player2.score
                score_total_text = FONT.render(f'Total: {total_score}', True, GREEN)
                multi_save_score(f"{player1_name} y {player2_name}", total_score)
                SCREEN.fill((0, 0, 0))
                SCREEN.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
                SCREEN.blit(score_p1_text, (SCREEN_WIDTH // 2 - score_p1_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
                SCREEN.blit(score_p2_text, (SCREEN_WIDTH // 2 - score_p2_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
                SCREEN.blit(score_total_text, (SCREEN_WIDTH // 2 - score_total_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
                pygame.display.update()
                pygame.time.wait(5000)
                import main_menu
                main_menu.main()
                return

            else:
                aliens = create_aliens(LEVEL_PATTERNS[current_level])

        # Dibuja las entidades
        player_group.draw(SCREEN)
        extra_group.draw(SCREEN)
        enemy_lasers.draw(SCREEN)
        blocks.draw(SCREEN)
        aliens.draw(SCREEN)
        explosions.update()
        explosions.draw(SCREEN)
        player1.lasers.draw(SCREEN)
        player2.lasers.draw(SCREEN)

        # Mostrar vidas de cada jugador debajo del puntaje
        # Para el Jugador 1
        for i in range(player1.lives):
            SCREEN.blit(IMAGES['ship'], (40 + i * 40, 40))  # Las naves de vida del jugador 1 debajo del puntaj
        player1_text = FONT.render(f"{player1_name}: {player1.score}", True, WHITE)
        SCREEN.blit(player1_text, (10, 10))

        # Para el Jugador 2
        for i in range(player2.lives):
            SCREEN.blit(IMAGES['ship'], (SCREEN_WIDTH - (i + 1) * 40 - 40, 40))  # Las naves de vida del jugador 2 debajo del puntaje
        player2_text = FONT.render(f"{player2_name}: {player2.score}", True, WHITE)
        SCREEN.blit(player2_text, (SCREEN_WIDTH - player2_text.get_width() - 10, 10))

        # Mostrar el número del nivel
        level_text = FONT.render(f"Nivel: {current_level + 1}", True, WHITE)
        SCREEN.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 10))

        pygame.display.update()
        CLOCK.tick(60)

def run_game():
    main()

if __name__ == "__main__":
    main()
