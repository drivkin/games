""" Variation on snake / snaketron. The person with longest tail at the end of the game wins. The game ends when all pips have been collected. Crashing into your own tail truncates it at the cut. Crashing into the adversary's tail truncates your tail entirely. The head of the last snake to have obtained a pip turns yellow, indicating that in the case of a head to head collision, that snake is the winner. Multiple pips may be in play, so if both snakes get a pip at the same time, the one that had last pip retains it. If both snakes are the same length when all pips are consumed, the last snake to get a pip wins. Tails are not removed until the next turn, i.e. if both snakes crash into their opponents tails at the same time, they will both lose their tails.
"""
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
pch = 50 #height of pip counter
backround = (0, 0, 0, 1)

class AdverSnake():
    """Wrapper class for adversnake game. Contains the screen, the snakes and 
    pip, screen display, and the interface for human players. When created, the
    AdverSnake object may be passed 0, 1, or 2 AI player objects. After every
    frame update, the AI objects update method will be called as follows:

    update(field_dims, Snake own_snake, Snake enemy_snake, [Pip pip], last_pip,
            pips_remaining)
    
    which must return one of four values: 'left', 'right', 'up', 'down'. Any 
    other input will be ignored. The heading of the snake at the next frame
    update will be set accordingly. AIs should not modify any of the objects
    because that would be cheating.

    note that in this variation, there may be more than one pip at a time.  
    """

    def __init__(self, p1='human', p2='human', pips_disp=1, pips_total=20, snake_len=3):
        """Initializes 2 Snakes, 1 pip, and the field and screen.
        """
        self.p1 = p1
        self.p2 = p2
        self.window = pygame.display.set_mode((screen_size[0], 
                                               screen_size[1] + pch))
        self.screen = pygame.Surface(screen_size)
        self.sr = self.screen.get_rect()
        self.pc = pygame.Surface((screen_size[0], pch))
        self.pcr = self.pc.get_rect(topleft=self.sr.bottomleft)
        self.font = pygame.font.Font(None, 30)
        pygame.display.set_caption("SnakeTron") 
        self.dims = (blocksx, blocksy)
        self.pips_disp = pips_disp
        self.s1 = Snake(init_loc=(10, 10), init_dir="right", 
            body_color=pygame.Color(255, 0, 0, 1), init_len=snake_len)
        self.s2 = Snake(init_loc=(20, 20), init_dir="left",
            body_color=pygame.Color(0, 255, 0, 1), init_len=snake_len)
        self.pips = []
        for p in range(pips_disp):
            self.pips.append(Pip(self))
        self.pips_remaining = pips_total
        self.last_pip = 1

    def play(self, per=100):
        """Basically the main method that runs the game. per is time between 
        moves in ms. return 1 if snake 1 won, 2 if snake 2 won.
        """
        pygame.time.set_timer(pygame.USEREVENT, 100)
        pygame.display.update()
        while True:
            event = pygame.event.poll()
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN: self.human_input(event.key)
            if event.type == pygame.USEREVENT:
                self.screen.fill(backround)
                self.s1.extend()
                self.s2.extend()
                self.check_collisions()
                self.s1.paint(self.screen)
                self.s2.paint(self.screen)
                for p in self.pips:
                    p.paint(self.screen)
                self.update_pip_display()
                self.paint_display()
                pygame.display.update()
                if self.pips_remaining <= 0:
                    return (len(self.s1.body), len(self.s2.body), self.last_pip)
                if self.p1 != 'human':
                    m1 = self.p1.update(self.dims, self.s1, self.s2, self.pips, 
                        self.last_pip == 1)
                if self.p2 != 'human':
                    m2 = self.p2.update(self.dims, self.s2, self.s1, self.pips, 
                        self.last_pip == 2)
                if self.p1 != 'human':
                    self.s1.set_direction(m1)
                if self.p2 != 'human':
                    self.s2.set_direction(m2)
    
    def snake_pip_collision(self, snake):
        try:
            pl = [p.location() for p in self.pips]
            idx = pl.index(snake.body[0])
            del self.pips[idx]
            self.pips_remaining -= 1
            return True
        except ValueError:
            return False

    def check_collisions(self):
        """This method, called after the snakes are extended, handles all 
        possible collisions.
        """
        s1hitophead = False
        s2hitophead = False
        s1pip = False
        s2pip = False
        s1hitop = False
        s2hitop = False
        s1hitself = False
        s2hitself = False
        #head to head collision
        if self.s1.body[0] == self.s2.body[0]:
            if self.last_pip == 1:
                s2hitop = True
            else:
                s1hitop = True

        #pip getting
        pl = [p.location() for p in self.pips]
        if self.s1.body[0] in pl and not s1hitop:
            s1pip = True
        if self.s2.body[0] in pl and not s2hitop:
            s2pip = True
        if s1pip:
            self.pips_remaining -= 1
            del self.pips[pl.index(self.s1.body[0])]
        elif not (s1hitop or s1hitself):
            self.s1.cut(self.s1.body[-1])
        if s2pip:
            self.pips_remaining -= 1
            del self.pips[pl.index(self.s2.body[0])]
        elif not (s2hitop or s2hitself):
            self.s2.cut(self.s2.body[-1])

        if not (s1pip and s2pip):
            if s1pip:
                self.last_pip = 1
            elif s2pip:
                self.last_pip = 2
        while (len(self.pips) < self.pips_disp 
            and len(self.pips) < self.pips_remaining): 
            self.pips.append(Pip(self))

        #head colors
        if self.last_pip == 1:
            self.s1.set_head_color('yellow')
            self.s2.set_head_color('white')
        else:
            self.s2.set_head_color('yellow')
            self.s1.set_head_color('white')

        #if the snakes come at each other head on, it is possible that the heads skip over each other. This case is handled here.
        skip_condition = False
        if self.s1.body[0][1] == self.s2.body[0][1]:
            if self.s1.direc == 'left' and self.s2.direc == 'right':
                if self.s1.body[0][0] == self.s2.body[0][0] - 1:
                    skip_condition = True
            elif self.s1.direc == 'right' and self.s2.direc == 'left':
                if self.s1.body[0][0] == self.s2.body[0][0] + 1:
                    skip_condition = True 
        elif self.s1.body[0][0] == self.s2.body[0][0]:
            if self.s1.direc == 'up' and self.s2.direc == 'down':
                if self.s1.body[0][1] == self.s2.body[0][1] - 1:
                    skip_condition == True
            elif self.s1.direc == 'down' and self.s2.direc == 'up':
                if self.s1.body[0][1] == self.s2.body[0][1] + 1:
                    skip_condition == True
        if skip_condition:
            if self.last_pip == 1:
                if len(self.s2.body) > 1:
                    self.s2.cut(self.s2.body[1])
                    return
            else:
                if len(self.s1.body) > 1:
                    self.s1.cut(self.s1.body[1])
                    return 

        #self hits
        if self.s1.body_present(self.s1.body[0]):
            s1hitself = True
        if self.s2.body_present(self.s2.body[0]):
            s2hitself = True
        #cut method only cuts at the first occurence of the location
        if s1hitself: 
            self.s1.cut(self.s1.body[0]) 
        if s2hitself:
            self.s2.cut(self.s2.body[0])

        #opponent body hits
        if self.s1.body_present(self.s2.body[0]):
            s2hitop = True
        if self.s2.body_present(self.s1.body[0]):
            s1hitop = True
        if s1hitop:
            if len(self.s1.body) > 1:
                self.s1.cut(self.s1.body[1])
        if s2hitop:
            if len(self.s2.body) > 1:
                self.s2.cut(self.s2.body[1])

        
    def update_pip_display(self):
        self.pc.fill((100, 100, 100))
        text = self.font.render("pips: " + str(self.pips_remaining), 1, 
                (0, 0, 0))
        tp = text.get_rect(centerx=screen_size[0]/2, centery=pch/2)
        self.pc.blit(text, tp)

    def paint_display(self):
        self.window.blit(self.screen, self.sr)
        self.window.blit(self.pc, self.pcr)

    def human_input(self, key):
        """Takes a pressed key and updates snake direction"""
        if self.p1 == 'human':
            if key == K_h:
                self.s1.set_direction('left')
            elif key == K_l:
                self.s1.set_direction('right')
            elif key == K_j:
                self.s1.set_direction('up')    
            elif key == K_k:
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

    def __init__(self, game, c=pygame.Color(0, 0, 255, 1)):
        """initializes color and position"""
        self.relocate(game)
        self.color = c

    def location(self):
        return self.loc

    def paint(self, screen):
        """paints pip on the screen"""
        paint_block(screen, self.loc, self.color)

    def relocate(self, game):
        """Randomly places a pip at a location not occupied by either snake or
        another pip. Takes an AdverSnake object so that it can have access to 
        the snakes and the pips.
        """
        self.loc = (randint(0, blocksx-1), randint(0, blocksy-1))
        other_pips = [p.location() for p in game.pips]
        while (game.s1.is_present(self.loc) 
               or game.s2.is_present(self.loc) 
               or self.loc in other_pips):
            self.loc = (randint(0, blocksx-1), randint(0, blocksy-1))
        
