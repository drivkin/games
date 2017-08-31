import pdb
from collections import defaultdict
from snaketron.AIs.ai1 import SnakeTronAI1
from snaketron import snaketron
from copy import deepcopy, copy

class SnakeTronAI2():
    """ An object of this class is to be passed to a SnakeTron contstructor.
    The SnakeTron object will call the update method of this class after every
    frame update.
    This is a more complex AI that looks a few moves ahead to see if any of those lead
    to death or victory and takes the best one. If there is a tie, it is decided by
    the applying the logic of AI1 to the tied choices.
    If none do, AI2 makes the same move as AI1.
    """
    dirs = set(['left', 'right', 'up', 'down'])
    # directions opposite each direction
    dir_ops = {'left': set(['right']),
               'right': set(['left']),
               'up': set(['down']),
               'down': set(['up'])}
    def __init__(self):
        self.ai1 = SnakeTronAI1()
        pass

    def _win_lose_recur(self, gamestate, this_move, max_moves):
        """
        Recursive brute force computation of wins/losses for each
        possible move.
        """
        s1allowed = self.dirs - self.dir_ops[gamestate.s1.get_direction()]
        s2allowed = self.dirs - self.dir_ops[gamestate.s2.get_direction()]
        moves = [(s1, s2) for s1 in s1allowed for s2 in s2allowed]
        out = {}
        for move in moves:
            gsnew = deepcopy(gamestate)
            win = gsnew.update(move[0], move[1])
            if win is not None or this_move == max_moves:
                out[move] = win
                # If a snake wins on this move, it wins on all future
                # moves as well. For each move, there are 3 x 3 = 9
                # different following moves. The following line scales
                # appropriately
                win_scale = 9 ** (max_moves - this_move)
                if win is not None:
                    if win == 1:
                        out[move] = (win_scale, 0)
                    else:
                        out[move] = (0, win_scale)
                else:
                    out[move] = (0, 0)
                continue
            out[move] = self._win_lose_recur(gsnew, this_move + 1, max_moves)
        return out

    def _parse_recur(self, subtree, snake_id):
        my_idx = snake_id - 1
        op_idx = 1 - my_idx
        if type(subtree) is tuple:
            return subtree[my_idx] - subtree[op_idx]
        return sum([self._parse_recur(subtree[k], snake_id) for k in subtree])


    def _move_quality(self, win_lose, snake_id):
        """
        Parse the output of _win_lose_recur to figure out which move
        is best for snake snake_id
        """
        # TODO: update interpreter and change to a lamba
        def return_0():
            return 0
        my_idx = snake_id - 1
        quality = defaultdict(return_0)
        for move in win_lose:
            quality[move[my_idx]] = quality[move[my_idx]] + self._parse_recur(win_lose[move], snake_id)
        return quality


    def update(self, gamestate, snake_id):
        # last number is the number of moves ahead to look
        win_lose = self._win_lose_recur(gamestate, 0, 1)
        move_quality = self._move_quality(win_lose, snake_id)
        print move_quality
        best_moves = []
        best_move_score = float('-inf')
        for m in move_quality:
            if move_quality[m] > best_move_score:
                best_moves = [m]
                best_move_score = move_quality[m]
            elif move_quality[m] == best_move_score:
                best_moves.append(m)
        if len(best_moves) == 1:
            return best_moves[0]
        # If there's a tie, let AI1 choose between the tied directions
        self.ai1.dirs = best_moves
        return self.ai1.update(gamestate, snake_id)


def play():
    ai1 = SnakeTronAI1()
    ai2 = SnakeTronAI2()
    snaketron.play_ai(ai1, ai2)

if __name__ == '__main__':
    print "play snaketron against ai"
    play()
