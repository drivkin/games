""" Adversarial variation on snake. The rules are as follows:
2 players, one using wasd and the other using the arrow keys, each have a snake.
When a snake eats a pip, it gets longer. You win by making your opponent crash
into your snake or the wall. If you crash into your own snake, you lose your 
tail behind the crash point. If snake heads collide, the last snake to have
consumed a pip wins.

Also known as snaketron.
"""
import os
import sys
import pygame
from collections import deque
from pygame.locals import *
from random import randint
pygame.init()

LOSE = -1
GOTPIP = 1
block_size = 20
blocksx = 31
blocksy = 31
screen_size = (blocksx*block_size, blocksy*block_size)
backround = (0, 0, 0, 1)

class SnakeTron():
    """Wrapper class for snaketron game. Contains the screen, the snakes and 
    pip, screen display, and the interface for human players. When created, the
    SnakeTron object may be passed 0, 1, or 2 AI player objects. After every
    frame update, the AI objects update method will be called as follows:

    update(field_dims, Snake own_snake, Snake enemy_snake, Pip pip, last_pip)
    
    which must return one of four values: 'left', 'right', 'up', 'down'. Any 
    other input will be ignored. The heading of the snake at the next frame
    update will be set accordingly. AIs should not modify any of the objects
    because that would be cheating. 
    """

    def __init__(self, p1='human', p2='human'):
        """Initializes 2 Snakes, 1 pip, and the field and screen.
        """
        self.p1 = p1
        self.p2 = p2
        self.display = True
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption("SnakeTron") 
        self.dims = (blocksx, blocksy)
        self.s1 = Snake(init_loc=(10, 10), init_dir="right", 
            body_color=pygame.Color(255, 0, 0, 1))
        self.s2 = Snake(init_loc=(20, 20), init_dir="left",
            body_color=pygame.Color(0, 255, 0, 1))
        self.pip = Pip(self.s1, self.s2)
        self.last_pip = 1

    def play(self, per=100):
        """Basically the main method that runs the game. per is time between 
        moves in ms. return 1 if snake 1 won, 2 if snake 2 won.
        """
        pygame.time.set_timer(pygame.USEREVENT, 100)
        pygame.display.update()
        while True:
            # events = pygame.event.get()
            event = pygame.event.poll()
            # for event in events:
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN: self.human_input(event.key)
            if event.type == pygame.USEREVENT:
                self.screen.fill(backround)
                self.s1.move(self.pip)
                self.s2.move(self.pip)
                win = self.check_collisions()
                self.s1.paint(self.screen)
                self.s2.paint(self.screen)
                self.pip.paint(self.screen)
                pygame.display.update()
                if win != None:
                    return win
                if self.p1 != 'human':
                    m1 = self.p1.update(self.dims, self.s1, self.s2, self.pip, 
                        self.last_pip == 1)
                if self.p2 != 'human':
                    m2 = self.p2.update(self.dims, self.s2, self.s1, self.pip, 
                        self.last_pip == 2)
                if self.p1 != 'human':
                    self.s1.set_direction(m1)
                if self.p2 != 'human':
                    self.s2.set_direction(m2)
    
    def check_collisions(self):
        """check updated snake body queues for collision with pip or enemy
        snake. If pip is found, this method relocates it. If collision, return
        the winning snake. Otherwise, return None. Last snake to get the pip
        gets priority in head to head collisions and simultaneous head-tail 
        collisions.
        """
        if self.last_pip == 1:
            if self.s1.is_present(self.s2.body[0]):
                return 1
            if self.s2.is_present(self.s1.body[0]):
                return 2
        else:
            if self.s2.is_present(self.s1.body[0]):
                return 2
            if self.s1.is_present(self.s2.body[0]):
                return 1
            
        if self.s1.body[0] == self.pip.location():
                self.pip.relocate(self.s1, self.s2)
                self.s1.set_head_color('yellow')
                self.s2.set_head_color('white')
                self.last_pip = 1
        if self.s2.body[0] == self.pip.location():
                self.pip.relocate(self.s1, self.s2)
                self.s2.set_head_color('yellow')
                self.s1.set_head_color('white')
                self.last_pip = 2
        return None


    def human_input(self, key):
        """Takes a pressed key and updates snake direction"""
        if self.p1 == 'human':
            if key == K_a:
                self.s1.set_direction('left')
            elif key == K_d:
                self.s1.set_direction('right')
            elif key == K_w:
                self.s1.set_direction('up')    
            elif key == K_s:
                self.s1.set_direction('down')
        if self.p2 == 'human':
            if key == K_UP:
                self.s2.set_direction('up')
            elif key == K_LEFT:
                self.s2.set_direction('left')
            elif key == K_RIGHT:
                self.s2.set_direction('right')
            elif key == K_DOWN:
                self.s2.set_direction('down')

