import copy
#   1 4 7
# 0 2 5 8 10
#   3 6 9
import os
import time

import psutil as psutil

EDGES = {
    0: {1, 2, 3},
    1: {0, 2, 4, 5},
    2: {0, 1, 3, 5},
    3: {0, 2, 5, 6},
    4: {1, 5, 7},
    5: {1, 2, 3, 4, 6, 7, 8, 9},
    6: {3, 5, 9},
    7: {4, 5, 8, 10},
    8: {5, 7, 9, 10},
    9: {5, 6, 8, 10},
    10: {7, 8, 9},
}

MAX_DEPTH = 6
HOUND1_CELL = 'c1'
HOUND2_CELL = 'c2'
HOUND3_CELL = 'c3'
EMPTY_CELL = '*'
HARE_CELL = 'i'
HOUNDS_STR = 'hounds'
HARE_STR = 'hare'

board_dict = {0: HOUND1_CELL,
              1: HOUND2_CELL,
              2: EMPTY_CELL,
              3: HOUND3_CELL,
              4: EMPTY_CELL,
              5: EMPTY_CELL,
              6: EMPTY_CELL,
              7: EMPTY_CELL,
              8: EMPTY_CELL,
              9: EMPTY_CELL,
              10: HARE_CELL}


class Game:
    MIN_PLAYER = HOUNDS_STR
    MAX_PLAYER = HARE_STR

    def __init__(self, board):
        self.board = board

    def get_hare_position(self):
        for key, val in self.board.items():
            if val == HARE_CELL:
                return key

    def get_hounds_position(self):
        h1 = -1
        h2 = -1
        h3 = -1
        for key, val in self.board.items():
            if val == HOUND1_CELL:
                h1 = key
            elif val == HOUND2_CELL:
                h2 = key
            elif val == HOUND3_CELL:
                h3 = key
        return (h1, h2, h3)

    def get_specific_hound_position(self, hound):
        for key, val in self.board.items():
            if val == hound:
                return key

    '''
    check if hare overcome one of the hounds
    '''
    def did_hare_overcome_hound(self, hare_pos, hound_pos):
        if hare_pos < hound_pos:
            return True
        if (hound_pos == 1 or hound_pos == 4 or hound_pos == 7) and (hare_pos == hound_pos + 1 or hare_pos == hound_pos + 2):
            return True
        if (hound_pos == 2 or hound_pos == 5 or hound_pos == 8) and hare_pos == hound_pos + 1:
            return True
        return False

    '''
    :return true if in 2 adjacent states hounds moved up, false otherwise
    '''
    def is_hounds_moved_up(self, state1, state2):
        board1 = state1.game.board
        board2 = state2.game.board
        for i in range(1, 4):
            hound_str = 'c' + str(i)
            if board1[0] == hound_str and \
                    (board2[1] == hound_str or board2[2] == hound_str or board2[3] == hound_str):
                return True
            if board1[1] == hound_str and (board2[4] == hound_str or board2[5] == hound_str):
                return True
            if board1[2] == hound_str and board2[5] == hound_str:
                return True
            if board1[3] == hound_str and (board2[5] == hound_str or board2[6] == hound_str):
                return True
            if board1[4] == hound_str and board2[7] == hound_str:
                return True
            if board1[6] == hound_str and board2[9] == hound_str:
                return True
            if board1[5] == hound_str and \
                    (board2[7] == hound_str or board2[8] == hound_str or board2[9] == hound_str):
                return True
            if board1[7] == hound_str and board2[10] == hound_str:
                return True
            if board1[8] == hound_str and board2[10] == hound_str:
                return True
            if board1[9] == hound_str and board2[10] == hound_str:
                return True
        return False

    '''
    :return true if game is tie, false otherwise
    '''
    def is_game_tie(self, state):
        states = state.get_parents()
        if len(states) < 10:
            return False
        for i in range(1, len(states)):
            state1 = states[i-1]
            state2 = states[i]
            if self.is_hounds_moved_up(state1, state2):
                return False
        # if hounds never moved up
        return True

    '''
    :return 'hounds' if hounds won
    :return 'hare' if hare won
    :return False if game is not over yet
    :return 'tie' if game is tie, i.e. hounds only moved down up
    '''
    def is_game_over(self, state):
        h1_pos, h2_pos, h3_pos = self.get_hounds_position()
        if h1_pos + h2_pos + h3_pos == 24 and self.get_hare_position() == 10:
            return 'hounds'
        hare_pos = self.get_hare_position()
        h1_pos, h2_pos, h3_pos = self.get_hounds_position()
        if self.did_hare_overcome_hound(hare_pos, hound_pos=h1_pos) and \
                self.did_hare_overcome_hound(hare_pos, hound_pos=h2_pos) and \
                self.did_hare_overcome_hound(hare_pos, hound_pos=h3_pos):
            return 'hare'
        if state is not None:
            if self.is_game_tie(state):
                return 'tie'
        return False

    '''
    check if player ('hounds' or 'hare') can move in a position based on their current position
    '''
    def can_move(self, player, current_pos, new_pos):
        if self.board[new_pos] != EMPTY_CELL:
            # if cell is already taken
            return False
        if current_pos == new_pos:
            return False
        if player == HOUNDS_STR:
            # hounds
            if current_pos - new_pos > 1 or current_pos == 10 or new_pos == 0:
                return False
            if new_pos in EDGES[current_pos]:
                return True
            else:
                return False
        else:
            # hare
            if new_pos in EDGES[current_pos]:
                return True
            else:
                return False

    '''
    :return a list of moves the player('hounds' or 'hare') can make
    if player is 'hounds' => return ([2], [2, 4, 5], [2, 5, 6]), where list[i] = list of moves for i-th hound
    if player is 'hare' => return [1,2] a list of possible moves of the hare  
    '''
    def generate_next_moves_position(self, player):
        if player == 'hare':
            moves = []
            pos = self.get_hare_position()
            possible_moves = EDGES[pos]
            for move_pos in possible_moves:
                if self.can_move('hare', current_pos=pos, new_pos=move_pos):
                    moves.append(move_pos)
            return moves
        else:
            moves_hound1 = []
            moves_hound2 = []
            moves_hound3 = []
            pos_hound1, pos_hound2, pos_hound3 = self.get_hounds_position()
            possible_moves_hound1 = EDGES[pos_hound1]
            possible_moves_hound2 = EDGES[pos_hound2]
            possible_moves_hound3 = EDGES[pos_hound3]
            for move_pos in possible_moves_hound1:
                if self.can_move('hounds', current_pos=pos_hound1, new_pos=move_pos):
                    moves_hound1.append(move_pos)
            for move_pos in possible_moves_hound2:
                if self.can_move('hounds', current_pos=pos_hound2, new_pos=move_pos):
                    moves_hound2.append(move_pos)
            for move_pos in possible_moves_hound3:
                if self.can_move('hounds', current_pos=pos_hound3, new_pos=move_pos):
                    moves_hound3.append(move_pos)
            return (moves_hound1, moves_hound2, moves_hound3)

    '''
    :return new board based on a move
    '''
    def generate_new_board(self, player_cell, curr_pos, new_pos):
        new_board = self.board.copy()
        new_board[curr_pos] = EMPTY_CELL
        new_board[new_pos] = player_cell
        return new_board

    '''
    player = 'hounds' or 'hare'
    :return a list of Game objects based on the player's next possible moves
    '''
    def generate_game_moves(self, player):
        moves = []
        if player == HARE_STR:
            hare_curr_pos = self.get_hare_position()
            for hare_new_pos in self.generate_next_moves_position(HARE_STR):
                moves.append(Game(board=self.generate_new_board(player_cell=HARE_CELL, curr_pos=hare_curr_pos, new_pos=hare_new_pos)))
            return moves
        else:
            h1_curr_pos, h2_curr_pos, h3_curr_pos = self.get_hounds_position()
            h1_new_moves, h2_new_moves, h3_new_moves = self.generate_next_moves_position(HOUNDS_STR)
            for h1_new_move in h1_new_moves:
                moves.append(Game(board=self.generate_new_board(player_cell=HOUND1_CELL, curr_pos=h1_curr_pos, new_pos=h1_new_move)))
            for h2_new_move in h2_new_moves:
                moves.append(Game(board=self.generate_new_board(player_cell=HOUND2_CELL, curr_pos=h2_curr_pos, new_pos=h2_new_move)))
            for h3_new_move in h3_new_moves:
                moves.append(Game(board=self.generate_new_board(player_cell=HOUND3_CELL, curr_pos=h3_curr_pos, new_pos=h3_new_move)))
            return moves

    '''
    player input moves
    '''
    def move_hounds(self, hound, new_pos):
        hound_pos = self.get_specific_hound_position(hound)
        # if not self.can_move(HOUNDS_STR, current_pos=hound_pos, new_pos=new_pos):
        #     return False
        new_board = self.generate_new_board(player_cell=hound, curr_pos=hound_pos, new_pos=new_pos)
        self.board = new_board
        # return True

    def move_hare(self, new_pos):
        hare_pos = self.get_hare_position()
        # if not self.can_move(HARE_STR, current_pos=hare_pos, new_pos=new_pos):
        #     return False
        new_board = self.generate_new_board(player_cell=HARE_CELL, curr_pos=hare_pos, new_pos=new_pos)
        self.board = new_board
        # return True

    '''
    aux for static_evaluation
    '''
    def get_hare_num_possible_moves(self):
        return len(self.generate_next_moves_position(HARE_STR))

    '''
    aux for static_evaluation
    '''
    def get_hounds_num_possible_moves(self):
        h1_new_moves, h2_new_moves, h3_new_moves = self.generate_next_moves_position(HOUNDS_STR)
        return len(h1_new_moves) + len(h2_new_moves) + len(h3_new_moves)

    '''
    MINIMAX static evaluation function
    '''
    def static_evaluation(self, depth):
        winner = self.is_game_over(state=None)
        if winner == HARE_STR:
            return 99 + depth
        elif winner == HOUNDS_STR:
            return -99 - depth
        else:
            return self.get_hare_num_possible_moves() - self.get_hounds_num_possible_moves()

    '''
    print board
    '''
    def print_board(self):
        print(' ' + self.board[1] + '-' + self.board[4] + '-' + self.board[7])
        print(" /|\\|/|\\")
        print(self.board[0] + '-' + self.board[2] + '-' + self.board[5] + '-' + self.board[8] + '-' + self.board[10])
        print(" \\|/|\\|/")
        print(' ' + self.board[3] + '-' + self.board[6] + '-' + self.board[9])

    def __str__(self):
        return self.print_board()


