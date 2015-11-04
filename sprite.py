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

class Sprite(pygame.sprite.Sprite):	# Player class
	def __init__(self, fname, pos):
		# Call the parent class (Sprite) constructor
		pygame.sprite.Sprite.__init__(self)
		
		
		self.sprite_width, self.sprite_height = 64, 64
		
		self.walk_index = 0
		self.standby_index = 0
		
		self.direction = 0
		
		self.pos_x = pos[0]
		self.pos_y = pos[1]
		
		self.speed_x = 4
		self.speed_y = 2
		
		self.moving = False
		
		self.move_sprites = self.load_spritesheet("player", "walk")
		self.standby_sprites = self.load_spritesheet("player", "standby")
		
		self.player_move = []
		self.player_standby = []
		
		self.player_move.append(self.move_sprites[0:31]) #DOWN
		self.player_move.append(self.move_sprites[32:63]) #RIGHT
		self.player_move.append(self.move_sprites[64:95]) #UP
		self.player_move.append(self.move_sprites[96:127]) #LEFT
		
		self.player_standby.append(self.standby_sprites[0:63]) #DOWN
		self.player_standby.append(self.standby_sprites[64:127]) #RIGHT
		self.player_standby.append(self.standby_sprites[128:191]) #UP
		self.player_standby.append(self.standby_sprites[192:255]) #LEFT
		
		
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
				sprite.blit(spritesheet, (0, 0), (x*64,y*64,(x*64)+64,(y*64)+64))
				
				sprites.append(sprite)
		return sprites

	def draw(self, screen):
		screen.blit(self.image, (self.pos_x, self.pos_y))

	def move(self, direction):
		self.direction = direction
		self.moving = True
		self.standby_index = 0
		
		if self.direction == 0:
			self.pos_x -= self.speed_x
			self.pos_y += self.speed_y
		elif self.direction == 1:
			self.pos_x += self.speed_x
			self.pos_y += self.speed_y
		elif self.direction == 2:
			self.pos_x += self.speed_x
			self.pos_y -= self.speed_y
		elif self.direction == 3:
			self.pos_x -= self.speed_x
			self.pos_y -= self.speed_y

	def update(self):
		if self.moving:
			self.walk_index += 1
			if self.walk_index >= len(self.player_move[self.direction]):
				self.walk_index = 0
			self.image = self.player_move[self.direction][self.walk_index]
		else:
			self.standby_index += 1
			if self.standby_index >= len(self.player_standby[self.direction]):
				self.standby_index = 0
			self.image = self.player_standby[self.direction][self.standby_index]
			
		self.moving = False
