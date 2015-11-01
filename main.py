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
		print 'Cannot load image:', name
		raise SystemExit, message
	
	
	return image, image.get_rect()

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

		self.screen = pygame.display.set_mode((self.width, self.height))

		pygame.display.set_caption('IsoGame')

		self.tiled_map = pytmx.TiledMap(os.path.join('data', 'level1.tmx'))
		
		self.tileset = load_image("iso-64x64-outside.png")
		
		self.screen.fill((0x00,0x00,0x00))
		

	def draw_level(self):
		for layer in self.tiled_map.layers:
			for x, y, image in layer.tiles():
				
				self.tile = pygame.Surface((self.tile_width,self.tile_height), pygame.SRCALPHA, 32).convert_alpha()
				
				xPos = (( x - y ) * self.tile_width/2) + self.width/2
				yPos = (( x + y ) * self.tile_height/2) + self.height/2

				self.tile.blit(self.tileset[0], (0, 0), image[1])
				self.screen.blit(self.tile, (xPos, yPos - self.width/2))

		pygame.display.flip()


	""" main function """
	def main(self):
		while True:
			self.draw_level()
			for event in pygame.event.get():
				if event.type == QUIT:
					return
				elif event.type == KEYDOWN and event.key == K_ESCAPE:
					return

if __name__ == '__main__':
	game = MainGame()
	game.main()
