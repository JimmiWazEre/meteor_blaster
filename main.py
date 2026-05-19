"""
=============================================================
METEOR BLAST
=============================================================
A space shooter built in Python using pygame-ce.
Player survives an endless meteor storm, shooting meteors
for bonus score while avoiding collisions. Difficulty
escalates through levels as meteor speed and spawn rate
increase.

-------------------------------------------------------------
CONTROLS
-------------------------------------------------------------
Arrow keys      Move ship
Space           Fire laser
R               Restart (game over screen)
ESC             Quit

-------------------------------------------------------------
PYGAME CONCEPTS COVERED
-------------------------------------------------------------
Game loop           setup, event loop, drawing
Surfaces            images, text rendering
Rects / Frects      hitboxes, positioning
Sprites & Groups    batch update, draw, collision
Movement            vectors, delta time, normalisation
Collisions          rect, mask, group vs group
Transformations     rotate, scale, rotozoom
Animations          frame-based explosion sequences
Particles           engine trail, fade over lifetime
Sound               sfx, looping music
OOP                 GameState, SplashScreen, GameOver classes
Colour              HSV cycling for dynamic background

-------------------------------------------------------------
REFERENCES
-------------------------------------------------------------
pygame-ce docs      https://pyga.me/docs/
"""

import pygame
from random import randint, uniform
from colorsys import hsv_to_rgb
from os.path import dirname, abspath, join
import json
BASE_DIR = dirname(abspath(__file__))

# -------------------------------------------------------------
# classes
# -------------------------------------------------------------

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

class MeteorParticle(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.Surface((4, 4), pygame.SRCALPHA)
        self.image.fill((220, 220, 220))
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = randint(150, 300)
        self.direction = pygame.Vector2(uniform(-1, 1), uniform(-1, 1)).normalize()
        self.speed = randint(400, 800)
        self.velocity = pygame.Vector2(uniform(-1, 1), uniform(-1, 1)).normalize() * self.speed

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
        self.entering_name = False
        self.scores = []
        self.pending_name = ""

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
        self.meteor_particles = pygame.sprite.Group()

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
        self.meteor_particles.empty()
        self.scores.clear()
        self.entering_name = False
        self.pending_name = ""
        for i in range(20):
            Star(self.star_sprites, star_surface, self.star_positions) # recreates stars fresh each reset
        self.player = Player(self.all_sprites) # recreates the player
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
        self.text_rect = self.text_surf.get_frect(center = (WINDOW_WIDTH / 2, 50))
        self.prompt_surf = font.render("Press R to play again", True, (240, 240, 240))
        self.prompt_rect = self.prompt_surf.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 150))

    def draw(self):
        window.blit(self.text_surf, self.text_rect)
        if not state.entering_name:
            window.blit(self.prompt_surf, self.prompt_rect)

    def input(self, event):
        if event.type == pygame.KEYDOWN and not state.player_alive:
            if state.entering_name:
                # name entry mode
                if event.key == pygame.K_BACKSPACE:
                    state.pending_name = state.pending_name[:-1]
                elif len(state.pending_name) < 3 and event.unicode.isalpha():
                    state.pending_name += event.unicode.upper()
                    for entry in state.scores:
                        if len(entry["name"]) < 3 or "_" in entry["name"]:
                            entry["name"] = state.pending_name.ljust(3, "_")
                            break
                    if len(state.pending_name) == 3:
                        save_scores(state.scores)
                        state.entering_name = False
            else:
                # normal game over mode
                if event.key == pygame.K_r:
                    state.reset()

# -------------------------------------------------------------
# functions
# -------------------------------------------------------------