class State:
    def __init__(self, game, current_player, depth, parent=None, score=None):
        self.game = game
        self.current_player = current_player
        self.depth = depth
        self.score = score
        self.parent=parent
        self.possible_moves = []
        self.choosen_state = None

    def get_opponent_player(self):
        return Game.MAX_PLAYER if self.current_player == Game.MIN_PLAYER else Game.MIN_PLAYER

    def generate_moves(self):
        games = self.game.generate_game_moves(self.current_player)
        opponent_player = self.get_opponent_player()
        moves_states = [State(game=game, current_player=opponent_player, depth=self.depth-1, parent=self) for game in games]
        return moves_states

    '''
    :return a list of state's parents
    '''
    def get_parents(self):
        state = self
        l = [state]
        while state.parent is not None:
            l.append(state.parent)
            state = state.parent
        return l

    def __str__(self):
        return str(self.game)


def calc_mem_max():
    process = psutil.Process(os.getpid())
    mem_current = process.memory_info()[0]
    return mem_current


memory_used = 0


def minimax(state):
    global memory_used
    if state.depth == 0 or state.game.is_game_over(state=state):
        state.score = state.game.static_evaluation(state.depth)
        return state

    state.possible_moves = state.generate_moves()
    memory_used = calc_mem_max()

    moves_score = [minimax(move) for move in state.possible_moves]

    if state.current_player == Game.MAX_PLAYER:
        state.choosen_state = max(moves_score, key=lambda x: x.score) if moves_score else None
    else:
        state.choosen_state = min(moves_score, key=lambda x: x.score)
    state.score = state.choosen_state.score if state.choosen_state else 0
    return state


