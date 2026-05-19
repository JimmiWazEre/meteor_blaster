"""
pygame docs = https://pyga.me/docs/

### Space Shooter ###

Skills Developed:
    Standard Game Components: setup, event loop, drawing the game
    Surfaces (images, text)
    Frects & Rects (hit boxes around surfaces or maybe just around nothing)
    Sprites (combining surfaces and frects, apllying these to groups for mass calling)
    Basic Movement (get_pressed, pygame.K_[something], vectors, delta time, framerate)
    Collisions
    Masks (make more precise collisions)
    Transforming Surfaces (rotate, flip, blur etc etc)
    Animations (explosions)
    Sound
"""

import pygame
from random import randint, uniform
from colorsys import hsv_to_rgb
from os.path import dirname, abspath, join
BASE_DIR = dirname(abspath(__file__))

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.transform.scale_by(pygame.image.load(join(BASE_DIR, "images", "player.png")).convert_alpha(), 3.5)
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.math.Vector2()
        self.speed = 350

        # cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 300

        # mask
        self.mask = pygame.mask.from_surface(self.image)
    
    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt
        self.rect.clamp_ip(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, state.all_sprites, state.laser_sprites)
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
        
        self.laser_timer()
        x, y = self.rect.midbottom
        for _ in range(8):
            EngineParticle((x, y - 10), state.engine_particles)

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, star_surface, star_positions, scrolling=False, spawn_x=None):
        super().__init__(groups)
        self.image = pygame.transform.scale_by(star_surface, uniform(0.2, 1.0))
        self.speed = 50
        self.start_time = pygame.time.get_ticks()
        self.lifetime = int((WINDOW_HEIGHT / self.speed) * 2000)
        self.direction = pygame.Vector2(0, 1)
        if scrolling:
            self.rect = self.image.get_frect(center=(spawn_x, randint(-200, -50)))
        else:
            while True:
                star_vect = (randint(50, WINDOW_WIDTH-50), randint(50, WINDOW_HEIGHT-50))
                if all(pygame.math.Vector2(star_vect).distance_to(pos) > 100 for pos in star_positions):
                    star_positions.append(star_vect)
                    self.rect = self.image.get_frect(center=star_vect)
                    break
    
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()

class Laser(pygame.sprite.Sprite):
    def __init__(self, laser_surface, pos, *groups):
        super().__init__(groups)
        self.image = laser_surface
        self.rect = self.image.get_frect(midbottom = pos)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.rect.centery -= 1000 * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, meteor_surface, pos, *groups):
        super().__init__(groups)

        self.og_image = pygame.transform.scale_by(meteor_surface, uniform(0.5, 2))
        self.image = self.og_image
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(200, 400) + (state.current_level * 20)
        self.mask = pygame.mask.from_surface(self.image)
        self.rotation = 0
        self.rotation_speed = randint(50, 100)

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.og_image, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 250

    def update(self, dt):
        self.frame_index += 100 * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        self.image = pygame.transform.scale_by(self.image, 2)
        self.rect = self.image.get_frect(center = self.rect.center)
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()

