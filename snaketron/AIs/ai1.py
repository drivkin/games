"""Dmitriy's first attempt at a SnakeTron ai
"""
from snaketron.snaketron import play_ai, Snake

def distance(dims, p1, p2):
    """determines the distance between two points on a wrapping field dimensions
    dims. Distance is defined as the minimum number of steps between p1 and p2
    if only vertical or horizontal steps are allowed.
    """
    hdx = dims[0]/2
    hdy = dims[1]/2
    xd = abs(p1[0] - p2[0])#%hdx
    yd = abs(p1[1] - p2[1])#%hdy
    #wrapping around produces cyclical behavior. Ideally, some method should be
    #developped to avoid this while still having the snake be smart enough to
    #go through walls when it needs to, but for now just don't wrap distance
    # if xd > hdx:
    #     xd = xd - hdx
    # if yd > hdy:
    #     yd = yd - hdy
    return xd + yd

def move_to(dims, p, direc):
    """helper function to compute the location of a move in direc from p
    """
    hx, hy = p
    if direc == 'left':
        return ((hx - 1 + dims[0])%dims[0], hy)
    elif direc == 'right':
        return ((hx + 1)%dims[0], hy)
    elif direc == 'up':
        return (hx, (hy - 1 + dims[1])%dims[1])
    elif direc == 'down':
        return (hx,(hy + 1)%dims[1])
    return None

def direction_distance(dims, head, pip, direc):
    """ computes distance between head and pip if the head is to move along
    direction direc
    """
    hx, hy = head
    if direc == 'left':
        return distance(dims, ((hx - 1 + dims[0])%dims[0], hy), pip)
    elif direc == 'right':
        return distance(dims, ((hx + 1)%dims[0], hy), pip)
    elif direc == 'up':
        return distance(dims, (hx, (hy - 1 + dims[1])%dims[1]), pip)
    elif direc == 'down':
        return distance(dims, (hx,(hy + 1)%dims[1]), pip)
    return None

def nearest_direction(dims, head, pip, dirs):
    """of the directions listed in dirs, compute the one along which a move of
    the head would put it closest to the pip, return (distance, direction)
    """
    return min([(direction_distance(dims, head, pip, x), x) for x in dirs])


class SnakeTronAI1():
    """ An object of this class is to be passed to a SnakeTron contstructor.
    The SnakeTron object will call the update method of this class after every
    frame update.
    This is a basic ai which follows two rules: go to the pip and avoid the
    other snake. It will always make the move that will bring it closest to the
    pip as long as that move doesn't cause it collide with the enemy.
    """
    def __init__(self):
        self.dirs = ['left', 'right', 'up', 'down']
        # directions opposite each direction
        self.dir_ops = {'left': 'right',
                        'right': 'left',
                        'up': 'down',
                        'down': 'up'}

    def update(self, gamestate, snake_id):
        """output 'left', 'right', 'up', or 'down' command to snake.

        Inputs:
        dims - (x,y) field dimensions
        mysnake - own Snake object (Snake class defined in snaketron module)
        opnake - opposing Snake object
        pip - Pip object (Pip class defined in snketron module)
        last_pip - True if your snake had the last pip, False otherwise
        """
        if snake_id == 1:
            mysnake = 1
            opsnake = 2
        else:
            mysnake = 2
            opsnake = 1
        dims = gamestate['dims'][0]
        pip = gamestate['pip'][0]
        last_pip = gamestate['last_pip'][0][0] == snake_id


        myhead = gamestate[(mysnake, 'body')][0]
        ophead = gamestate[(opsnake, 'body')][0]
        pl = pip
        mydir = gamestate[(snake_id, 'direction')][0][0]
        dirs = list(set(self.dirs) - set([self.dir_ops[mydir]]))

        #a penalty for each direction is computed, and the one with the lowest
        #penalty wins
        d = [direction_distance(dims, myhead, pl, x) for x in dirs]
        hit_self = [Snake.is_present(gamestate, mysnake, move_to(dims, myhead, x)) for x in dirs]
        hit_op = [Snake.is_present(gamestate, opsnake, move_to(dims, myhead, x)) for x in dirs]
        doh = [not last_pip
               and direction_distance(dims, myhead, ophead, x) <3
               for x in dirs]


        k_d = 1
        k_hit_self = 10
        k_hit_op = 1000
        k_doh = 100
        cost = [k_d*w + k_hit_self*x + k_hit_op*y + k_doh*z for w, x, y, z
                in zip(d, hit_self, hit_op, doh)]
        return min(zip(cost, dirs))[1]

def play():
    ai1 = SnakeTronAI1()
    #ai2 = SnakeTronAI1()
    play_ai(ai1)

if __name__ == '__main__':
    print "play snaketron against ai"
    play()

