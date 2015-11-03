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

class Sprite(object):         # Player class
	def __init__(self, fname):
		self.sprite_width, self.sprite_height = 64, 64

		self.sprites = []
		self.sprite = self.load(fname)

	def load(self, name):
		self.spritesheet = load_image("%s.png" % name)
		
		spritesheet_size = self.spritesheet.get_rect()
		sprites_x, sprites_y = spritesheet_size[2]/64, spritesheet_size[3]/64
		
		
		for y in range(sprites_y):
			for x in range(sprites_x):
				
				sprite = pygame.Surface((self.sprite_width,self.sprite_height), pygame.SRCALPHA, 32).convert_alpha()
				sprite.blit(self.spritesheet, (0, 0), (x*64,y*64,(x*64)+64,(y*64)+64))
				
				self.sprites.append(sprite)
				
		return self.sprites

	def draw(self,screen):
		
		self.player_move_up = self.sprites[0::32]
		self.player_move_down = self.sprites[33:65]
		self.player_move_left = self.sprites[66:98]
		self.player_move_right = self.sprites[98:130]
		
		screen.blit(self.player_move_down[0], (200,200))