def alphabeta(alpha, beta, state):
    global memory_used
    if state.depth == 0 or state.game.is_game_over(state=state):
        state.score = state.game.static_evaluation(state.depth)
        return state

    if alpha > beta:
        return state

    state.possible_moves = state.generate_moves()
    memory_used = calc_mem_max()

    if state.current_player == Game.MAX_PLAYER:
        current_score = float('-inf')
        for move in state.possible_moves:
            new_state = alphabeta(alpha, beta, state=move)
            if current_score < new_state.score:
                state.choosen_state = new_state
                current_score = new_state.score
            alpha = max(alpha, current_score)
            if alpha >= beta:
                break
    else:
        current_score = float('inf')
        for move in state.possible_moves:
            new_state = alphabeta(alpha, beta, state=move)
            if current_score > new_state.score:
                state.choosen_state = new_state
                current_score = new_state.score
            beta = min(beta, current_score)
            if alpha >= beta:
                break
    state.score = state.choosen_state.score if state.choosen_state else 0
    return state


def print_if_final(current_state):
    final = current_state.game.is_game_over(state=current_state)
    if final != False:
        if final == HOUNDS_STR:
            print("Hounds a castigat")
        elif final == HARE_STR:
            print("Hare a castigat")
        else:
            print("EGAL")
        return True
    return False