class EngineParticle(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.Surface((4, 4), pygame.SRCALPHA)
        self.image.fill((255, randint(50, 150), 0))
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = randint(150, 300)
        self.direction = pygame.Vector2(uniform(-1, 1), 2)
        self.speed = randint(100, 400)
        self.velocity = pygame.Vector2(uniform(-0.5, 0.5), 5) * self.speed

    def update(self, dt):
        self.rect.center += self.velocity * dt
        remaining = 1 - (pygame.time.get_ticks() - self.start_time) / self.lifetime
        self.image.set_alpha(int(255 * remaining))
        if remaining <= 0:
            self.kill()

class GameState():
    def __init__(self):
        # state flags
        self.player_alive = True
        self.app_running = True
        self.splash_complete = False
        # scoring
        self.final_score = 0
        self.score_bonus = 0
        self.current_time = 0
        # time
        self.start_time = 0
        # level
        self.current_level = 1
        self.previous_level = 0
        self.level_up_time = 0
        # groups
        self.all_sprites = pygame.sprite.Group()
        self.meteor_sprites = pygame.sprite.Group()
        self.laser_sprites = pygame.sprite.Group()
        self.star_sprites = pygame.sprite.Group()
        self.engine_particles = pygame.sprite.Group()
        # star setup
        self.star_interval = int((WINDOW_HEIGHT / 100) / 20 * 1000)
        self.star_positions = []
        # player
        self.player = None

    def reset(self):
        self.all_sprites.empty()
        self.meteor_sprites.empty()
        self.laser_sprites.empty()
        self.star_sprites.empty()
        self.star_positions.clear()
        self.engine_particles.empty()

        for i in range(20):
            Star(self.star_sprites, star_surface, self.star_positions) # recreates stars fresh each reset

        self.player = Player(self.all_sprites) # NEW: recreates the player

        self.player_alive = True
        self.final_score = 0 
        self.start_time = pygame.time.get_ticks()
        self.previous_level = 0
        self.level_up_time = 0
        self.current_level = 1
        self.score_bonus = 0
        pygame.time.set_timer(meteor_event, 500)

class SplashScreen():
    def __init__(self):
        self.scaled = pygame.transform.scale(splash_surf, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
    def draw(self):
        window.blit(self.scaled, (0, 0))

    def input(self, event):
        if event.type == pygame.KEYDOWN and not state.splash_complete:
            state.splash_complete = True
            state.reset()

class GameOver():
    def __init__(self):
        self.text_surf = font.render("GAME OVER", True, (240, 240, 240))
        self.text_rect = self.text_surf.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.prompt_surf = font.render("Press R to play again", True, (240, 240, 240))
        self.prompt_rect = self.prompt_surf.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 60))

    def draw(self):
        window.blit(self.text_surf, self.text_rect)
        window.blit(self.prompt_surf, self.prompt_rect)

    def input(self, event):
        if event.type == pygame.KEYDOWN and not state.player_alive:
            if event.key == pygame.K_r:
                state.reset()

def collisions():

    collision_sprites = pygame.sprite.spritecollide(state.player, state.meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        for i in collision_sprites:
            Explosion(explosion_frames, i.rect.center, state.all_sprites)
            explosion_sound.play()
            state.player.kill()
            state.engine_particles.empty()
            state.player_alive = False
            state.final_score = (pygame.time.get_ticks() - state.start_time) // 100 + state.score_bonus # core relative to run start, not program start

    for laser in state.laser_sprites:
        collision_sprites = pygame.sprite.spritecollide(laser, state.meteor_sprites, True)
        if collision_sprites:
            laser.kill()
            for i in collision_sprites:
                Explosion(explosion_frames, i.rect.center, state.all_sprites)
                explosion_sound.play()
                state.score_bonus += 20

    meteors = list(state.meteor_sprites)
    for i, meteor1 in enumerate(meteors):
        for meteor2 in meteors[i+1:]:
            if pygame.sprite.collide_mask(meteor1, meteor2):
                Explosion(explosion_frames, meteor1.rect.center, state.all_sprites)
                Explosion(explosion_frames, meteor2.rect.center, state.all_sprites)
                explosion_sound.play()
                meteor1.kill()
                meteor2.kill()

def display_score():
    text_surf = font.render(str(state.current_time), True, (240, 240, 240))
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
    window.blit(text_surf, text_rect)
    pygame.draw.rect(window, (240, 240, 240), text_rect.inflate(20, 30).move(0, -2), 5, 10)

def update_level():
    state.current_level = (state.current_time // 200) + 1
    if state.current_level != state.previous_level:
        state.previous_level = state.current_level
        state.level_up_time = pygame.time.get_ticks()
        pygame.time.set_timer(meteor_event, max(500 - (state.current_level * 50), 100))

    if pygame.time.get_ticks() - state.level_up_time < 2000:
        text_surf = font.render(f"Level {state.current_level}", True, (240, 240, 240))
        text_rect = text_surf.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 100))
        window.blit(text_surf, text_rect)