def collisions():
    collision_sprites = pygame.sprite.spritecollide(state.player, state.meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        for i in collision_sprites:
            Explosion(explosion_frames, i.rect.center, state.all_sprites)
            explosion_sound.play()
            state.player.kill()
            state.engine_particles.empty()
            state.player_alive = False
            state.final_score = (pygame.time.get_ticks() - state.start_time) // 100 + state.score_bonus
            check_high_score(load_scores())
            for _ in range(50):
                MeteorParticle(i.rect.center, state.meteor_particles)

    for laser in state.laser_sprites:
        collision_sprites = pygame.sprite.spritecollide(laser, state.meteor_sprites, True)
        if collision_sprites:
            laser.kill()
            for i in collision_sprites:
                Explosion(explosion_frames, i.rect.center, state.all_sprites)
                explosion_sound.play()
                state.score_bonus += 20
            for _ in range(50):
                MeteorParticle(i.rect.center, state.meteor_particles)

    meteors = list(state.meteor_sprites)
    for i, meteor1 in enumerate(meteors):
        for meteor2 in meteors[i+1:]:
            if pygame.sprite.collide_mask(meteor1, meteor2):
                Explosion(explosion_frames, meteor1.rect.center, state.all_sprites)
                Explosion(explosion_frames, meteor2.rect.center, state.all_sprites)
                explosion_sound.play()
                meteor1.kill()
                meteor2.kill()
                for _ in range(50):
                        MeteorParticle(meteor1.rect.center, state.meteor_particles)
                        MeteorParticle(meteor2.rect.center, state.meteor_particles)
def display_score():
    text_surf = font.render(str(state.current_time), True, (240, 240, 240))
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
    window.blit(text_surf, text_rect)
    pygame.draw.rect(window, (240, 240, 240), text_rect.inflate(20, 30).move(0, -2), 5, 10)

def update_level():
    state.current_level = int((state.current_time / 500) ** 0.7) + 1 # exponential curve: early levels come quickly, later levels take progressively longer to reach
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
    # only fires when the star timer event triggers and the player is still alive
    # stars stop spawning on game over to preserve the freeze frame effect
    if event.type == star_event and state.player_alive:

        # build a list of the x positions of all currently live stars
        # used to prevent new stars spawning too close to existing ones horizontally
        existing_x = [s.rect.centerx for s in state.star_sprites if isinstance(s, Star)]

        # pick a random x position within the screen bounds
        x = randint(50, WINDOW_WIDTH - 50)
        attempts = 0

        # keep trying new x positions until one is found that is at least 100px
        # from every existing star, or until 30 attempts have been made
        # the attempt cap prevents an infinite loop if the screen is too crowded
        while any(abs(x - ex) < 100 for ex in existing_x) and attempts < 30:
            x = randint(50, WINDOW_WIDTH - 50)
            attempts += 1

        # spawn the star above the screen at the validated x position
        # scrolling=True skips the padding check and places it off the top of the screen
        Star(state.star_sprites, star_surface, state.star_positions, scrolling=True, spawn_x=x)

def meteor_spawn(event):
    if event.type == meteor_event and state.player_alive:
        x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
        Meteor(meteor_surf, (x, y), state.all_sprites, state.meteor_sprites)

def draw_background():
    # calculate a hue value that slowly cycles from 0.0 to 1.0 over 50 seconds
    # % 1.0 wraps it back to 0.0 once it reaches 1.0, creating a continuous loop
    hue = (pygame.time.get_ticks() / 50000) % 1.0

    # convert the hue to RGB using HSV colour model:
    # hue = the colour (0.0-1.0 cycles through the full colour wheel)
    # 0.6 = saturation (how vivid the colour is — 1.0 is fully vivid, 0.0 is grey)
    # 0.15 = value/brightness (kept low to maintain a dark background)
    # hsv_to_rgb returns three floats between 0.0 and 1.0
    r, g, b = hsv_to_rgb(hue, 0.6, 0.15)

    # pygame expects RGB values as integers between 0-255
    # multiply each float by 255 and convert to int before passing to fill
    window.fill((int(r * 255), int(g * 255), int(b * 255)))

def draw_game_over():
    state.current_time = state.final_score
    if not state.scores:
        state.scores = load_scores()
    draw_background()
    state.star_sprites.draw(window)
    state.all_sprites.draw(window)
    display_score()
    game_over_screen.draw()
    display_leaderboard()

def draw_game(dt):
    state.current_time = (pygame.time.get_ticks() - state.start_time) // 100 + state.score_bonus
    draw_background()
    state.star_sprites.update(dt)
    state.all_sprites.update(dt)
    state.engine_particles.update(dt)
    state.meteor_particles.update(dt)
    collisions()
    update_level()
    state.star_sprites.draw(window)
    state.all_sprites.draw(window)
    state.engine_particles.draw(window)
    state.meteor_particles.draw(window)
    display_score()

def load_scores():
    try:
        with open(SCORES_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except:
        return []

def save_scores(scores):
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f)

def check_high_score(scores):
    if len(scores) < 10 or state.final_score > scores[-1]["score"]:
        scores.append({"name": "___", "score": state.final_score})
        scores = sorted(scores, key=lambda x: x["score"], reverse=True)
        scores = scores[:10] 
        save_scores(scores)
        state.entering_name = True
        state.scores = scores

def display_leaderboard():
    show_cursor = (pygame.time.get_ticks() // 500) % 2 == 0
    for i, entry in enumerate(state.scores):
        name = entry["name"]
        if state.entering_name and "_" in name:
            if show_cursor:
                name = name  # show the underscores
            else:
                name = name.replace("_", " ")  # hide them
        text = f"{i+1:02}  {name}  {entry['score']}"
        text_surf = score_font.render(text, True, (240, 240, 240))
        text_rect = text_surf.get_frect(center=(WINDOW_WIDTH / 2, 120 + i * 30))
        window.blit(text_surf, text_rect)
        if state.entering_name:
            prompt_surf = font.render("ENTER YOUR CALLSIGN", True, (240, 240, 240))
            prompt_rect = prompt_surf.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 150))
            window.blit(prompt_surf, prompt_rect)

# -------------------------------------------------------------
# initial setup
# -------------------------------------------------------------
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

# -------------------------------------------------------------
# import assets
# -------------------------------------------------------------

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

# scores
SCORES_FILE = join(BASE_DIR, "scores.json")

# -------------------------------------------------------------
# instantialise pre-loop classes
# -------------------------------------------------------------
splash = SplashScreen()
game_over_screen = GameOver()

# -------------------------------------------------------------
# game loop
# -------------------------------------------------------------

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