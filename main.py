# -*- coding: utf-8 -*-

import os

import pygame
from pygame.locals import *

import pyscroll
import pyscroll.data
from pyscroll.util import PyscrollGroup

from player import Player
from level import Level

if not pygame.font:
	print 'Warning, fonts disabled'
if not pygame.mixer:
	print 'Warning, sound disabled'

BLACK = (0x00, 0x00, 0x00)

class MainGame(object):	# Game class
	
	def __init__(self):
		pygame.mixer.pre_init(44100, -16, 2, 2048)  # sounds
		pygame.init()
		pygame.display.set_caption("IsoGame")  # Set app name
		pygame.key.set_repeat(1, 20)
		
		self.width, self.height = 800, 600
		
		self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
		self.temp_surface = pygame.Surface((self.width / 1.5, self.height / 1.5)).convert()
		
		self.clock = pygame.time.Clock()
		
		self.player = Player("player", (100,100))
		
		self.level = Level("level1")
		
		self.levelGroup = self.level.group()
		self.levelGroup.add(self.player)
	
	def draw(self, screen):

		# center the map/screen on our Hero
		self.levelGroup.center(self.player.rect.center)

		# draw the map and all sprites
		self.levelGroup.draw(screen)
	
	def update(self, dt):
		""" Tasks that occur over time should be handled here
		"""
		self.levelGroup.update(dt)

		# check if the sprite's feet are colliding with wall
		# sprite must have a rect called feet, and move_back method,
		# otherwise this will fail
		"""
		for sprite in self.group.sprites():
			if sprite.feet.collidelist(self.walls) > -1:
				sprite.move_back(dt)
		"""
		
	""" main function """
	def main(self):
		while True:
			dt = self.clock.tick(30)
			
			for event in pygame.event.get():
				if event.type == QUIT:
					return
				elif event.type == pygame.KEYDOWN:
					if event.key == K_ESCAPE:
						return
				# this will be handled if the window is resized
				elif event.type == VIDEORESIZE:
					self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
					#self.map_layer.set_size((event.w / 2, event.h / 2))
				
				self.player.handle_event(event)
			
			#self.player.update()
			#self.update(dt)
			
			self.temp_surface.fill(BLACK)
			self.draw(self.temp_surface)
			self.player.draw(self.temp_surface)
			
			pygame.transform.scale(self.temp_surface, self.screen.get_size(), self.screen)
			
			pygame.display.flip()

if __name__ == '__main__':
	game = MainGame()
	game.main()
