from snaketron.AIs.ai1 import SnakeTronAI1
from snaketron import snaketron

class SnakeTronAI2():
    """ An object of this class is to be passed to a SnakeTron contstructor.
    The SnakeTron object will call the update method of this class after every
    frame update.
    This is a more complex AI that looks a few moves ahead to see if any of those lead
    to death or victory and takes the best one. If there is a tie, it is decided by
    the applying the logic of AI1 to the tied choices.
    If none do, AI2 makes the same move as AI1.
    """
    def __init__(self):
        self.ai1 = SnakeTronAI1()
        pass

    def _one_step(self, dims, mysnake, opsnake, pip, last_pip):


    def update(self, dims, mysnake, opsnake, pip, last_pip):



