""" Dmitriy's first attempt at classic Snake using Pygame"""
import os
import sys
import pygame
from collections import deque
from pygame.locals import *
from random import randint
pygame.init()

block_size = 20
blocksx = 30
blocksy = 30
screen_size = (blocksx*block_size, blocksy*block_size)
backround = (0, 0, 0 , 1)

def paint_block(screen, loc, color):
    """paints block at location (loc, 2tuple) a color (color, pygame.Color)"""
    x0 = loc[0]*block_size
    y0 = loc[1]*block_size
    block = pygame.Rect((x0, y0), (block_size, block_size))
    pygame.draw.rect(screen, color, block)   

class Pip():
    """Implements the pip"""

    def __init__(self, snake, init_loc=None, c=pygame.Color(0, 0, 255, 1)):
        """initializes color and position"""
        self.relocate(snake, init_loc)
        self.color = c

    def location(self):
        return self.loc

    def paint(self, screen):
        """paints pip on the screen"""
        paint_block(screen, self.loc, self.color)

    def relocate(self, snake=None, loc=None):
        """ If snake object is passed and loc is None, then pip is relocated
        to a random position that is not overlapping with the snake body. If 
        no snake is given, pip is placed randomly without checking for overlap.
        If a location is passed then the pip is placed there regardless of snake
        """

        if loc == None:
            self.loc = (randint(0, blocksx-1), randint(0, blocksy-1))
            if snake != None:
                while snake.is_present(self.loc):
                    self.loc = (randint(0, blocksx-1), randint(0, blocksy-1))
        else:
            self.loc = loc

class Snake():
    """Implements the snake by drawing rectangles on canvas"""

    def __init__(self, 
                 init_loc=(15, 15),
                 init_dir= 'left', 
                 init_len=3, 
                 head_color=pygame.Color(255, 0, 0, 1),
                 body_color=pygame.Color(0, 255, 0, 1)):
        """Initialize snake object.

        Inputs: 
        init_loc - initial location of snake. Top left corner is (0,0)
        init_dir - initial direction of snake motion
        init_len - initial length of snake
        head_color - color of snakes head
        body_color - color of snakes body
        """
        self.direc = init_dir
        self.length = init_len
        self.head_color = head_color
        self.body_color = body_color
        
        #queue containing all current locations of snake
        if init_dir == 'left':
            self.body = deque([(init_loc[0] + x, init_loc[1]) 
                        for x in range(init_len)])
        if init_dir == 'right':
            self.body = deque([(init_loc[0] - x, init_loc[1]) 
                        for x in range(init_len)])
        if init_dir == 'up':
            self.body = deque([(init_loc[0], init_loc[1] + x) 
                        for x in range(init_len)])
        if init_dir == 'down':
            self.body = deque([(init_loc[0], init_loc[1] - x) 
                        for x in range(init_len)])
    
    def paint(self, screen, bgr= pygame.Color(0, 0, 0, 1)):
        """Paint the snake object on the backround.
        
        Inputs:
        screen - pygame display object
        bgr - background color, default black
        """

        for i, block in enumerate(self.body):
            if i == 0:
                paint_block(screen, block, self.head_color)
            else:        
                paint_block(screen, block, self.body_color)
    
    def is_present(self, loc):
        """checks if location loc is on top of the snake"""
        if loc in self.body:
            return True
        else:
            return False

    def set_direction(self, direc):
        if (self.direc == "left" and direc == "right"
        or  self.direc == "right" and direc == "left"
        or  self.direc == "up" and direc == "down"
        or  self.direc == "down" and direc == "up"):
            return

        self.direc = direc

    def move(self, pip):
        """Moves the head in the appropriate direction."""  
        
        if self.direc == "left":
            nhead = (self.body[0][0] - 1, self.body[0][1])
        if self.direc == "right":
            nhead = (self.body[0][0] + 1, self.body[0][1])
        if self.direc == "up":
            nhead = (self.body[0][0], self.body[0][1] - 1)
        if self.direc == "down":
            nhead = (self.body[0][0], self.body[0][1] + 1)

        #check if dead
        if (nhead[0] in (-1, blocksx + 1) 
        or nhead[1] in (-1, blocksy + 1)
        or nhead in self.body):
            return -1 #indicates that you're dead

        self.body.appendleft(nhead)

        if nhead == pip.location():
            pip.relocate(self)
            #potentially increase score
        else:
            self.body.pop()



def main():
    screen = pygame.display.set_mode(screen_size)
    s = Snake()
    p = Pip(s)
    pygame.time.set_timer(pygame.USEREVENT, 100)

    while True:
        event = pygame.event.poll()
        updateFlag = False
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.KEYDOWN:
            updateFlag = True
            if event.unicode == "a":
                s.set_direction("left")
            if event.unicode == "d":
                s.set_direction("right")
            if event.unicode == "w":
                s.set_direction("up")
            if event.unicode == "s":
                s.set_direction("down")
        if event.type == pygame.USEREVENT:
            updateFlag = True
        if updateFlag:
            screen.fill(backround) #may cause flicker
            status = s.move(p)
            s.paint(screen)
            p.paint(screen)
            pygame.display.update()
            if status == -1:
                sys.exit()

if __name__ == '__main__':
    main()