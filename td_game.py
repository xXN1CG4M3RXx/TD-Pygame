import pygame
import random

# --- Konstanten ---
WIDTH, HEIGHT = 1920, 1200  # Fenstergröße
MAP_WIDTH, MAP_HEIGHT = 3000, 2000  # Große Map
PLAYER_SIZE = 40
ENEMY_SIZE = 40
PLAYER_SPEED = 3
ENEMY_SPEED = 2
BULLET_SPEED = 12
FPS = 60
NUM_OBSTACLES = 120


# --- Initialisierung ---
pygame.init()
FONT = pygame.font.SysFont('Arial', 32)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# --- Klassen ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        self.image.fill((0, 200, 255))
        pygame.draw.rect(self.image, (255,255,255), self.image.get_rect(), 3)  # Weißer Rand
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)

    def update(self, keys):
        self.vel = pygame.Vector2(0, 0)
        if keys[pygame.K_w]: self.vel.y = -PLAYER_SPEED
        if keys[pygame.K_s]: self.vel.y = PLAYER_SPEED
        if keys[pygame.K_a]: self.vel.x = -PLAYER_SPEED
        if keys[pygame.K_d]: self.vel.x = PLAYER_SPEED
        if keys[pygame.K_ESCAPE]: pygame.quit(); exit()
        self.pos += self.vel
        self.pos.x = max(0, min(MAP_WIDTH, self.pos.x))
        self.pos.y = max(0, min(MAP_HEIGHT, self.pos.y))
        self.rect.center = self.pos

