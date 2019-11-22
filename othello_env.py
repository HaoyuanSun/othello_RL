# Othello

import random
import sys
import numpy as np


# static methods
def is_on_board(x, y):
    # Returns True if the coordinates are located on the board.
    return 0 <= x <= 7 and 0 <= y <= 7


def is_on_corner(x, y):
    # Returns True if the position is in one of the four corners.
    return (x == 0 and y == 0) or (x == 7 and y == 0) or (x == 0 and y == 7) or (x == 7 and y == 7)


class Board:

    def __init__(self):
        self.board = []
        for _ in range(8):
            self.board.append([' ']*8)
        self.reset()

    def draw(self):

        h_line = '  +----+----+----+----+----+----+----+----+'

        print('     1    2    3    4    5    6    7    8')
        print(h_line)
        for y in range(8):
            print(y + 1, end=' ')
            for x in range(8):
                print('| %s' % (self.board[x][y]), end='  ')
            print('|')
            print(h_line)

    def reset(self):
        # Blanks out the board it is passed, except for the original starting position.
        for x in range(8):
            for y in range(8):
                self.board[x][y] = ' '

        # Starting pieces: X = black, O = white.
        self.board[3][3] = 'X'
        self.board[3][4] = 'O'
        self.board[4][3] = 'O'
        self.board[4][4] = 'X'

    def is_valid_move(self, tile, x_start, y_start):
        # Returns False if the player's move on space x_start, y_start is invalid.
        # If it is a valid move, returns a list of spaces that would become the player's if they made a move here.
        if self.board[x_start][y_start] != ' ' or not is_on_board(x_start, y_start):
            return False

        self.board[x_start][y_start] = tile  # temporarily set the tile on the board.

        if tile == 'X':
            other_tile = 'O'
        else:
            other_tile = 'X'

        tiles_to_flip = []
        for x_direction, y_direction in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
            x, y = x_start, y_start
            x += x_direction  # first step in the direction
            y += y_direction  # first step in the direction
            if is_on_board(x, y) and self.board[x][y] == other_tile:
                # There is a piece belonging to the other player next to our piece.
                x += x_direction
                y += y_direction
                if not is_on_board(x, y):
                    continue
                while self.board[x][y] == other_tile:
                    x += x_direction
                    y += y_direction
                    if not is_on_board(x, y):  # break out of while loop, then continue in for loop
                        break
                if not is_on_board(x, y):
                    continue
                if self.board[x][y] == tile:
                    # There are pieces to flip over. Go in the reverse direction until we reach the original space,
                    # noting all the tiles along the way.
                    while True:
                        x -= x_direction
                        y -= y_direction
                        if x == x_start and y == y_start:
                            break
                        tiles_to_flip.append([x, y])

        self.board[x_start][y_start] = ' '  # restore the empty space
        if len(tiles_to_flip) == 0:  # If no tiles were flipped, this is not a valid move.
            return False
        return tiles_to_flip
    
    def get_valid_moves(self, tile):
        # Returns a list of [x,y] lists of valid moves for the given player on the given board.
        valid_moves = []

        for x in range(8):
            for y in range(8):
                if self.is_valid_move(tile, x, y):
                    valid_moves.append([x, y])
        return valid_moves

    def get_score(self):
        # Determine the score by counting the tiles. Returns a dictionary with keys 'X' and 'O'.
        x_score = 0
        o_score = 0
        for x in range(8):
            for y in range(8):
                if self.board[x][y] == 'X':
                    x_score += 1
                elif self.board[x][y] == 'O':
                    o_score += 1
        return {'X': x_score, 'O': o_score}

    def make_move(self, tile, x_start, y_start):
        # Place the tile on the board at x_start, y_start, and flip any of the opponent's pieces.
        # Returns False if this is an invalid move, True if it is valid.
        tiles_to_flip = self.is_valid_move(tile, x_start, y_start)

        if not tiles_to_flip:
            return False

        self.board[x_start][y_start] = tile
        for x, y in tiles_to_flip:
            self.board[x][y] = tile
        return True

    def copy(self):
        # Make a duplicate of the board list and return the duplicate.
        dupe_board = Board()

        for x in range(8):
            for y in range(8):
                dupe_board.board[x][y] = self.board[x][y]

        return dupe_board

    def copy_with_valid_moves(self, tile):
        # ONLY TO BE USED WITH PLAYER INTERACTION. NOT FOR TRAINING
        # Returns a new board with . marking the valid moves the given player can make.
        dupe_board = self.copy()

        for x, y in dupe_board.get_valid_moves(tile):
            dupe_board.board[x][y] = '.'
        return dupe_board

    def list_to_array(self):
        state = np.zeros((8, 8))
        for i in range(8):
            for j in range(8):
                if self.board[j][i] == 'X':
                    state[i, j] = 1
                elif self.board[j][i] == 'O':
                    state[i, j] = -1
                else:
                    state[i, j] = 0
        return state

    def array_to_list(self, state):
        for i in range(8):
            for j in range(8):
                if state[i, j] == 1:
                    self.board[j][i] = 'X'
                elif state[i, j] == -1:
                    self.board[j][i] = 'O'
                else:
                    self.board[j][i] = ' '
        return self.board


