# -*- coding: utf-8 -*-

import os

import pygame
from pygame.locals import *

if not pygame.font:
	print 'Warning, fonts disabled'
if not pygame.mixer:
	print 'Warning, sound disabled'

def load_image(name):
	fullname = os.path.join('data', name)
	try:
		image = pygame.image.load(fullname).convert_alpha()
	except pygame.error, message:
		print 'Cannot load image: ', name
		raise SystemExit, message

	return image

class Player(pygame.sprite.Sprite):	# Player class
	def __init__(self, fname, pos):

		# Call the parent class (Sprite) constructor
		pygame.sprite.Sprite.__init__(self)

		self.sprite_width, self.sprite_height = 64, 64

		self.walk_index = 0
		self.standby_index = 0

		self.direction = 0

		self.pos_x = pos[0]
		self.pos_y = pos[1]

		self.up = False
		self.down = False
		self.left = False
		self.right = False

		self.walking = False
		self.running = False

		self.walk_speed_x = 4
		self.walk_speed_y = 2

		self.running_speed_x = 6
		self.running_speed_y = 3


		self.move_sprites = self.load_spritesheet("player", "walk")
		self.standby_sprites = self.load_spritesheet("player", "standby")

		self.player_move = []
		self.player_standby = []

		self.player_move.append(self.move_sprites[0:31]) # Down - Left
		self.player_move.append(self.move_sprites[32:63]) # Down
		self.player_move.append(self.move_sprites[64:95]) # Down - Right
		self.player_move.append(self.move_sprites[96:127]) # Right

		self.player_move.append(self.move_sprites[128:159]) # Up - Right
		self.player_move.append(self.move_sprites[160:191]) # Up
		self.player_move.append(self.move_sprites[192:223]) # Up - Left
		self.player_move.append(self.move_sprites[224:255]) # Left

		self.player_standby.append(self.standby_sprites[0:63]) # Down - Left
		self.player_standby.append(self.standby_sprites[64:127]) # Down
		self.player_standby.append(self.standby_sprites[128:191]) # Down - Right
		self.player_standby.append(self.standby_sprites[192:255]) # Right

		self.player_standby.append(self.standby_sprites[256:319]) # Up - Right
		self.player_standby.append(self.standby_sprites[320:383]) # Up
		self.player_standby.append(self.standby_sprites[384:447]) # Up - Left
		self.player_standby.append(self.standby_sprites[448:511]) # Left


		self.image = self.player_standby[self.direction][self.standby_index]
		self.rect = self.image.get_rect()


	def load_spritesheet(self, fname, tname):
		spritesheet = load_image("%s_%s.png" % (fname, tname))

		sprites = []
		spritesheet_size = spritesheet.get_rect()
		sprites_x, sprites_y = spritesheet_size[2]/self.sprite_width, spritesheet_size[3]/self.sprite_height

		for y in range(sprites_y):
			for x in range(sprites_x):

				sprite = pygame.Surface((self.sprite_width,self.sprite_height), pygame.SRCALPHA, 32).convert_alpha()
				sprite.blit(spritesheet, (0, 0), (x * self.sprite_width,y * self.sprite_height,(x * self.sprite_width) + self.sprite_width,(y * self.sprite_height) + self.sprite_height))

				sprites.append(sprite)
		return sprites

	def handle_event(self, event):

		if event.type == pygame.KEYDOWN:
			if event.key == K_DOWN:
				self.down = True
			if event.key == K_RIGHT:
				self.right = True
			if event.key == K_UP:
				self.up = True
			if event.key == K_LEFT:
				self.left = True

			if event.key == K_LSHIFT:
				self.running = True

		elif event.type == pygame.KEYUP:
			if event.key == K_DOWN:
				self.down = False
			if event.key == K_RIGHT:
				self.right = False
			if event.key == K_UP:
				self.up = False
			if event.key == K_LEFT:
				self.left = False

			if event.key == K_LSHIFT:
				self.running = False


		if self.down and self.left:
			self.move(0,self.running)

		elif self.down and self.right:
			self.move(2,self.running)

		elif self.up and self.right:
			self.move(4,self.running)

		elif self.up and self.left:
			self.move(6,self.running)

		elif self.down:
			self.move(1,self.running)

		elif self.right:
			self.move(3,self.running)

		elif self.up:
			self.move(5,self.running)

		elif self.left:
			self.move(7,self.running)

	def draw(self, screen):
		screen.blit(self.image, (self.pos_x, self.pos_y))

	def move(self, direction, running):
		self.direction = direction
		self.walking = True
		self.standby_index = 0

		if running:
			speed_x, speed_y = self.running_speed_x, self.running_speed_y
		else:
			speed_x, speed_y = self.walk_speed_x, self.walk_speed_y

		if self.direction == 0:
			self.pos_y += speed_y # Down
			self.pos_x -= speed_x # Left

		elif self.direction == 1:
			self.pos_y += speed_y # Down

		elif self.direction == 2:
			self.pos_y += speed_y # Down
			self.pos_x += speed_x # Right

		elif self.direction == 3:
			self.pos_x += speed_x # Right

		elif self.direction == 4:
			self.pos_y -= speed_y # Up
			self.pos_x += speed_x # Right

		elif self.direction == 5:
			self.pos_y -= speed_y # Up

		elif self.direction == 6:
			self.pos_y -= speed_y # Up
			self.pos_x -= speed_x # Left
			
		elif self.direction == 7:
			self.pos_x -= speed_x # Left

	def update(self):
		if self.walking:
			self.walk_index += 1
			if self.walk_index == len(self.player_move[self.direction]):
				self.walk_index = 0
			self.image = self.player_move[self.direction][self.walk_index]
		else:
			self.standby_index += 1
			if self.standby_index == len(self.player_standby[self.direction]):
				self.standby_index = 0
			self.image = self.player_standby[self.direction][self.standby_index]

		self.walking = False
