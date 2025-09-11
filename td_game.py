
import pygame
import random
import math

# --- Konstanten ---
WIDTH, HEIGHT = 1280, 1024  # Fenstergröße
MAP_WIDTH, MAP_HEIGHT = 3000, 2000  # Große Map
NUM_OBSTACLES = 30
MAP_WIDTH, MAP_HEIGHT = 3000, 2000  # Große Map
NUM_OBSTACLES = 30

# --- Pygame Initialisierung ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Shooter")
clock = pygame.time.Clock()
try:
	FONT = pygame.font.SysFont("Arial", 36)
except:
	FONT = pygame.font.Font(None, 36)

PLAYER_SIZE = 40
PLAYER_SPEED = 4
ENEMY_SIZE = 40
ENEMY_SPEED = 4
BULLET_SPEED = 12
FPS = 60

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
		if keys[pygame.K_ESCAPE]:
			pygame.quit()
			exit()
		if keys[pygame.K_w]:
			self.vel.y = -PLAYER_SPEED
		if keys[pygame.K_s]:
			self.vel.y = PLAYER_SPEED
		if keys[pygame.K_a]:
			self.vel.x = -PLAYER_SPEED
		if keys[pygame.K_d]:
			self.vel.x = PLAYER_SPEED
		self.pos += self.vel
		wall_thickness = 30
		min_x = wall_thickness + PLAYER_SIZE//2
		max_x = MAP_WIDTH - wall_thickness - PLAYER_SIZE//2
		min_y = wall_thickness + PLAYER_SIZE//2
		max_y = MAP_HEIGHT - wall_thickness - PLAYER_SIZE//2
		self.pos.x = max(min_x, min(max_x, self.pos.x))
		self.pos.y = max(min_y, min(max_y, self.pos.y))
		self.rect.center = self.pos

class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y, fast=False):
		super().__init__()
		self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE), pygame.SRCALPHA)
		if fast:
			self.image.fill((255, 140, 0))  # Orange für schnellen Gegner
			pygame.draw.rect(self.image, (0,0,0), self.image.get_rect(), 3)
			self.speed = PLAYER_SPEED * 1.25
		else:
			self.image.fill((200, 50, 50))
			pygame.draw.rect(self.image, (0,0,0), self.image.get_rect(), 3)
			self.speed = PLAYER_SPEED
		self.rect = self.image.get_rect(center=(x, y))
		self.pos = pygame.Vector2(x, y)

	def update(self, player_pos):
		direction = (player_pos - self.pos).normalize() if player_pos != self.pos else pygame.Vector2(0, 0)
		self.pos += direction * self.speed
		self.rect.center = self.pos

