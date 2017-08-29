"""Dmitriy's first attempt at an adversnake ai
"""
from adversnake import adversnake

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

def dd_nearest(dims, head, pips, direc):
    """returns the distance to the nearest pip of a move in direction d. 
    pips is an array of position tuples, not Pip objects"""
    hx, hy = head
    if len(pips)==0:
        return 0
    if direc == 'left':
        return min([distance(dims, ((hx - 1 + dims[0])%dims[0], hy), pip)
                    for pip in pips])
    elif direc == 'right':
        return min([distance(dims, ((hx + 1)%dims[0], hy), pip)
                    for pip in pips])
    elif direc == 'up':
        return min([distance(dims, (hx, (hy - 1 + dims[1])%dims[1]), pip)
                    for pip in pips])
    elif direc == 'down':
        return min([distance(dims, (hx,(hy + 1)%dims[1]), pip)
                    for pip in pips])
    return None    

class AdverSnakeAI1():
    """ An object of this class is to be passed to a AdverSnake contstructor.
    The AdverSnake object will call the update method of this class after every
    frame update.
    This is a basic ai which follows two rules: go to the nearest pip and avoid the 
    other snake. It will always make the move that will bring it closest to a 
    pip as long as that move doesn't cause it collide with the enemy or itself. 
    """
    def __init__(self):
        pass

    def update(self, dims, mysnake, opsnake, pips, last_pip):
        """output 'left', 'right', 'up', or 'down' command to snake. 
        
        Inputs:
        dims - (x,y) field dimensions
        mysnake - own Snake object (Snake class defined in AdverSnake module)
        opnake - opposing Snake object
        pips - lisf of Pip objects (Pip class defined in AdverSnake module)
        last_pip - True if your snake had the last pip, False otherwise
        """
        myhead = mysnake.body[0]
        pl = [pip.location() for pip in pips]
        mydir = mysnake.direc
        outcom = mydir
        if mydir == 'left':
            dirs = ['left', 'up', 'down']
        if mydir == 'right':
            dirs = ['right', 'down', 'up']
        if mydir == 'up':
            dirs = ['up', 'left', 'right']
        if mydir == 'down':
            dirs = ['down', 'right', 'left']
        
        #a penalty for each direction is computed, and the one with the lowest
        #penalty wins
        d = [dd_nearest(dims, myhead, pl, x) for x in dirs]
        hit_self = [mysnake.is_present(move_to(dims, myhead, x)) for x in dirs]
        hit_op = [opsnake.is_present(move_to(dims, myhead, x)) for x in dirs]
        doh = [not last_pip
               and dd_nearest(dims, myhead, [opsnake.body[0]], x) <3
               for x in dirs]


        k_d = 1
        k_hit_self = 10
        k_hit_op = 1000
        k_doh = 100
        cost = [k_d*w + k_hit_self*x + k_hit_op*y + k_doh*z for w, x, y, z
                in zip(d, hit_self, hit_op, doh)]
        return min(zip(cost, dirs))[1]

def play():
    ai1 = AdverSnakeAI1()
    ai2 = AdverSnakeAI1()
    adversnake.play_ai(ai1)

if __name__ == '__main__':
    print "play adversnake against ai"
    play()

