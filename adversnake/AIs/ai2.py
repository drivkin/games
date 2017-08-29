"""First attempt an ai that looks ahead. Only intended to work with one pip at a time.
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

def move_to(p, direc):
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

class AdverSnakeAI2():
    """ An object of this class is to be passed to a AdverSnake contstructor.
    The AdverSnake object will call the update method of this class after every
    frame update.
    """
    def __init__(self, lookahead=4, max_snake_len=50):
        """lookahead is how many steps to look ahead"""
        self.lookahead = lookahead
        self.max_snake_len = max_snake_len 

    def update(self, fdims, mysnake, opsnake, pips, last_pip):
        """output 'left', 'right', 'up', or 'down' command to snake. 
                
        Inputs:
        dims - (x,y) field dimensions
        mysnake - own Snake object (Snake class defined in AdverSnake module)
        opnake - opposing Snake object
        pips - lisf of Pip objects (Pip class defined in AdverSnake module)
        last_pip - True if your snake had the last pip, False otherwise
        """
        global dims
        dims = fdims
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

def index(v, l):
    """returns index of first occurance of v in l, or -1 none found
    """
    try:
        return l.index(v)
    except ValueError:
        return -1

class State():
    """class containing the two snakes and the pip locations. Everything is a list of tuples. Upon creation, collisions should not have been resolved (this will be done by the workhorse reward() method).
    """
    def __init__(self, mysnake, opsnake, pips, last_pip):
        self.mysnake = mysnake
        self.opsnake = opsnake
        self.pips = pips
        self.last_pip = last_pip
    
    def reward(self):
        """computes the reward associated with being in the current state. 
        In the process of doing so, also handles collisions by appropriately
        modifying the snakes.
        """
        k_dpip = -1 #reward per distance to pip
        k_opdpip = 1 # reward for opponent distance to pip
        k_gotpip = 100 #reward for getting a pip
        k_opgotpip = -100 #reward for opponent getting pip
        #rewards for crashing or making opponent crash are based on how many 
        #pips you or they lose

        dist = min([distance(self.mysnake[0], p) for p in self.pips])
        opdist = min([distance(self.opsnake[0], p) for p in self.pips])
        gotpip = False
        opgotpip = False
        myloss = 0
        oploss = 0
        eval_done = False #used to signify to skip rest of collision checking
        if self.last_pip:
            gotpip = self.mysnake[0] in pips
            if self.mysnake[0] != self.opsnake[0]:
                opgotpip = self.opsnake[0] in pips
            else:
                oploss = len(self.opsnake) - 1
                self.opsnake = self.opsnake[0]
                eval_done = True
        else:
            opgotpip = self.opsnake[0] in pips
            if self.mysnake[0] != self.opsnake[0]:
                gotpip = self.mysnake[0] in pips
            else:
                myloss = len(self.mysnake) - 1
                self.mysnake = self.mysnake[0]
                eval_done = True

        if not eval_done: #no head collisions
            idmy = index(self.mysnake[0], self.mysnake[1:])           
            if idmy != -1:
                myloss = len(self.mysnake) - idmy
            else:
                idmy = index(self.mysnake[0], self.opsnake) 
                if idmy != -1:
                    myloss = len(self.mysnake) - 1
            
            idop = index(self.opsnake[0], self.opsnake[1:])
            if idop != -1:
                oploss = len(self.opsnake) - idop
            else:
                idop = index(self.opsnake[0], self.mysnake[1:])
                if idop != -1:
                    oploss = l
            


        #head to head collision. Igoring the skip condition for now
        if self.mysnake[0] == self.opsnake[0]:
            if self.last_pip:
                oploss = len(self.opsnake) - 1
            else:
                myloss = len(self.mysnake) - 1
        elif self.last_pip:
            if self.opsnake[0] in self.mysnake:
                oploss = len(self.opsnake) - 1
                self.opsnake = self.opsnake[0] 
            else:
                try:
                    idx = self.opsnake[1:].index(self.opsnake[0])
                    oploss = len(self.opsnake) - idx
                    self.opsnake = self.opsnake[:idx]
                except ValueError:
                    pass


def play():
    ai1 = AdverSnakeAI2()
    ai2 = AdverSnakeAI2()
    adversnake.play_ai(ai1, ai2)

if __name__ == '__main__':
    print "play adversnake against ai"
    play()