class ExploderEnemy(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE), pygame.SRCALPHA)
		self.image.fill((255, 0, 0))  # Rot für Exploder
		pygame.draw.circle(self.image, (255,255,0), (ENEMY_SIZE//2, ENEMY_SIZE//2), ENEMY_SIZE//2, 3)
		self.rect = self.image.get_rect(center=(x, y))
		self.pos = pygame.Vector2(x, y)
		self.speed = PLAYER_SPEED * 0.8
		self.exploded = False
		self.explode_timer = 0

	def update(self, player_pos):
		if self.exploded:
			# Explosion dauert 500ms
			if pygame.time.get_ticks() - self.explode_timer > 500:
				self.kill()
			return
		direction = (player_pos - self.pos).normalize() if player_pos != self.pos else pygame.Vector2(0, 0)
		self.pos += direction * self.speed
		self.rect.center = self.pos
		# Explodiere, wenn zu nah am Spieler
		if self.pos.distance_to(player_pos) < ENEMY_SIZE * 2.5:
			self.exploded = True
			self.explode_timer = pygame.time.get_ticks()

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
level_targets = [10, 20, 30, 40, 50]  # Gegner pro Level
level_kills = 0
level_show_ticks = pygame.time.get_ticks()
show_level = True
show_level_duration = 2000  # ms
lives = 3
level_spawned = 0


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



# --- Game-Over-Logik ---
def reset_game():
	global score, level, level_kills, level_spawned, lives, enemies, bullets, player, show_level, level_show_ticks
	score = 0
	level = 1
	level_kills = 0
	level_spawned = 0
	lives = 3
	enemies.empty()
	bullets.empty()
	player = Player(MAP_WIDTH//2, MAP_HEIGHT//2)
	show_level = True
	level_show_ticks = pygame.time.get_ticks()

def draw_button(rect, text):
	pygame.draw.rect(screen, (80,80,80), rect)
	pygame.draw.rect(screen, (255,255,255), rect, 3)
	txt = FONT.render(text, True, (255,255,255))
	txt_rect = txt.get_rect(center=rect.center)
	screen.blit(txt, txt_rect)

running = True
game_over = False
while running:
	clock.tick(FPS)
	now = pygame.time.get_ticks()
	seconds_since_start = (now - game_start_time) / 1000

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		if not game_over:
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				mx, my = pygame.mouse.get_pos()
				cam_offset = get_camera_offset(player)
				target = pygame.Vector2(mx + cam_offset.x, my + cam_offset.y)
				direction = (target - player.pos).normalize()
				bullets.add(Bullet(player.pos.x, player.pos.y, direction))
		else:
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				mx, my = pygame.mouse.get_pos()
				if retry_btn.collidepoint(mx, my):
					reset_game()
					game_over = False
					game_start_time = pygame.time.get_ticks()
				if quit_btn.collidepoint(mx, my):
					running = False

	if not game_over:
		# Levelwechsel: Nur wenn genug Gegner besiegt
		if level_kills >= level_targets[min(level-1, len(level_targets)-1)]:
			level += 1
			level_kills = 0
			level_spawned = 0
			show_level = True
			level_show_ticks = now
			enemies.empty()

		# Levelanzeige
		if show_level and now - level_show_ticks < show_level_duration:
			pass
		else:
			show_level = False

		# Gegner-Spawning nach 3 Sekunden, dann alle SPAWN_INTERVAL Sekunden, aber nur bis zur Zielanzahl
		if seconds_since_start > SPAWN_DELAY:
			if (level_spawned < level_targets[min(level-1, len(level_targets)-1)]) and (now - last_spawn_time > SPAWN_INTERVAL * 1000):
				# Gegner nicht zu nah am Spieler spawnen
				while True:
					ex = random.randint(0, MAP_WIDTH)
					ey = random.randint(0, MAP_HEIGHT)
					if pygame.Vector2(ex, ey).distance_to(player.pos) > PLAYER_SIZE * 6:
						break
				fast = level >= 3 and random.random() < 0.3  # Ab Level 3, 30% schnell
				# 15% Exploder ab Level 2
				if level >= 2 and random.random() < 0.15:
					enemies.add(ExploderEnemy(ex, ey))
				else:
					enemies.add(Enemy(ex, ey, fast=fast))
				last_spawn_time = now
				level_spawned += 1

		keys = pygame.key.get_pressed()
		player.update(keys)
		for enemy in enemies:
			enemy.update(player.pos)
		bullets.update()

		# Kollisionen
		for bullet, hit_enemies in pygame.sprite.groupcollide(bullets, enemies, True, True).items():
			for hit_enemy in hit_enemies:
				if getattr(hit_enemy, 'speed', ENEMY_SPEED) > ENEMY_SPEED:
					score += 2
				else:
					score += 1
				level_kills += 1
		hit_enemy = pygame.sprite.spritecollideany(player, enemies)
		if hit_enemy:
			if isinstance(hit_enemy, ExploderEnemy):
				if hit_enemy.exploded:
					# Exploder hat explodiert, Leben abziehen
					lives -= 1
					hit_enemy.kill()
					# Spawne neuen Gegner
					ex = random.randint(0, MAP_WIDTH)
					ey = random.randint(0, MAP_HEIGHT)
					fast = level >= 3 and random.random() < 0.3
					if level >= 2 and random.random() < 0.15:
						enemies.add(ExploderEnemy(ex, ey))
					else:
						enemies.add(Enemy(ex, ey, fast=fast))
					if lives <= 0:
						game_over = True
				else:
					# Exploder explodiert jetzt, aber noch kein Leben abziehen
					hit_enemy.exploded = True
					hit_enemy.explode_timer = pygame.time.get_ticks()
			else:
				lives -= 1
				hit_enemy.kill()
				# Spawne neuen Gegner
				ex = random.randint(0, MAP_WIDTH)
				ey = random.randint(0, MAP_HEIGHT)
				fast = level >= 3 and random.random() < 0.3
				if level >= 2 and random.random() < 0.15:
					enemies.add(ExploderEnemy(ex, ey))
				else:
					enemies.add(Enemy(ex, ey, fast=fast))
				if lives <= 0:
					game_over = True

		# Kamera Offset
		cam_offset = get_camera_offset(player)

		# --- Zeichnen ---
		# Hintergrund als schönes Grasfeld
		screen.fill((60, 180, 75))  # Sattes Grün für Gras
		# Bäume und Sträucher: Positionen werden einmalig erzeugt
		if 'tree_positions' not in globals():
			global tree_positions, bush_positions
			tree_positions = [(random.randint(0, MAP_WIDTH), random.randint(0, MAP_HEIGHT)) for _ in range(40)]
			bush_positions = [(random.randint(0, MAP_WIDTH), random.randint(0, MAP_HEIGHT)) for _ in range(60)]
		for tx, ty in tree_positions:
			tree_pos = (int(tx - cam_offset.x), int(ty - cam_offset.y))
			pygame.draw.rect(screen, (139,69,19), (tree_pos[0]-13, tree_pos[1]+25, 25, 50))
			pygame.draw.circle(screen, (34,139,34), (tree_pos[0], tree_pos[1]), int(22*2.5))
			pygame.draw.circle(screen, (0,100,0), (tree_pos[0]+int(8*2.5), tree_pos[1]-int(8*2.5)), int(12*2.5))
			pygame.draw.circle(screen, (0,100,0), (tree_pos[0]-int(8*2.5), tree_pos[1]-int(8*2.5)), int(12*2.5))
		for sx, sy in bush_positions:
			bush_pos = (int(sx - cam_offset.x), int(sy - cam_offset.y))
			pygame.draw.ellipse(screen, (0,128,0), (bush_pos[0]-10, bush_pos[1]-5, 20, 10))
			pygame.draw.ellipse(screen, (34,139,34), (bush_pos[0]-7, bush_pos[1]-3, 14, 7))
		for obs in obstacles:
			screen.blit(obs.image, obs.rect.move(-cam_offset.x, -cam_offset.y))
		for enemy in enemies:
			# Explosionsanimation für ExploderEnemy
			if hasattr(enemy, 'exploded') and enemy.exploded:
				explosion_pos = enemy.rect.move(-cam_offset.x, -cam_offset.y).center
				pygame.draw.circle(screen, (255,0,0), explosion_pos, ENEMY_SIZE*2)
			screen.blit(enemy.image, enemy.rect.move(-cam_offset.x, -cam_offset.y))
		for bullet in bullets:
			screen.blit(bullet.image, bullet.rect.move(-cam_offset.x, -cam_offset.y))
		screen.blit(player.image, player.rect.move(-cam_offset.x, -cam_offset.y))

		# HUD: Highscore, Level, Leben, verbleibende Gegner (mit Schatten)
		def draw_hud():
			hud_items = [
				(f"Score: {score}", (255,255,0), 20),
				(f"Level: {level}", (0,255,255), 60),
				(f"Leben: {lives}", (255,0,0), 100),
				(f"Noch: {max(0, level_targets[min(level-1, len(level_targets)-1)]-level_kills)}", (255,255,255), 140)
			]
			for text, color, y in hud_items:
				txt_shadow = FONT.render(text, True, (0,0,0))
				screen.blit(txt_shadow, (22, y+2))
				txt = FONT.render(text, True, color)
				screen.blit(txt, (20, y))

		draw_hud()
		# Draw walls only if the camera is at the map edge
		wall_thickness = 30
		cam_offset = get_camera_offset(player)
		# Top wall
		if cam_offset.y <= 0:
			pygame.draw.rect(screen, (100,100,100), (0, 0, WIDTH, wall_thickness))
		# Bottom wall
		if cam_offset.y >= MAP_HEIGHT-HEIGHT:
			pygame.draw.rect(screen, (100,100,100), (0, HEIGHT-wall_thickness, WIDTH, wall_thickness))
		# Left wall
		if cam_offset.x <= 0:
			pygame.draw.rect(screen, (100,100,100), (0, 0, wall_thickness, HEIGHT))
		# Right wall
		if cam_offset.x >= MAP_WIDTH-WIDTH:
			pygame.draw.rect(screen, (100,100,100), (WIDTH-wall_thickness, 0, wall_thickness, HEIGHT))

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

	else:
		# --- Game Over Screen ---
		screen.fill((30, 30, 30))
		# HUD oben links auch im Game Over
		def draw_hud():
			hud_items = [
				(f"Score: {score}", (255,255,0), 20),
				(f"Level: {level}", (0,255,255), 60),
				(f"Leben: {lives}", (255,0,0), 100),
				(f"Noch: {max(0, level_targets[min(level-1, len(level_targets)-1)]-level_kills)}", (255,255,255), 140)
			]
			for text, color, y in hud_items:
				txt_shadow = FONT.render(text, True, (0,0,0))
				screen.blit(txt_shadow, (22, y+2))
				txt = FONT.render(text, True, color)
				screen.blit(txt, (20, y))
		draw_hud()
		# Game Over Text und Buttons
		over_text = FONT.render("Du bist gestorben!", True, (255,0,0))
		rect = over_text.get_rect(center=(WIDTH//2, HEIGHT//2-60))
		screen.blit(over_text, rect)
		score_text_center = FONT.render(f"Score: {score}", True, (255,255,0))
		screen.blit(score_text_center, (WIDTH//2-80, HEIGHT//2))
		retry_btn = pygame.Rect(WIDTH//2-120, HEIGHT//2+60, 100, 50)
		quit_btn = pygame.Rect(WIDTH//2+20, HEIGHT//2+60, 100, 50)
		draw_button(retry_btn, "Neu versuchen")
		draw_button(quit_btn, "Beenden")

	pygame.display.flip()

pygame.quit()