class Snake():
    """Implements the snake by drawing rectangles on canvas"""

    def __init__(self, 
                 init_loc=(15, 15),
                 init_dir= 'left', 
                 init_len=50, 
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

    def body_present(self, loc):
        """checks if location loc is present in body of snake (head excluded)
        """
        if loc in list(self.body)[1:]:
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

    def extend(self):
        """Extends the snake by moving the head in the appropriate direction.
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
        self.body.appendleft(nhead)
    
    def cut(self, loc):
        """Cuts of the tail at the given location. Note that loc is not the 
        location of the cut in the array, but rather the (x,y) coordinates
        of the cut point."""
        
        val = self.body.pop()
        while val != loc:
            val = self.body.pop()

red_win_count = 0
green_win_count = 0
def win_message(window, score):
    global red_win_count
    global green_win_count
    font = pygame.font.Font(None, 36)
    msg = 'Red: ' + str(score[0]) + ' Green: ' + str(score[1]) 
    if score[0] > score[1]:
        red_win_count += 1
        msg = msg + ' | Red Wins!'
        
    elif score[1] > score[0]:
        green_win_count += 1
        msg = msg + ' | Green Wins!'
    else:
        if score[2] == 1:
            red_win_count += 1
            msg = msg + ' | Red Wins!' 
        else:
            green_win_count += 1
            msg = msg + ' | Green Wins!'
    text = font.render(msg, 1, (255, 255, 255))
    textpos = text.get_rect(centerx=window.get_width()/2)
    window.blit(text, textpos)

    text2 = font.render('Score Count | Red: ' + str(red_win_count) 
                       +' Green: ' + str(green_win_count),1,(255,255,255))
    textpos2 = text2.get_rect(centerx = window.get_width()/2,
                              centery = textpos.bottom + 20)
    window.blit(text2, textpos2)
    pygame.display.update()

def play_ai(ai1, ai2='human'):
    while True:
        game = AdverSnake(ai1, ai2, snake_len=3)
        score = game.play()
        win_message(game.window, score)        
        while True:
            event = pygame.event.poll()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                break
            if event.type == pygame.QUIT: sys.exit()

def play():
    while True:
        game = AdverSnake()
        score = game.play()
        win_message(game.window, score)        
        while True:
            event = pygame.event.poll()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                break
            if event.type == pygame.QUIT: sys.exit()

if __name__ == '__main__':
    play()