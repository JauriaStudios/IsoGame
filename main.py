# -*- coding: utf-8 -*-

import os

import pygame
from pygame.locals import *

from sprite import Sprite
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
		
		self.screen = pygame.display.set_mode((self.width, self.height))
		
		self.clock = pygame.time.Clock()
		
		self.player = Sprite("player", (100,100))
		
		self.levelLayer1 = Level("level1", "background")
		self.levelLayer2 = Level("level1", "layer1")
		self.levelLayer3 = Level("level1", "layer2")
		self.levelLayer4 = Level("level1", "layer3")
		self.levelLayer5 = Level("level1", "layer4")
		self.levelLayer6 = Level("level1", "layer5")
		
		
		self.levelBGGroup = pygame.sprite.OrderedUpdates()
		self.levelGroup = pygame.sprite.OrderedUpdates()
		
		self.levelBGGroup.add(self.levelLayer1)
		
		self.levelGroup.add(self.levelLayer2)
		self.levelGroup.add(self.levelLayer3)
		self.levelGroup.add(self.levelLayer4)
		self.levelGroup.add(self.levelLayer5)
		self.levelGroup.add(self.levelLayer6)
		
	
	""" main function """
	def main(self):
		while True:
			self.clock.tick(30)
			
			for event in pygame.event.get():
				if event.type == QUIT:
					return
				if event.type == pygame.KEYDOWN:
					if event.key == K_ESCAPE:
						return
				
				self.player.handle_event(event)
				
			self.player.update()
			
			self.screen.fill(BLACK)
			
			self.levelBGGroup.draw(self.screen)
			
			self.player.draw(self.screen)
			
			self.levelGroup.draw(self.screen)
			
			
			
			pygame.display.flip()

if __name__ == '__main__':
	game = MainGame()
	game.main()
