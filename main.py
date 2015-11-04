# -*- coding: utf-8 -*-

import os

import pytmx

import pygame
from pygame.locals import *

from sprite import Sprite
from level import Level

if not pygame.font:
	print 'Warning, fonts disabled'
if not pygame.mixer:
	print 'Warning, sound disabled'


class MainGame(object):	# Game class

	def __init__(self):
		pygame.mixer.pre_init(44100, -16, 2, 2048)  # sounds
		pygame.init()
		pygame.display.set_caption("IsoGame")  # Set app name
		pygame.key.set_repeat(100, 20)
		
		self.width, self.height = 800, 600
		
		self.screen = pygame.display.set_mode((self.width, self.height))
		
		self.clock = pygame.time.Clock()
		
		self.level= Level("level1")
		
		self.player = Sprite("player", (100,100))

	""" main function """
	def main(self):
		while True:
			self.clock.tick(60)
			
			for event in pygame.event.get():
				if event.type == QUIT:
					return
				elif event.type == KEYDOWN and event.key == K_ESCAPE:
					return
				elif event.type == KEYDOWN and event.key == K_DOWN:
					self.player.move(0)
				elif event.type == KEYDOWN and event.key == K_RIGHT:
					self.player.move(1)
				elif event.type == KEYDOWN and event.key == K_UP:
					self.player.move(2)
				elif event.type == KEYDOWN and event.key == K_LEFT:
					self.player.move(3)
			
			self.screen.fill((0x00,0x00,0x00))
			
			self.player.update()
			
			self.level.draw(self.screen)
			self.player.draw(self.screen)
			
			pygame.display.flip()

if __name__ == '__main__':
	game = MainGame()
	game.main()
