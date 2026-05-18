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
from os.path import join
from random import randint, uniform

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.transform.scale_by(pygame.image.load(join("images", "player.png")).convert_alpha(), 3)
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
            Laser(laser_surf, self.rect.midtop, all_sprites, laser_sprites)
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
        
        self.laser_timer()

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
        global current_level
        self.og_image = pygame.transform.scale_by(meteor_surface, uniform(0.5, 1.5))
        self.image = meteor_surface
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(200, 400) + (current_level * 20)
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
        self.rect = self.image.get_frect(center = self.rect.center)
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()

def reset(): # wraps all game state setup so it can be called at start and on restart
    global game_active, final_score, player, start_time, previous_level, level_up_time, current_level, meteor_event, score_bonus # NEW: declares the variables we need to modify at the outer scope

    all_sprites.empty()    # clears all sprites from the group
    meteor_sprites.empty() # clears all meteors
    laser_sprites.empty()  # clears all lasers
    star_sprites.empty()
    star_positions.clear() # empties the list in place (not reassigned) so Star.__init__ can repopulate it

    for i in range(20):
        Star(star_sprites, star_surface, star_positions) # recreates stars fresh each reset

    player = Player(all_sprites) # NEW: recreates the player

    game_active = True  # ensures the game runs after reset
    final_score = 0     # clears the frozen score from the previous run
    start_time = pygame.time.get_ticks() # records the time at the start of each run so score is relative, not absolute
    previous_level = 0
    level_up_time = 0
    current_level = 1
    score_bonus = 0
    pygame.time.set_timer(meteor_event, 500)

def collisions():
    global game_active
    global final_score
    global score_bonus
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        for i in collision_sprites:
            Explosion(explosion_frames, i.rect.center, all_sprites)
            explosion_sound.play()
            player.kill()
            game_active = False
            final_score = (pygame.time.get_ticks() - start_time) // 100 + score_bonus # core relative to run start, not program start

    for laser in laser_sprites:
        collision_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collision_sprites:
            laser.kill()
            for i in collision_sprites:
                Explosion(explosion_frames, i.rect.center, all_sprites)
                explosion_sound.play()
                score_bonus += 20
                


    meteors = list(meteor_sprites)
    for i, meteor1 in enumerate(meteors):
        for meteor2 in meteors[i+1:]:
            if pygame.sprite.collide_mask(meteor1, meteor2):
                Explosion(explosion_frames, meteor1.rect.center, all_sprites)
                Explosion(explosion_frames, meteor2.rect.center, all_sprites)
                explosion_sound.play()
                meteor1.kill()
                meteor2.kill()

def display_score():
    global current_time
    text_surf = font.render(str(current_time), True, (240, 240, 240))
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
    window.blit(text_surf, text_rect)
    pygame.draw.rect(window, (240, 240, 240), text_rect.inflate(20, 10).move(0, -7), 5, 10)

def game_over():
    text_surf = font.render("GAME OVER", True, (240, 240, 240))
    text_rect = text_surf.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
    window.blit(text_surf, text_rect)
    prompt_surf = font.render("Press R to play again", True, (240, 240, 240)) # NEW: restart prompt
    prompt_rect = prompt_surf.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 60))
    window.blit(prompt_surf, prompt_rect) # NEW: draws the prompt below the game over message

def update_level():
    global previous_level, level_up_time, current_level
    current_level = (current_time // 200) + 1
    if current_level != previous_level:
        previous_level = current_level
        level_up_time = pygame.time.get_ticks()
        pygame.time.set_timer(meteor_event, max(500 - (current_level * 50), 100))

    if pygame.time.get_ticks() - level_up_time < 2000:
        text_surf = font.render(f"Level {current_level}", True, (240, 240, 240))
        text_rect = text_surf.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 100))
        window.blit(text_surf, text_rect)

# general setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), vsync=1)
pygame.display.set_caption("Meteor Blast")
running = True
clock = pygame.time.Clock()
star_positions = []
game_active = True
final_score = 0
score_bonus = 0
start_time = 0 # declared here, set properly by reset() each run
player = None # declared here so it exists in the outer scope before reset() assigns it
previous_level = 0
level_up_time = 0
current_level = 1
meteor_event = pygame.event.custom_type()
STAR_SPEED = 100 # NEW
star_interval = int((WINDOW_HEIGHT / STAR_SPEED) / 20 * 1000) # NEW
star_event = pygame.event.custom_type() # NEW
pygame.time.set_timer(star_event, star_interval) # NEW

# import
star_surface = pygame.transform.scale_by(pygame.image.load(join("images", "star.png")).convert_alpha(), 2)
meteor_surf = pygame.transform.scale_by(pygame.image.load(join("images", "meteor.png")).convert_alpha(), 3)
laser_surf = pygame.transform.scale_by(pygame.image.load(join("images", "laser.png")).convert_alpha(), 2)
explosion_frames = [pygame.image.load(join("images", "explosion", f"{i}.png")).convert_alpha() for i in range(17)]
font = pygame.font.Font(join("images", "Oxanium-Bold.ttf"), 40)

laser_sound = pygame.mixer.Sound(join("audio", "laser.wav"))
laser_sound.set_volume(0.1)
explosion_sound = pygame.mixer.Sound(join("audio", "explosion.wav"))
explosion_sound.set_volume(0.1)
damage_sound = pygame.mixer.Sound(join("audio", "damage.ogg"))
damage_sound.set_volume(0.1)
game_music = pygame.mixer.Sound(join("audio", "game_music.wav"))
game_music.set_volume(0.1)
game_music.play(loops = -1)

# sprite groups — created once, emptied and repopulated by reset()
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
star_sprites = pygame.sprite.Group()

reset() # replaces the inline sprite setup block — does the same thing but is now reusable

while running:
    dt = clock.tick(60) / 1000
    
    for event in pygame.event.get():
        esc = pygame.key.get_pressed()
        if event.type == pygame.QUIT or esc[pygame.K_ESCAPE]:
            running = False
        if event.type == star_event and game_active:
            existing_x = [s.rect.centerx for s in star_sprites if isinstance(s, Star)]
            x = randint(50, WINDOW_WIDTH - 50)
            attempts = 0
            while any(abs(x - ex) < 100 for ex in existing_x) and attempts < 30:
                x = randint(50, WINDOW_WIDTH - 50)
                attempts += 1
            Star(star_sprites, star_surface, star_positions, scrolling=True, spawn_x=x)
        if event.type == meteor_event and game_active: # stops spawning meteors after game over
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            Meteor(meteor_surf, (x, y), all_sprites, meteor_sprites)
        if event.type == pygame.KEYDOWN and not game_active: # listens for R key on game over screen
            if event.key == pygame.K_r:
                reset() # calls reset to restart the game

    window.fill('#3a2e3f')
    star_sprites.draw(window)
    all_sprites.draw(window)

    if game_active:
        current_time = (pygame.time.get_ticks() - start_time) // 100 + score_bonus
    else:
        current_time = final_score

    display_score()

    if not game_active:
        game_over()
    else:
        star_sprites.update(dt)
        all_sprites.update(dt)
        collisions()
        update_level()

    pygame.display.update()