def print_select_choose():
    print('  ' + '1' + '-' + '4' + '-' + '7')
    print(" /|\\|/|\\")
    print('0' + '-' + '2' + '-' + '5' + '-' + '8' + '-' + '10')
    print(" \\|/|\\|/")
    print('  ' + '3' + '-' + '6' + '-' + '9')


def is_int_helper(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def main():
    valid_responde = False
    player = ''
    while not valid_responde:
        algorithm_type = input("What algorithm would you like to use? (answer with 1 or 2)\n1.Minimax\n2.Alpha-beta\n")
        if algorithm_type in ['1', '2']:
            valid_responde = True
        else:
            print("You did not choose a valid response")
    valid_responde = False
    while not valid_responde:
        player = input("Choose your type of player. Choose between hounds and hare\n")
        if player in ['hounds', 'hare']:
            valid_responde = True
        else:
            print("You did not choose a valid response")

    # game = Game(board=board_dict)
    # print("Initial board")
    # game.print_board()

    current_state = State(game=Game(board=board_dict), current_player=HOUNDS_STR, depth=MAX_DEPTH)

    while True:
        if current_state.current_player == player:
            # player is moving
            print("============\nCurrent state:\n============")
            current_state.game.print_board()
            curr_pos = -1
            if player == HOUNDS_STR:
                valid_responde = False
                while not valid_responde:
                    hound_to_move = input("Select the hound you want to move. Write c1, c2 or c3\n")
                    if hound_to_move in  ['c1', 'c2', 'c3']:
                        valid_responde = True
                        curr_pos = current_state.game.get_specific_hound_position(hound_to_move)
                    else:
                        print("You did not choose a valid response")
            else:
                curr_pos = current_state.game.get_hare_position()
            print_select_choose()
            valid_responde = False
            while not valid_responde:
                new_pos = input("Pick a number for the new move\n")
                if is_int_helper(new_pos):
                    new_pos = int(new_pos)
                    if current_state.game.can_move(player=player, current_pos=curr_pos, new_pos=new_pos):
                        valid_responde = True
                else:
                    print("You cant move there, pick again")
            if player == HOUNDS_STR:
                current_state.game.move_hounds(hound=hound_to_move, new_pos=new_pos)
            else:
                current_state.game.move_hare(new_pos=new_pos)
            if print_if_final(current_state):
                break
            current_state.current_player = current_state.get_opponent_player()
        else:
            # AI is moving
            t1_computer = int(round(time.time() * 1000))
            if algorithm_type == '1':
                updated_state = minimax(current_state)
            else:
                updated_state = alphabeta(alpha=-500, beta=500, state=current_state)
            current_state.game = updated_state.choosen_state.game
            t2_computer = int(round(time.time() * 1000))
            print("Computer took {} miliseconds to think and used {} memory".format(t2_computer-t1_computer, memory_used))
            print("============\nAfter computer moved:\n============")
            current_state.game.print_board()
            print('='*20)

            if print_if_final(current_state):
                break
            current_state.current_player = current_state.get_opponent_player()


t1_game = int(round(time.time() * 1000))
main()
t2_game = int(round(time.time() * 1000))
print("Game finished in {} miliseconds".format(t2_game-t1_game))