class OthelloGame:

    def __init__(self, opponent='rand', interactive=True, show_steps=False):
        """
        :param opponent: specifies opponent
            'rand' --> chooses randomly among valid actions
            'heur' --> uses a symmetrical value table
            'bench' --> uses a value table trained via co-evolution
        :param interactive: specifies whether we are using program for RL
                or to play interactively
        :param show_steps: shows board at each step
        """
        self.board = Board()
        self.player_tile = 'X'
        self.computer_tile = 'O'
        self.player_score = 0
        self.computer_score = 0
        self.interactive = interactive
        self.stepper = show_steps
        self.show_hints = False

    def reset(self):
        self.board.reset()
        self.player_score = 0
        self.computer_score = 0

    def get_state(self):
        return self.board.list_to_array()

    def choose_player_tile(self):
        # Lets the player type which tile they want to be.
        # Returns a list with the player's tile as the first item, and the computer's tile as the second.
        tile = ''
        while not (tile == 'X' or tile == 'O'):
            print('Do you want to be X or O? X always moves first.')
            tile = input().upper()

        # the first element in the list is the player's tile, the second is the computer's tile.
        if tile == 'X':
            assigned_tiles = ['X', 'O']
        else:
            assigned_tiles = ['O', 'X']

        self.player_tile, self.computer_tile = assigned_tiles

    def get_player_action(self):
        # Let the player type in their move given a board state.
        # Returns the move as [x, y] (or returns the strings 'hints' or 'quit')
        valid_digits = '1 2 3 4 5 6 7 8'.split()
        while True:
            print('Enter your move, or type quit to end the game, or hints to turn off/on hints.')
            player_action = input().lower()
            if player_action == 'quit':
                return 'quit'
            elif player_action == 'hints':
                return 'hints'

            elif len(player_action) == 2 and player_action[0] in valid_digits and player_action[1] in valid_digits:
                x = int(player_action[0]) - 1
                y = int(player_action[1]) - 1
                if not self.board.is_valid_move(self.player_tile, x, y):
                    if self.interactive:
                        print('That is not a legal move.')
                    continue
                else:
                    break
            else:
                print('That is not a valid move. Type the x digit (1-8), then the y digit (1-8).')
                print('For example, 81 will be the top-right corner.')

        return [x, y]

    def get_computer_move(self):
        # TODO - add functionality for which opponent is active
        # Given a board and the computer's tile, determine where to
        # move and return that move as a [x, y] list.
        possible_moves = self.board.get_valid_moves(self.computer_tile)

        # randomize the order of the possible moves
        random.shuffle(possible_moves)

        # always go for a corner if available.
        for x, y in possible_moves:
            if is_on_corner(x, y):
                return [x, y]

        # Go through all the possible moves and remember the best scoring move
        best_score = -1
        best_move = []
        for x, y in possible_moves:
            dupe_board = self.board.copy()
            dupe_board.make_move(self.computer_tile, x, y)
            score = dupe_board.get_score()[self.computer_tile]
            if score > best_score:
                best_move = [x, y]
                best_score = score
        return best_move
    
    def show_points(self):
        # Prints out the current score.
        scores = self.board.get_score()
        print('You have %s points. The computer has %s points.' % (scores[self.player_tile], scores[self.computer_tile]))

    def start(self):
        if self.interactive:
            self.run_interactive()
        else:
            # Reset the board and game.
            self.board.reset()
            self.choose_player_tile()
            self.show_hints = False
            if self.player_tile == 'X':
                turn = 'player'
            else:
                turn = 'computer'

    def step(self, action):
        reward = 0
        terminal = False  # indicates terminal state
        next_board = self.board.copy()

        # generate next state
        if not self.board.is_valid_move(self.player_tile, action[0], action[1]):
            # TODO - go down the list and get the next best action
            return -10, self.board, terminal
        next_board.make_move(self.player_tile, action[0], action[1])

        # option to display visuals while learning how to train
        if self.stepper:
            next_board.draw()
            print(next_board.list_to_array())
            print('Reward on step: {0}'.format(reward))
        if not next_board.get_valid_moves(self.player_tile) and not next_board.get_valid_moves(self.computer_tile):
            terminal = True
            if self.player_score > self.computer_score:
                reward = 1
            elif self.player_score < self.computer_score:
                reward = -1
            else:
                reward = 0
        self.board = next_board.copy()
        return reward, self.board, terminal

    def run_interactive(self):
        print('Welcome to Othello!')
        while True:
            # Reset the board and game.
            self.board.reset()
            self.choose_player_tile()
            self.show_hints = True
            if self.player_tile == 'X':
                turn = 'player'
            else:
                turn = 'computer'

            while True:
                if turn == 'player':
                    # Player's turn.
                    if self.show_hints:
                        valid_moves_board = self.board.copy_with_valid_moves(self.player_tile)
                        valid_moves_board.draw()
                        print(self.board.list_to_array())
                    else:
                        self.board.draw()

                    self.show_points()
                    player_action = self.get_player_action()

                    if player_action == 'quit':
                        print('Thanks for playing!')
                        sys.exit()  # terminate the program
                    elif player_action == 'hints':
                        self.show_hints = not self.show_hints
                        continue
                    else:
                        self.board.make_move(self.player_tile, player_action[0], player_action[1])

                    if not self.board.get_valid_moves(self.computer_tile):
                        print('Your opponent has no legal move. It is your turn.')
                        if not self.board.get_valid_moves(self.player_tile):
                            print('You also have no legal move. The game is over.')
                            break
                        pass
                    else:
                        turn = 'computer'
                else:
                    # Computer's turn.
                    self.board.draw()
                    self.show_points()
                    input('Press Enter to see the computer\'s move.\n')
                    x, y = self.get_computer_move()
                    self.board.make_move(self.computer_tile, x, y)

                    if not self.board.get_valid_moves(self.player_tile):
                        print('You have no legal move. It is the computer\'s turn.')
                        if not self.board.get_valid_moves(self.computer_tile):
                            print('Your opponent also has no legal move. The game is over.')
                            break
                        pass
                    else:
                        turn = 'player'

            # Display the final score.
            self.board.draw()
            scores = self.board.get_score()
            self.player_score = scores[self.player_tile]
            self.computer_score = scores[self.computer_tile]
            margin = self.player_score - self.computer_score
            print('The player scored %s points. The computer scored %s points.' % (
                self.player_score, self.computer_score))
            if self.player_score > self.computer_score:
                print('You beat the computer by %s points! Congratulations!' % margin)
            elif self.player_score < self.computer_score:
                print('You lost. The computer beat you by %s points.' % margin)
            else:
                print('The game was a tie!')
