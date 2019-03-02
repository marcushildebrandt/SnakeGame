#! /usr/bin/env python
# -*- coding: utf-8 -*-

#a simple game with pygame

import random
import pygame
from pygame.locals import *

X = 0
Y = 1

class Game:
	
	def __init__(self, title, screen_width, screen_height):
		self.game_finished = False
		pygame.init()
		pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
		random.seed()
		self.clock = pygame.time.Clock()
		self.frame_rate = 30
		self.title = title
		self.screen_width = screen_width
		self.screen_height = screen_height
		self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
		pygame.display.set_caption(self.title)
		self.background = Background((self.screen_width, self.screen_height), (0,0,0))
		self.block_width = 20
		self.block_height = 20
		self.radius = 9
		self.snake = Snake((290, 290), (self.block_width, self.block_height), (255,255,255), self.radius)
		self.fruit = Fruit((200, 290), (self.block_width, self.block_height), (0, 255, 0), (self.screen_width, self.screen_height), self.radius)
		self.sprite_group = pygame.sprite.Group(self.snake, self.fruit)
		self.new_snake_direction = (1, 0)
		pygame.mixer.music.load("data/music.mp3")
		pygame.mixer.music.play(loops=-1)
		self.pick_up = pygame.mixer.Sound("data/sfx01.wav")
		self.failed = pygame.mixer.Sound("data/sfx02.wav")
		self.score = 0
		self.font = pygame.font.Font("data/freesansbold.ttf", 20)
		self.font_image = self.font.render(str(self.score), True, (255,255,255))
	
	def run(self):
		while(not self.game_finished):
			self.clock.tick(self.frame_rate)
			self.process_events()
			self.update_objects()
			self.draw_on_the_screen()
	
	def process_events(self):
		for event in pygame.event.get():
			if self.is_quit_event(event):
				self.game_finished = True
			elif self.is_new_direction(event):
				self.snake.set_direction(self.new_snake_direction)
	
	def update_objects(self):
		self.sprite_group.update()
		if pygame.sprite.collide_rect(self.fruit, self.snake):
			self.fruit.new()
			self.snake.new()
			self.pick_up.play()
			self.score += 1
		if self.is_out_on_the_screen(self.snake.rect):
			self.reset()
			self.failed.play()
		if self.snake.has_blocks_colliding():
			self.reset()
			self.failed.play()
	
	def draw_on_the_screen(self):
		self.screen.blit(self.background.image, self.background.rect)
		self.font_image = self.font.render(str(self.score), True, (255,255,255))
		size =self.font.size(str(self.score))
		position = (self.screen_width-size[X], 0)
		self.screen.blit(self.font_image, (position, size))
		self.sprite_group.draw(self.screen)
		pygame.display.flip()
	
	def is_quit_event(self, event):
		option1 = event.type == QUIT
		option2 = event.type == KEYDOWN and event.key == K_ESCAPE
		if option1 or option2: return True
		else: return False
	
	def is_new_direction(self, event):
		is_up = event.type == KEYDOWN and event.key == K_UP
		is_right = event.type == KEYDOWN and event.key == K_RIGHT
		is_down = event.type == KEYDOWN and event.key == K_DOWN
		is_left = event.type == KEYDOWN and event.key == K_LEFT
		if is_up:
			self.new_snake_direction = (0, -1)
		elif is_right:
			self.new_snake_direction = (1, 0)
		elif is_down:
			self.new_snake_direction = (0, 1)
		elif is_left:
			self.new_snake_direction = (-1, 0)
		else: return False
		return True
	
	def is_out_on_the_screen(self, rect):
		is_to_right = rect.x + rect.w > self.screen_width
		is_to_left = rect.x < 0
		is_to_up = rect.y < 0
		is_to_down = rect.y + rect.h > self.screen_height
		if is_to_up or is_to_right or is_to_down or is_to_left:
			return True
		else: return False
	
	def reset(self):
		self.fruit.new()
		self.snake.reset()
		self.score = 0


