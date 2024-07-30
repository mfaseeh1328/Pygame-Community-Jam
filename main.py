import pygame, sys, math, time, random
import asyncio
from pytmx.util_pygame import load_pygame

pygame.init()
# creating and modifying level
class Level():
	tile_size = 32
	def __init__(self, map_tmx):
		self.map = map_tmx
		self.pos_rect = []
		self.world_offset = [0, 0]

	def create(self):
		for layer in self.map.visible_layers:
			for tiles in layer.tiles():
				x, y, img = tiles[0]*Level.tile_size, tiles[1]*Level.tile_size, tiles[2]
				rect = pygame.Rect(x, y, Level.tile_size, Level.tile_size)
				self.pos_rect.append([img, rect])

	def draw(self):
		for pos in self.pos_rect:	
			WIN.blit(pos[0], (pos[1][0]+self.world_offset[0], pos[1][1]+self.world_offset[1]))

	def update(self):
		self.draw()
		pass

# creating and modifying the enemy boses
class Enemy():
	def __init__(self, map):
		self.bat_object = map.get_layer_by_name("bat")
		self.knight_object = map.get_layer_by_name("knight")
		self.striker_object = map.get_layer_by_name("striker")
		self.bat_index = 0
		self.knight_index = 0
		self.striker_index = 0

		self.vel = 1

	def draw(self, world_offset, tile_rect):
		def animate_bat():
			self.bat_index += 1
			if self.bat_index >= 32:
				self.bat_index = 0
		animate_bat()

		def animate_knight():
			self.knight_index += 1
			if self.knight_index >= 60:
				self.knight_index = 0
		animate_knight()

		def animate_striker():
			self.striker_index += 1
			if self.striker_index >= 32:
				self.striker_index = 0
		animate_striker()

		for bat, knight, striker in zip(self.bat_object, self.knight_object, self.striker_object):
			WIN.blit(pygame.transform.scale(bat_image[self.bat_index // 8], (bat.width, bat.height)), (bat.x + world_offset[0], bat.y))
			WIN.blit(pygame.transform.scale(knight_image[self.knight_index // 4], (knight.width, knight.height)), (knight.x + world_offset[0], knight.y))
			WIN.blit(pygame.transform.scale(striker_image[self.striker_index // 4], (striker.width, striker.height)), (striker.x + world_offset[0], striker.y))
			

	def update(self, world_offset, tile_rect):
		self.draw(world_offset, tile_rect)

# creating and modifying the interst
class Background():
	def __init__(self):
		self.width, self.height = WIDTH, HEIGHT
		self.x, self.y = 0, 0

	def draw(self):
		for i in range(3):
			WIN.blit(pygame.transform.scale(bg_images[i], (self.width, self.height)), (self.x, self.y))

	def update(self):
		self.draw()

# creating and modifying the player
class Player():
	def __init__(self, x, y, w, h):
		self.player_image_state = player_idle_image
		self.player_state = "idle"
		self.rect = pygame.Rect(x, y, w, h)
		self.dx, self.dy = 0, 0
		self.vel = 5
		self.index = 0
		self.flip = False
		self.vel_y, self.jump_height = 5, 12
		self.on_ground, self.gravity = False, 0.5
		self.dash = False
		self.dash_vel, self.dash_timer, self.dash_cooldown = 12, 20, 20
		self.dash_index = 0
		self.index_divisor = 8

	def draw(self):

		def animate():
			try:
				self.index += 1
				if self.index >= 48:
					self.index = 0
			except Exception as error:
				print(error)

		animate()

		if self.player_state == "run":
			self.player_image_state = player_run_image
			self.index_divisor = 6

		if self.player_state == "dash":
			self.player_image_state = player_dash_image
			self.index_divisor = 8

		if self.player_state == "jump":
			self.player_image_state = player_jump_image
			self.index_divisor = 8
		
		if self.player_state == "fall":
			self.player_image_state = player_fall_image
			self.index_divisor = 8
		
		if self.player_state == "idle":
			self.player_image_state = player_idle_image
			self.index_divisor = 8

		WIN.blit(pygame.transform.flip(self.player_image_state[self.index // self.index_divisor], self.flip, False), (self.rect.x-20, self.rect.y-16))

	def move(self):
		self.dx = 0
		keys = pygame.key.get_pressed()

		if keys[pygame.K_LEFT]:
			self.dx = -self.vel
			self.flip = True
			self.player_state = "run"

		elif keys[pygame.K_RIGHT]:
			self.dx = self.vel
			self.flip = False
			self.player_state = "run"
		
		else:
			self.player_state = "idle"

		self.rect.x += self.dx

	def jump(self):
		keys = pygame.key.get_pressed()
		self.dy = 0

		# jumping
		if keys[pygame.K_UP] and self.on_ground == True:
			self.vel_y = -self.jump_height
			self.on_ground = False

		# apply graivty	
		self.vel_y += self.gravity
		self.dy += self.vel_y
		self.rect.y += self.dy 

		if self.rect.y > HEIGHT:
			self.rect.bottom = HEIGHT - self.rect.height - (tile_size*2)
			self.on_ground = True
			self.vel_y = 0

		if self.rect.y < 0:
			self.rect.top = 0
			self.vel_y = 0

	def dash_move(self):

		def animate():
			self.dash_index += 1
			if self.dash_index >= 10:
				self.dash_index = 0

		animate()

		keys_pressed = pygame.key.get_pressed()

		if keys_pressed[pygame.K_SPACE] and self.dash_cooldown == 0 and self.dash == False:
			self.dash = True
			self.dash_cooldown = 20
		try:
			if self.dash:
				self.player_state = "dash"
				if self.dash_timer > 0:
					self.dash_timer -= 1

					if keys_pressed[pygame.K_LEFT]:
						self.rect.x -= self.dash_vel
						WIN.blit(pygame.transform.flip(player_dash[self.dash_index // 2], True, False), (self.rect.x+65, self.rect.y))

					if keys_pressed[pygame.K_RIGHT]:
						self.rect.x += self.dash_vel
						WIN.blit(player_dash[self.dash_index // 2], (self.rect.x-115, self.rect.y))
				else:
					self.dash = False

			if self.dash_cooldown > 0:
				self.dash_cooldown -= 1

			if not self.dash:
				self.dash_timer = 12

		except Exception as error:
			print(error)
	
	def update(self):
		self.draw()
		self.move()
		self.dash_move()

		if self.vel_y < 0 and self.on_ground == False:
			self.player_state = "jump"
		elif self.vel_y > 0 and self.on_ground == False:
			self.player_state = "fall"

def collision(tile_rect, world_offset, player, dx, dy):
	future_rect = player.move(dx, dy)

	for pos in tile_rect:
		player_rect = pygame.Rect(player.x, player.y+4, player.w-4, player.h-4)

		platform_rect = pygame.Rect(pos[1].x + world_offset[0], pos[1].y, pos[1].w, pos[1].h)
		if player_rect.colliderect(platform_rect):
			return platform_rect
		
	return None


WIDTH, HEIGHT = 1088, 736
FPS = 60
tile_size = 32
# window settings
WIN = pygame.display.set_mode((WIDTH, HEIGHT))# pygame.SCALED | pygame.FULLSCREEN)
pygame.display.set_caption("Insterstellar Miner")

# loading the level data
MAP_TMX = load_pygame("level/tmx/1.tmx")

# loading images and assets
# logo
logo_image = pygame.transform.scale(pygame.image.load("Assets/logo.png"), (WIDTH//2, 219)).convert_alpha()
game_logo_image = [pygame.image.load(f"Assets/logo_animation/{i}.png").convert_alpha() for i in range(1, 145)]
# bg images
bg_images = [pygame.image.load(f"Assets/space/{i}.png").convert_alpha() for i in range(1, 4)]
# enemy images
bat_image = [pygame.transform.flip(pygame.image.load(f"Assets/enemy/bat/{i}.png"), True, False).convert_alpha() for i in range(1, 5)]
knight_image = [pygame.transform.flip(pygame.image.load(f"Assets/enemy/knight/{i}.png"), True, False).convert_alpha() for i in range(1, 16)]
striker_image = [pygame.transform.flip(pygame.image.load(f"Assets/enemy/striker/{i}.png"), True, False).convert_alpha() for i in range(1, 9)]

# player images
player_idle_image = [pygame.transform.scale2x(pygame.image.load(f"Assets/player/idle/{i}.png")).convert_alpha() for i in range(1, 7)]
player_run_image = [pygame.transform.scale2x(pygame.image.load(f"Assets/player/run/{i}.png")).convert_alpha() for i in range(1, 9)]
player_dash_image = [pygame.transform.scale2x(pygame.image.load(f"Assets/player/run/{i}.png")).convert_alpha() for i in range(1, 7)]
player_jump_image = [pygame.transform.scale2x(pygame.image.load(f"Assets/player/run/{i}.png")).convert_alpha() for i in range(1, 7)]
player_fall_image = [pygame.transform.scale2x(pygame.image.load(f"Assets/player/run/{i}.png")).convert_alpha() for i in range(1, 7)]
player_dash = [pygame.transform.scale2x(pygame.image.load(f"Assets/vfx/{i}.png")).convert_alpha() for i in range(1, 6)]
# enemy images

CLOCK = pygame.time.Clock()

# main App class
class App():
	def __init__(self):
		self.running = True
		self.font = pygame.font.Font("Font/pixel.ttf", 20)
		self.background = Background()
		self.enemy = Enemy(MAP_TMX)
		self.player = Player(100, 500, 36, 36)
		self.level = Level(MAP_TMX)

		self.level.create()
		
		self.welcome_input = False
		self.game_logo_index = 0
		self.game_logo_animation_index = 0

	def write_msg(self, msg, color, x, y):
		render = self.font.render(msg, 1, color, (40, 40, 40))
		WIN.blit(render, (x, y))

	def welcome_screen(self):
		WIN.fill(("black"))
		font = pygame.font.Font("Font/pixel.ttf", 40)
		render = font.render("Made With ", 1, "green")
		msg = font.render("Press Space To Play!", 1, "green")

		WIN.blit(render, (420, math.sin(time.time()) * 10 + 240))
		WIN.blit(msg, (270, math.sin(time.time()) * 10 + 600))
		WIN.blit(logo_image, (300, math.sin(time.time()) * 10 + 300))

	def game_logo_screen(self):
		WIN.fill(("black"))
		
		def animate():
			try:
				self.game_logo_animation_index += 1
				if self.game_logo_animation_index >= 288:
					self.game_logo_animation_index = 287
			except Exception as error:
				print(error)
		animate()

		WIN.blit(game_logo_image[self.game_logo_animation_index // 2], (0, 0))

	def exit(self):
		if self.running:
			self.running = False
		sys.exit()
		pygame.quit()

	# main game loop
	async def main(self):
		while self.running:

			WIN.fill((40, 60, 40))
			self.background.update()
			self.level.update()
			self.enemy.update(self.level.world_offset, self.level.pos_rect)
			self.write_msg(f"FPS: {round(CLOCK.get_fps(), 1)}", "green", 10, 10)
			self.player.update()

			# moving the player in x-axis and collision mechanics
			try:
				x_collision = collision(self.level.pos_rect, self.level.world_offset, self.player.rect, self.player.dx, 0)

				if x_collision:

					try:
						rand_color = random.choice(["red", "green", "blue", "yellow", "pink", "purple", "orange", "magenta", "cyan"])
						color_surf = pygame.Surface((x_collision.w, x_collision.h))
						color_surf.fill(rand_color)
						color_surf.set_alpha(150)
						WIN.blit(color_surf, (x_collision))
					except Exception as error:
						print(error)

					self.player.player_state = ""
					if self.player.dx > 0:
						self.player.rect.right = x_collision.left

					if self.player.dx < 0:
						self.player.rect.left = x_collision.right
			except Exception as error:
				print(error)

			# creating the player jump and collision mechanics
			self.player.jump()
			y_collision = collision(self.level.pos_rect, self.level.world_offset, self.player.rect, 0, self.player.dy)
			
			try:
				if y_collision:

					try:
						rand_color = random.choice(["red", "green", "blue", "yellow", "pink", "purple", "orange", "magenta", "cyan"])
						color_surf = pygame.Surface((y_collision.w, y_collision.h))
						color_surf.fill(rand_color)
						color_surf.set_alpha(150)
						WIN.blit(color_surf, (y_collision))
					except Exception as error:
						print(error)

					if self.player.vel_y > 0:
						self.player.rect.bottom = y_collision.top
						self.player.vel_y = 0
						self.player.on_ground = True
					
					if self.player.vel_y < 0:
						self.player.rect.top = y_collision.bottom
						self.player.vel_y = 0
			except Exception as error:
				print(error)
			
			# changing the world offset according to the player movement
			if self.player.rect.x >= WIDTH:
				self.player.rect.x = 100
				self.level.world_offset[0] -= (WIDTH//2)
			if self.player.rect.x <= 0:
				self.player.rect.x = WIDTH - self.player.rect.w
				self.level.world_offset[0] += (WIDTH//2)
			
			#if not self.welcome_input and self.game_logo_index == 0:
			#	self.welcome_screen()

			#if self.welcome_input:
			#	self.game_logo_index += 1
			#	self.game_logo_screen()

			#if self.game_logo_index >= 300:
			#	self.welcome_input = False

			CLOCK.tick(FPS)
			pygame.display.update()

			# event handler
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						exit()
					if event.key == pygame.K_SPACE and self.game_logo_index == 0:
						self.welcome_input = True

			await asyncio.sleep(0)

if __name__ == '__main__':
	app = App()
	asyncio.run(app.main())