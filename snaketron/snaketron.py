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

def paint_block(screen, loc, color):
    """paints block at location (loc, 2tuple) a color (color, pygame.Color)"""
    x0 = loc[0]*block_size
    y0 = loc[1]*block_size
    block = pygame.Rect((x0, y0), (block_size, block_size))
    pygame.draw.rect(screen, color, block)

def copy_gamestate(gamestate):
    return {k: gamestate[k][:] for k in gamestate}

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
        self.gamestate = GameStep.reset()
        self.s1_dir = 'right'
        self.s2_dir = 'left'
        pygame.display.set_caption("SnakeTron")

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
                Snake.paint(self.gamestate, 1, self.screen)
                Snake.paint(self.gamestate, 2, self.screen)
                Pip.paint(self.gamestate, self.screen)
                win = GameStep.update(self.gamestate, self.s1_dir, self.s2_dir)
                pygame.display.update()
                if win != None:
                    return win
                if self.p1 != 'human':
                    self.s1_dir = self.p1.update(copy_gamestate(self.gamestate), 1)
                if self.p2 != 'human':
                    self.s2_dir = self.p2.update(copy_gamestate(self.gamestate), 2)

    def human_input(self, key):
        """Takes a pressed key and updates snake direction"""
        if self.p1 == 'human':
            if key == K_a:
                self.s1_dir = 'left'
            elif key == K_d:
                self.s1_dir = 'right'
            elif key == K_w:
                self.s1_dir = 'up'
            elif key == K_s:
                self.s1_dir = 'down'
        if self.p2 == 'human':
            if key == K_UP:
                self.s2_dir = 'up'
            elif key == K_LEFT:
                self.s2_dir = 'left'
            elif key == K_RIGHT:
                self.s2_dir = 'right'
            elif key == K_DOWN:
                self.s2_dir = 'down'

# Full state of the game should be represented in a single dict
class GameStep():
    """
    Compute one step of the game (or reset to step 1).
    """

    @staticmethod
    def reset():
        """
        Get a new gamestate with starting config.
        """
        gamestate = {
            'dims': [(blocksx, blocksy)],
            'pip': [('replaced in Pip.recet')],
            'last_pip': [(1,)]

        }
        Snake.reset(gamestate, 1)
        Snake.reset(gamestate, 2)
        Pip.reset(gamestate)
        return gamestate

    @staticmethod
    def update(gamestate, s1dir, s2dir):
        Snake.set_direction(gamestate, 1, s1dir)
        Snake.set_direction(gamestate, 2, s2dir)
        Snake.move(gamestate, 1)
        Snake.move(gamestate, 2)
        return GameStep.check_collisions(gamestate)

    @staticmethod
    def check_collisions(gamestate):
        """check updated snake body queues for collision with pip or enemy
        snake. If pip is found, this method relocates it. If collision, return
        the winning snake. Otherwise, return None. Last snake to get the pip
        gets priority in head to head collisions and simultaneous head-tail
        collisions.
        """
        pip = gamestate['pip'][0]
        last_pip = gamestate['last_pip'][0][0]
        s1_body = gamestate[(1, 'body')]
        s2_body = gamestate[(2, 'body')]
        if last_pip == 1:
            if Snake.is_present(gamestate, 1, s2_body[0]):
                return 1
            if Snake.is_present(gamestate, 2, s1_body[0]):
                return 2
        else:
            if Snake.is_present(gamestate, 2, s1_body[0]):
                return 2
            if Snake.is_present(gamestate, 1, s2_body[0]):
                return 1

        if s1_body[0] == pip:
                Pip.relocate(gamestate)
                gamestate['last_pip'] = [(1,)]
        if s2_body[0] == pip:
                Pip.relocate(gamestate)
                gamestate['last_pip'] = [(2,)]

