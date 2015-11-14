# -*- coding: utf-8 -*-

import os

import pytmx

import pygame
from pygame.locals import *

import pyscroll
import pyscroll.data
from pyscroll.util import PyscrollGroup

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

class Level(object):	# Level class
	
	def __init__(self, fname):
		
		#pygame.sprite.Sprite.__init__(self)
		
		self.width, self.height = 800, 600
		self.tile_width, self.tile_height = 64, 32
		
		self.image = pygame.Surface((self.width,self.height), pygame.SRCALPHA, 32).convert_alpha()
		self.rect = self.image.get_rect()
		
		self.tiled_map = pytmx.TiledMap(os.path.join('data', '%s.tmx'% fname))
		self.tileset = load_image("iso-64x64-outside.png")
		
		self.map_data = pyscroll.data.TiledMapData(self.tiled_map)
		
		self.map_layer = pyscroll.BufferedRenderer(self.map_data, (self.width / 2, self.height / 2), clamp_camera=True)
		
		self.group = PyscrollGroup(map_layer=self.map_layer, default_layer=2)
		
	def get_group(self):
		
		return self.group
		
		
		"""
		self.layerName = layer
		
		
		self.layer = self.tiled_map.get_layer_by_name(self.layerName)
		
		for x, y, image in self.layer.tiles():
			
			self.tile = pygame.Surface((self.tile_width,self.tile_height), pygame.SRCALPHA, 32).convert_alpha()
			self.tile.blit(self.tileset, (0, 0), image[1])
			
			xPos = (( x - y ) * self.tile_width/2) + self.width/2
			yPos = (( x + y ) * self.tile_height/2) + self.height/2
			
			self.image.blit(self.tile, (xPos, yPos))
		"""