class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y, fast=False):
		super().__init__()
		self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE), pygame.SRCALPHA)
		if fast:
			self.image.fill((255, 140, 0))  # Orange für schnellen Gegner
			pygame.draw.rect(self.image, (0,0,0), self.image.get_rect(), 3)
			self.speed = ENEMY_SPEED * 1.4
		else:
			self.image.fill((200, 50, 50))
			pygame.draw.rect(self.image, (0,0,0), self.image.get_rect(), 3)
			self.speed = ENEMY_SPEED
		self.rect = self.image.get_rect(center=(x, y))
		self.pos = pygame.Vector2(x, y)

	def update(self, player_pos):
		direction = (player_pos - self.pos).normalize() if player_pos != self.pos else pygame.Vector2(0, 0)
		self.pos += direction * self.speed
		self.rect.center = self.pos

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, dir):
		super().__init__()
		self.image = pygame.Surface((10, 10))
		self.image.fill((255, 255, 0))
		self.rect = self.image.get_rect(center=(x, y))
		self.pos = pygame.Vector2(x, y)
		self.dir = dir

	def update(self):
		self.pos += self.dir * BULLET_SPEED
		self.rect.center = self.pos
		if not (0 <= self.pos.x <= MAP_WIDTH and 0 <= self.pos.y <= MAP_HEIGHT):
			self.kill()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.image.fill(color)
        # Muster für bessere Unterscheidung
        if color == (34,139,34):  # Baum
            pygame.draw.circle(self.image, (0,100,0), (w//2, h//2), min(w,h)//3)
        elif color == (139,69,19):  # Stein
            pygame.draw.ellipse(self.image, (160,82,45), [w//4, h//4, w//2, h//2])
        elif color == (128,128,128):  # Busch
            for i in range(3):
                pygame.draw.circle(self.image, (0,255,0), (random.randint(0,w), random.randint(0,h)), min(w,h)//5, 1)
        self.rect = self.image.get_rect(center=(x, y))

# --- Map generieren ---
obstacles = pygame.sprite.Group()
for _ in range(NUM_OBSTACLES):
	x = random.randint(50, MAP_WIDTH-50)
	y = random.randint(50, MAP_HEIGHT-50)
	w = random.randint(30, 80)
	h = random.randint(30, 80)
	color = random.choice([(34,139,34), (139,69,19), (128,128,128)])  # Baum, Stein, Busch
	obstacles.add(Obstacle(x, y, w, h, color))


# --- Sprites ---
player = Player(MAP_WIDTH//2, MAP_HEIGHT//2)
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# --- Highscore, Level, Leben ---
score = 0
level = 1
level_time = [20, 30, 40, 50, 60]  # Sekunden pro Level
level_start_ticks = pygame.time.get_ticks()
level_show_ticks = pygame.time.get_ticks()
show_level = True
show_level_duration = 2000  # ms
lives = 3


# --- Gegner-Spawning ---
SPAWN_DELAY = 3  # Sekunden bis zum ersten Spawn
SPAWN_INTERVAL = 1.2  # Sekunden zwischen Spawns
last_spawn_time = 0
game_start_time = pygame.time.get_ticks()

# --- Kamera ---
def get_camera_offset(player):
	offset_x = player.pos.x - WIDTH//2
	offset_y = player.pos.y - HEIGHT//2
	offset_x = max(0, min(MAP_WIDTH-WIDTH, offset_x))
	offset_y = max(0, min(MAP_HEIGHT-HEIGHT, offset_y))
	return pygame.Vector2(offset_x, offset_y)

# --- Hauptloop ---
running = True
while running:
	clock.tick(FPS)
	now = pygame.time.get_ticks()
	seconds_since_start = (now - game_start_time) / 1000
	seconds_in_level = (now - level_start_ticks) / 1000

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			mx, my = pygame.mouse.get_pos()
			cam_offset = get_camera_offset(player)
			target = pygame.Vector2(mx + cam_offset.x, my + cam_offset.y)
			direction = (target - player.pos).normalize()
			bullets.add(Bullet(player.pos.x, player.pos.y, direction))

	# Levelwechsel
	if seconds_in_level > level_time[min(level-1, len(level_time)-1)]:
		level += 1
		level_start_ticks = now
		show_level = True
		level_show_ticks = now
		enemies.empty()

	# Levelanzeige
	if show_level and now - level_show_ticks < show_level_duration:
		pass
	else:
		show_level = False

	# Gegner-Spawning nach 3 Sekunden, dann alle SPAWN_INTERVAL Sekunden
	if seconds_since_start > SPAWN_DELAY:
		if now - last_spawn_time > SPAWN_INTERVAL * 1000:
			ex = random.randint(0, MAP_WIDTH)
			ey = random.randint(0, MAP_HEIGHT)
			fast = level >= 3 and random.random() < 0.3  # Ab Level 3, 30% schnell
			enemies.add(Enemy(ex, ey, fast=fast))
			last_spawn_time = now

	keys = pygame.key.get_pressed()
	player.update(keys)
	enemies.update(player.pos)
	bullets.update()

	# Kollisionen
	for bullet, hit_enemies in pygame.sprite.groupcollide(bullets, enemies, True, True).items():
		for hit_enemy in hit_enemies:
			if getattr(hit_enemy, 'speed', ENEMY_SPEED) > ENEMY_SPEED:
				score += 2
			else:
				score += 1
	hit_enemy = pygame.sprite.spritecollideany(player, enemies)
	if hit_enemy:
		lives -= 1
		hit_enemy.kill()
		if lives <= 0:
			running = False  # Game Over

	# Kamera Offset
	cam_offset = get_camera_offset(player)

	# --- Zeichnen ---
	screen.fill((30, 30, 30))
	for obs in obstacles:
		screen.blit(obs.image, obs.rect.move(-cam_offset.x, -cam_offset.y))
	for enemy in enemies:
		screen.blit(enemy.image, enemy.rect.move(-cam_offset.x, -cam_offset.y))
	for bullet in bullets:
		screen.blit(bullet.image, bullet.rect.move(-cam_offset.x, -cam_offset.y))
	screen.blit(player.image, player.rect.move(-cam_offset.x, -cam_offset.y))

	# HUD: Highscore, Level, Leben
	score_text = FONT.render(f"Score: {score}", True, (255,255,0))
	screen.blit(score_text, (20, 20))
	level_text = FONT.render(f"Level: {level}", True, (0,255,255))
	screen.blit(level_text, (20, 60))
	lives_text = FONT.render(f"Leben: {lives}", True, (255,0,0))
	screen.blit(lives_text, (20, 100))

	# Levelanzeige (groß, mittig)
	if show_level and now - level_show_ticks < show_level_duration:
		overlay = FONT.render(f"Level {level} startet!", True, (255,255,255))
		rect = overlay.get_rect(center=(WIDTH//2, HEIGHT//2))
		screen.blit(overlay, rect)

	# Minimap
	minimap = pygame.Surface((200, 133))
	minimap.fill((50,50,50))
	px = int(player.pos.x / MAP_WIDTH * 200)
	py = int(player.pos.y / MAP_HEIGHT * 133)
	pygame.draw.circle(minimap, (0,200,255), (px, py), 5)
	screen.blit(minimap, (WIDTH-210, 10))

	pygame.display.flip()

pygame.quit()