def quit(event):
    esc = pygame.key.get_pressed()
    if event.type == pygame.QUIT or esc[pygame.K_ESCAPE]:
        state.app_running = False

def star_spawn(event):
    if event.type == star_event and state.player_alive:
        existing_x = [s.rect.centerx for s in state.star_sprites if isinstance(s, Star)]
        x = randint(50, WINDOW_WIDTH - 50)
        attempts = 0
        while any(abs(x - ex) < 100 for ex in existing_x) and attempts < 30:
            x = randint(50, WINDOW_WIDTH - 50)
            attempts += 1
        Star(state.star_sprites, star_surface, state.star_positions, scrolling=True, spawn_x=x)

def meteor_spawn(event):
    if event.type == meteor_event and state.player_alive:
        x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
        Meteor(meteor_surf, (x, y), state.all_sprites, state.meteor_sprites)

def draw_background():
    hue = (pygame.time.get_ticks() / 50000) % 1.0
    r, g, b = hsv_to_rgb(hue, 0.6, 0.15)
    window.fill((int(r * 255), int(g * 255), int(b * 255)))

def draw_game_over():
    state.current_time = state.final_score
    draw_background()
    state.star_sprites.draw(window)
    state.all_sprites.draw(window)
    display_score()
    game_over_screen.draw()

def draw_game(dt):
    state.current_time = (pygame.time.get_ticks() - state.start_time) // 100 + state.score_bonus
    draw_background()
    state.star_sprites.update(dt)
    state.all_sprites.update(dt)
    state.engine_particles.update(dt)
    collisions()
    update_level()
    state.star_sprites.draw(window)
    state.all_sprites.draw(window)
    state.engine_particles.draw(window)
    display_score()

### initial setup
pygame.init()
# window
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), vsync=1)
pygame.display.set_caption("Meteor Blast")
# game running
state = GameState()
clock = pygame.time.Clock()
# meteor spawns
meteor_event = pygame.event.custom_type()
# star spawns
star_event = pygame.event.custom_type()
pygame.time.set_timer(star_event, state.star_interval)

### import
# images
splash_surf = pygame.image.load(join(BASE_DIR, "images", "splash.png")).convert()
star_surface = pygame.transform.scale_by(pygame.image.load(join(BASE_DIR, "images", "star.png")).convert_alpha(), 2)
meteor_surf = pygame.transform.scale_by(pygame.image.load(join(BASE_DIR, "images", "meteor.png")).convert_alpha(), 3)
laser_surf = pygame.transform.scale_by(pygame.image.load(join(BASE_DIR, "images", "laser.png")).convert_alpha(), 2)
explosion_frames = [pygame.image.load(join(BASE_DIR, "images", "explosion", f"{i}.png")).convert_alpha() for i in range(17)]
font = pygame.font.Font(join(BASE_DIR, "images", "PressStart2P-Regular.ttf"), 40)
score_font = pygame.font.Font(join(BASE_DIR, "images", "PressStart2P-Regular.ttf"), 20)
# sound
laser_sound = pygame.mixer.Sound(join(BASE_DIR, "audio", "laser.wav"))
laser_sound.set_volume(0.1)
explosion_sound = pygame.mixer.Sound(join(BASE_DIR, "audio", "explosion.wav"))
explosion_sound.set_volume(0.1)
damage_sound = pygame.mixer.Sound(join(BASE_DIR, "audio", "damage.ogg"))
damage_sound.set_volume(0.1)
game_music = pygame.mixer.Sound(join(BASE_DIR, "audio", "game_music.wav"))
game_music.set_volume(0.1)
game_music.play(loops=-1)

# instantialise
splash = SplashScreen()
game_over_screen = GameOver()

while state.app_running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        quit(event)
        star_spawn(event)
        meteor_spawn(event)
        splash.input(event)
        game_over_screen.input(event)

    if not state.splash_complete:
        splash.draw()
    elif not state.player_alive:
        draw_game_over()
    else:
        draw_game(dt)

    pygame.display.update()