class Snake(pygame.sprite.Sprite):
	
	def __init__(self, position, size, color, radius):
		pygame.sprite.Sprite.__init__(self)
		self.color = color
		self.radius = radius
		self.image = pygame.Surface(size)
		self.image = self.image.convert()
		pygame.draw.circle(self.image, self.color, (radius, radius), radius)
		self.rect = pygame.Rect(position, size)
		self.start_rect = pygame.Rect(position, size)
		self.direction = (1, 0)
		self.start_direction = (1, 0)
		self.speed = 5
		self.body = []
		self.track = []
		self.track_limite = self.rect.w // self.speed
	
	def set_direction(self, new_direction):
		self.direction = new_direction
	
	def update(self):
		self.update_track((self.rect.x, self.rect.y), self.track_limite)
		self.rect.x += self.direction[X] * self.speed
		self.rect.y += self.direction[Y] * self.speed
		if len(self.body) > 0:
			if len(self.body) > 1:
				for i in range(len(self.body)-1, 0, -1):
					self.body[i].update_track((self.body[i].rect.x, self.body[i].rect.y), self.track_limite)
					self.body[i].update_position(self.body[i-1].track[0])
			self.body[0].update_track((self.body[0].rect.x, self.body[0].rect.y), self.track_limite)
			self.body[0].update_position(self.track[0])
	
	def new(self):
		body_length = len(self.body)
		last_block = body_length - 1
		if body_length > 0:
			next_block = len(self.body) - 1
			block = SnakeBodyBlock(self.body[next_block].track[0], (self.rect.w, self.rect.h), self.color, self.radius)
			self.body.append(block)
		else:
			block = SnakeBodyBlock(self.track[0], (self.rect.w, self.rect.h), self.color, self.radius)
			self.body.append(block)
		self.body[len(self.body)-1].add(self.groups())
	
	def update_track(self, position, limite):
		self.track.append(position)
		if len(self.track) > limite:
			del(self.track[0])
	
	def update_position(self, position):
		self.rect.x = position[X]
		self.rect.y = position[Y]
	
	def reset(self):
		for sprite in self.body:
			sprite.kill()
		del(self.body)
		self.body = []
		self.rect = self.start_rect.copy()
		self.direction = self.start_direction
	
	def has_blocks_colliding(self):
		if len(self.body) > 1:
			for block in range(1, len(self.body)-1, 1):
				if pygame.sprite.collide_rect(self, self.body[block]):
					return True
		return False


class SnakeBodyBlock(pygame.sprite.Sprite):
	
	def __init__(self, position, size, color, radius):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface(size)
		self.image = self.image.convert()
		pygame.draw.circle(self.image, color, (radius, radius), radius)
		self.rect = pygame.Rect(position, size)
		self.track = []
	
	def update_track(self, position, limite):
		self.track.append(position)
		if len(self.track) > limite:
			del(self.track[0])
	
	def update_position(self, position):
		self.rect.x = position[X]
		self.rect.y = position[Y]


class Fruit(pygame.sprite.Sprite):
	
	def __init__(self, position, size, color, limite, radius):
		pygame.sprite.Sprite.__init__(self)
		self.color = color
		self.radius = radius
		self.image = pygame.Surface(size)
		self.image = self.image.convert()
		pygame.draw.circle(self.image, self.color, (radius, radius), radius)
		self.rect = pygame.Rect(position, size)
		x_limite = limite[X] - size[X] + 1
		y_limite = limite[Y] - size[Y] + 1
		self.limite = (x_limite, y_limite)
	
	def new(self):
		self.rect.x = random.randrange(self.limite[X]) // self.rect.w * self.rect.w
		self.rect.y = random.randrange(self.limite[Y]) // self.rect.h * self.rect.h


class Background(pygame.sprite.Sprite):
	
	def __init__(self, size, color):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface(size)
		self.image = self.image.convert()
		self.image.fill(color)
		self.rect = ((0, 0), size)


def main():
	game = Game("Snake Game", 600, 600)
	game.run()

if __name__ == "__main__": main()
