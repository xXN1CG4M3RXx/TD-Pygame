
import pygame
import random

# --- Konstanten ---
WIDTH, HEIGHT = 1200, 800  # Fenstergröße
MAP_WIDTH, MAP_HEIGHT = 3000, 2000  # Große Map
PLAYER_SIZE = 40
ENEMY_SIZE = 40
PLAYER_SPEED = 6
ENEMY_SPEED = 2
BULLET_SPEED = 12
FPS = 60
NUM_ENEMIES = 15
NUM_OBSTACLES = 120

# --- Initialisierung ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# --- Klassen ---
class Player(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
		self.image.fill((0, 200, 255))
		self.rect = self.image.get_rect(center=(x, y))
		self.pos = pygame.Vector2(x, y)
		self.vel = pygame.Vector2(0, 0)

	def update(self, keys):
		self.vel = pygame.Vector2(0, 0)
		if keys[pygame.K_w]: self.vel.y = -PLAYER_SPEED
		if keys[pygame.K_s]: self.vel.y = PLAYER_SPEED
		if keys[pygame.K_a]: self.vel.x = -PLAYER_SPEED
		if keys[pygame.K_d]: self.vel.x = PLAYER_SPEED
		self.pos += self.vel
		self.pos.x = max(0, min(MAP_WIDTH, self.pos.x))
		self.pos.y = max(0, min(MAP_HEIGHT, self.pos.y))
		self.rect.center = self.pos

class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
		self.image.fill((200, 50, 50))
		self.rect = self.image.get_rect(center=(x, y))
		self.pos = pygame.Vector2(x, y)

	def update(self, player_pos):
		direction = (player_pos - self.pos).normalize() if player_pos != self.pos else pygame.Vector2(0, 0)
		self.pos += direction * ENEMY_SPEED
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
		self.image = pygame.Surface((w, h))
		self.image.fill(color)
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

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			mx, my = pygame.mouse.get_pos()
			cam_offset = get_camera_offset(player)
			target = pygame.Vector2(mx + cam_offset.x, my + cam_offset.y)
			direction = (target - player.pos).normalize()
			bullets.add(Bullet(player.pos.x, player.pos.y, direction))

	# Gegner-Spawning nach 3 Sekunden, dann alle SPAWN_INTERVAL Sekunden
	if seconds_since_start > SPAWN_DELAY:
		if now - last_spawn_time > SPAWN_INTERVAL * 1000:
			ex = random.randint(0, MAP_WIDTH)
			ey = random.randint(0, MAP_HEIGHT)
			enemies.add(Enemy(ex, ey))
			last_spawn_time = now

	keys = pygame.key.get_pressed()
	player.update(keys)
	enemies.update(player.pos)
	bullets.update()

	# Kollisionen
	for bullet in pygame.sprite.groupcollide(bullets, enemies, True, True):
		pass
	if pygame.sprite.spritecollideany(player, enemies):
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

	# Minimap
	minimap = pygame.Surface((200, 133))
	minimap.fill((50,50,50))
	px = int(player.pos.x / MAP_WIDTH * 200)
	py = int(player.pos.y / MAP_HEIGHT * 133)
	pygame.draw.circle(minimap, (0,200,255), (px, py), 5)
	screen.blit(minimap, (WIDTH-210, 10))

	pygame.display.flip()

pygame.quit()