class Pip():
    """Implements the pip"""

    @staticmethod
    def reset(gamestate):
        """initializes color and position"""
        Pip.relocate(gamestate)

    @staticmethod
    def location(gamestate):
        return gamestate['pip'][0]

    @staticmethod
    def paint(gamestate, screen):
        """paints pip on the screen"""
        c = pygame.Color(0, 0, 255, 1)
        paint_block(screen, gamestate['pip'][0], c)

    @staticmethod
    def relocate(gamestate):
        """Randomly places a pip at a location not occupied by either snake
        """
        loc = (randint(0, blocksx-1), randint(0, blocksy-1))
        while Snake.is_present(gamestate, 1, loc) or Snake.is_present(gamestate, 2, loc):
            loc = (randint(0, blocksx-1), randint(0, blocksy-1))
        gamestate['pip'][0] = loc

class Snake():
    """Implements the snake by drawing rectangles on canvas"""

    @staticmethod
    def reset(gamestate, sid, init_len=10):
        if sid == 1:
            init_dir = 'right'
            init_loc = (10, 10)
        if sid == 2:
            init_dir = 'left'
            init_loc = (20, 20)

        if init_dir == 'left':
            body =      [(init_loc[0] + x, init_loc[1])
                        for x in range(init_len)]
        if init_dir == 'right':
            body = [(init_loc[0] - x, init_loc[1])
                        for x in range(init_len)]
        if init_dir == 'up':
            body = [(init_loc[0], init_loc[1] + x)
                        for x in range(init_len)]
        if init_dir == 'down':
            body =      [(init_loc[0], init_loc[1] - x)
                        for x in range(init_len)]

        gamestate[(sid, 'direction')] = init_dir
        gamestate[(sid, 'next_direction')] = init_dir
        gamestate[(sid, 'body')] = body



    @staticmethod
    def paint(gamestate, sid, screen, bgr=pygame.Color(0, 0, 0, 1)):
        """Paint the snake object on the backround.

        Inputs:
        screen - pygame display object
        bgr - background color, default black
        """
        body = gamestate[(sid, 'body')]
        if gamestate['last_pip'][0][0] == sid:
            head_color = pygame.Color(255, 255, 0)
        else:
            head_color = pygame.Color(255, 255, 255)
        if sid == 1:
            body_color=pygame.Color(255, 0, 0, 1)
        if sid == 2:
            body_color=pygame.Color(0, 255, 0, 1)

        for i, block in enumerate(body):
            if i == 0:
                paint_block(screen, block, head_color)
            else:
                paint_block(screen, block, body_color)

    @staticmethod
    def is_present(gamestate, sid, loc):
        """checks if location loc is on top of the snake"""
        body = gamestate[(sid, 'body')]
        if loc in body:
            return True
        else:
            return False

    @staticmethod
    def set_direction(gamestate, sid, direc):
        if not direc in ['left', 'right', 'up', 'down']:
            return
        curr_direc = gamestate[(sid, 'direction')]
        if (curr_direc == 'left' and direc == 'right'
        or  curr_direc == 'right' and direc == 'left'
        or  curr_direc == 'up' and direc == 'down'
        or  curr_direc == 'down' and direc == 'up'):
            return
        gamestate[(sid, 'next_direction')] = [(direc,)]

    @staticmethod
    def get_direction(gamestate, sid):
        return gamestate[(sid, 'direction')][0][0]

    @staticmethod
    def move(gamestate, sid):
        """Moves the head in the appropriate direction. Now only checks if
        encountered pip and extends. Does not move pip or check for collisions.
        """
        gamestate[(sid, 'direction')] = gamestate[(sid, 'next_direction')]
        direc = gamestate[(sid, 'direction')][0][0]
        body = gamestate[(sid, 'body')]
        pip = gamestate['pip'][0]
        if direc == 'left':
            nhead = (body[0][0] - 1, body[0][1])
        if direc == 'right':
            nhead = (body[0][0] + 1, body[0][1])
        if direc == 'up':
            nhead = (body[0][0], body[0][1] - 1)
        if direc == 'down':
            nhead = (body[0][0], body[0][1] + 1)

        nhead = ((nhead[0] + blocksx)%blocksx, (nhead[1] + blocksy)%blocksy)

        #check if overlapping self
        if nhead in body:
            #truncate tail
            val = body.pop()
            while val != nhead:
                val = body.pop()

        body.insert(0, nhead)
        if nhead == pip:
            return
        body.pop()


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
