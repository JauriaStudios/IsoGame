# -*- coding: utf-8 -*-

import os

import pygame
import pytmx

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

def load_sound(name):
	class NoneSound:
		def play(self): pass
	if not pygame.mixer:
		return NoneSound()
	fullname = os.path.join('data', name)
	try:
		sound = pygame.mixer.Sound(fullname)
	except pygame.error, message:
		print 'Cannot load sound:', wav
		raise SystemExit, message
	return sound

class MainGame(object):         # Game class

	def __init__(self):
		pygame.mixer.pre_init(44100, -16, 2, 2048)  # sounds
		pygame.init()
		pygame.display.set_caption("IsoGame")  # Set app name
		pygame.key.set_repeat(100, 20)

		self.width, self.height = 800, 600
		self.tile_width, self.tile_height = 64, 32
		self.sprite_width, self.sprite_height = 64, 64

		self.screen = pygame.display.set_mode((self.width, self.height))

		self.load_level("level1")
		self.player = self.load_spritesheet("player")

	def load_spritesheet(self, name):
		self.spritesheet = load_image("%s.png" % name)
		
		spritesheet_size = self.spritesheet.get_rect()
		sprites_x, sprites_y = spritesheet_size[2]/64, spritesheet_size[3]/64
		
		sprites = []
		
		for y in range(sprites_y):
			for x in range(sprites_x):
				sprite = pygame.Surface((self.sprite_width,self.sprite_height), pygame.SRCALPHA, 32).convert_alpha()
				sprite.blit(self.spritesheet, (0, 0), (x*64,y*64,(x*64)+64,(y*64)+64))
				
				sprites.append(sprite)
		return sprites

	def draw_spritesheet(self):
		for sprite in self.player:
			self.screen.blit(sprite, (200,200))
		
		pygame.display.flip()

	def load_level(self,name):
		self.tiled_map = pytmx.TiledMap(os.path.join('data', '%s.tmx'% name))
		self.tileset = load_image("iso-64x64-outside.png")
		

	def draw_level(self):
		self.screen.fill((0x00,0x00,0x00))

		for layer in self.tiled_map.layers:
			for x, y, image in layer.tiles():
				
				self.tile = pygame.Surface((self.tile_width,self.tile_height), pygame.SRCALPHA, 32).convert_alpha()
				self.tile.blit(self.tileset, (0, 0), image[1])

				xPos = (( x - y ) * self.tile_width/2) + self.width/2
				yPos = (( x + y ) * self.tile_height/2) + self.height/2

				self.screen.blit(self.tile, (xPos, yPos - self.width/2))

		pygame.display.flip()


	""" main function """
	def main(self):
		while True:
			for event in pygame.event.get():
				if event.type == QUIT:
					return
				elif event.type == KEYDOWN and event.key == K_ESCAPE:
					return
			self.draw_level()
			self.draw_spritesheet()

if __name__ == '__main__':
	game = MainGame()
	game.main()