def paint_block(screen, loc, color):
    """paints block at location (loc, 2tuple) a color (color, pygame.Color)"""
    x0 = loc[0]*block_size
    y0 = loc[1]*block_size
    block = pygame.Rect((x0, y0), (block_size, block_size))
    pygame.draw.rect(screen, color, block)   

class Pip():
    """Implements the pip"""

    def __init__(self, s1, s2, c=pygame.Color(0, 0, 255, 1)):
        """initializes color and position"""
        self.relocate(s1, s2)
        self.color = c

    def location(self):
        return self.loc

    def paint(self, screen):
        """paints pip on the screen"""
        paint_block(screen, self.loc, self.color)

    def relocate(self, s1, s2):
        """Randomly places a pip at a location not occupied by either snake
        """
        self.loc = (randint(0, blocksx-1), randint(0, blocksy-1))
        while s1.is_present(self.loc) or s2.is_present(self.loc):
            self.loc = (randint(0, blocksx-1), randint(0, blocksy-1))
        
class Snake():
    """Implements the snake by drawing rectangles on canvas"""

    def __init__(self, 
                 init_loc=(15, 15),
                 init_dir= 'left', 
                 init_len=10, 
                 head_color=pygame.Color(255, 255, 255, 1),
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
        self.next_direc = init_dir
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
    
    def set_head_color(self, c='white'):
        """sets head color to "white" or "yellow" """
        if c == 'white':
            self.head_color = pygame.Color(255, 255, 255)
        elif c == 'yellow':
            self.head_color = pygame.Color(255, 255, 0)

    def paint(self, screen, bgr=pygame.Color(0, 0, 0, 1)):
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
        if not direc in ['left', 'right', 'up', 'down']:
            return
        if (self.direc == 'left' and direc == 'right'
        or  self.direc == 'right' and direc == 'left'
        or  self.direc == 'up' and direc == 'down'
        or  self.direc == 'down' and direc == 'up'):
            return
        self.next_direc = direc

    def move(self, pip):
        """Moves the head in the appropriate direction. Now only checks if 
        encountered pip and extends. Does not move pip or check for collisions.
        """  
        self.direc = self.next_direc
        if self.direc == 'left':
            nhead = (self.body[0][0] - 1, self.body[0][1])
        if self.direc == 'right':
            nhead = (self.body[0][0] + 1, self.body[0][1])
        if self.direc == 'up':
            nhead = (self.body[0][0], self.body[0][1] - 1)
        if self.direc == 'down':
            nhead = (self.body[0][0], self.body[0][1] + 1)

        nhead = ((nhead[0] + blocksx)%blocksx, (nhead[1] + blocksy)%blocksy)
     
        #check if overlapping self
        if nhead in self.body:
            #truncate tail
            val = self.body.pop()
            while val != nhead:
                val = self.body.pop()

        self.body.appendleft(nhead)
        if nhead == pip.location():
            return 
        self.body.pop()
         

red_win_count = 0
green_win_count = 0
def win_message(screen, winner):
    global red_win_count
    global green_win_count
    font = pygame.font.Font(None, 36)
    msg = " Snake Wins!!!"
    if winner == 1:
        red_win_count += 1
        text = font.render("Red" + msg + " Red: " + str(red_win_count)
                + " Green: " + str(green_win_count), 1, (255, 255, 255))
    else:
        green_win_count += 1
        text = font.render("Green" + msg + " Red: " + str(red_win_count)
                + " Green: " + str(green_win_count), 1, (255, 255, 255))

    textpos = text.get_rect(centerx=screen.get_width()/2)
    screen.blit(text, textpos)
    text2 = font.render("Press Enter to reset",1,(255,255,255))
    textpos2 = text2.get_rect(centerx = screen.get_width()/2,
                              centery = textpos.bottom + 20)
    screen.blit(text2, textpos2)
    pygame.display.update()

def play_ai(ai1, ai2='human'):
    while True:
        game = SnakeTron(ai1, ai2)
        winner = game.play()
        win_message(game.screen, winner)        
        while True:
            event = pygame.event.poll()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                break
            if event.type == pygame.QUIT: sys.exit()

def play():
    while True:
        game = SnakeTron()
        winner = game.play()
        win_message(game.screen, winner)        
        while True:
            event = pygame.event.poll()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                break
            if event.type == pygame.QUIT: sys.exit()

if __name__ == '__main__':
    play()
