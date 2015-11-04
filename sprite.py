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
		
		self.sprites = []
		
		self.index = 0
		
		self.spritesheet = load_image("%s.png" % fname)
		
		self.spritesheet_size = self.spritesheet.get_rect()
		sprites_x, sprites_y = self.spritesheet_size[2]/64, self.spritesheet_size[3]/64
		
		self.direction = 0
		
		for y in range(sprites_y):
			for x in range(sprites_x):
				
				sprite = pygame.Surface((self.sprite_width,self.sprite_height), pygame.SRCALPHA, 32).convert_alpha()
				sprite.blit(self.spritesheet, (0, 0), (x*64,y*64,(x*64)+64,(y*64)+64))
				
				self.sprites.append(sprite)
		
		self.player_move = []
		
		self.player_move.append(self.sprites[0:31]) #DOWN
		
		self.player_move.append(self.sprites[32:63]) #RIGHT
		
		self.player_move.append(self.sprites[64:95]) #UP
		
		self.player_move.append(self.sprites[96:127]) #LEFT
		
		
		self.image = self.player_move[self.direction][self.index]
		
		self.rect = self.image.get_rect()
		self.pos_x = pos[0]
		self.pos_y = pos[1]
		
		self.speed_x = 2
		self.speed_y = 1
		

	def draw(self, screen):
		screen.blit(self.image, (self.pos_x, self.pos_y))

	def move(self, direction):
		self.direction = direction
		
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
		
		self.index += 1
		if self.index == len(self.player_move[self.direction]):
			self.index = 0
		self.image = self.player_move[self.direction][self.index]
